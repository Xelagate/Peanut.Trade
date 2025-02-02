import json
import asyncio
import logging
import websockets
from pathlib import Path
from web3 import Web3
import httpx
from config import INFURA_WS_URL, HTTP_PROVIDER_URL, POOL_CONFIG, ABI_PATH

# Налаштовуємо логування (залишаємо лише повідомлення про помилки)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Підключення до Ethereum через Infura
w3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER_URL))

# Завантаження ABI пулу Uniswap V3
base_dir = Path(__file__).resolve().parent.parent.parent  # переходимо до кореня проекту
abi_file = base_dir / ABI_PATH
with open(abi_file, "r") as f:
    abi_data = json.load(f)
    # Якщо завантажені дані є списком, використовуємо їх без змін
    if isinstance(abi_data, list):
        UNISWAP_V3_POOL_ABI = abi_data
    # Якщо дані є словником і містять ключ "abi", беремо його значення
    elif isinstance(abi_data, dict) and "abi" in abi_data:
        UNISWAP_V3_POOL_ABI = abi_data["abi"]
    # Інакше обгортаємо дані в список
    else:
        UNISWAP_V3_POOL_ABI = [abi_data]

# Глобальний словник для збереження отриманих курсів з пулів (через WebSocket)
pool_prices = {}


def get_token_decimals(token_address):
    """
    Функція отримання кількості десяткових знаків для заданого токена.
    Якщо виникає помилка, повертає значення за замовчуванням 18.
    """
    try:
        token_contract = w3.eth.contract(address=token_address, abi=[{
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }])
        return token_contract.functions.decimals().call()
    except Exception as e:
        logger.error(f"Помилка отримання десяткових знаків для токена {token_address}: {e}")
        return 18


def init_pools():
    """
    Ініціалізація пулів: завантаження контракту за адресою, отримання адрес токенів та їх десяткових знаків.
    """
    for pool_name, config in POOL_CONFIG.items():
        # Перетворення адреси пулу у формат checksum
        pool_address = Web3.to_checksum_address(config["pool_address"])
        contract = w3.eth.contract(address=pool_address, abi=UNISWAP_V3_POOL_ABI)
        config["contract"] = contract
        try:
            token0 = contract.functions.token0().call()
            token1 = contract.functions.token1().call()
        except Exception as e:
            logger.error(f"Помилка отримання токенів для пулу {pool_name}: {e}")
            token0, token1 = None, None
        config["token0_address"] = token0
        config["token1_address"] = token1
        config["token0_decimals"] = get_token_decimals(token0)
        config["token1_decimals"] = get_token_decimals(token1)


init_pools()


async def listen_pool_swaps(pool_name: str, config: dict):
    """
    Підписка на події Swap для заданого пулу Uniswap V3 та оновлення словника pool_prices.
    """
    pool_address = config["pool_address"]
    ws_url = INFURA_WS_URL
    # Сигнатура події Swap: Swap(address,address,int256,int256,uint160,uint128,int24)
    event_signature = "0x" + Web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)").hex()
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                subscribe_msg = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": ["logs", {"address": pool_address, "topics": [event_signature]}]
                })
                await ws.send(subscribe_msg)
                await ws.recv()  # отримуємо підтвердження підписки
                while True:
                    event = await ws.recv()
                    await handle_swap_event(pool_name, config, event)
        except Exception as e:
            logger.error(f"Помилка прослуховування пулу {pool_name}: {e}")
            await asyncio.sleep(5)


async def handle_swap_event(pool_name: str, config: dict, event: str):
    """
    Обробка події Swap:
      - Витягуємо sqrtPriceX96 (байти з 128 по 192 із даних події)
      - Обчислюємо базову ціну за формулою: (sqrtPriceX96² / 2**192)
      - Коригуємо значення з урахуванням десяткових знаків токенів
      - Зберігаємо отримане значення у словнику pool_prices
    """
    try:
        data = json.loads(event)
        if "params" in data and "result" in data["params"]:
            result = data["params"]["result"]
            if "data" not in result:
                return
            data_hex = result["data"][2:]
            if len(data_hex) < 320:
                return
            # Отримання sqrtPriceX96 (байти з 128 по 192)
            sqrtPrice_hex = data_hex[128:192]
            sqrtPriceX96 = int(sqrtPrice_hex, 16)
            price_base = (sqrtPriceX96 ** 2) / (2 ** 192)
            decimals0 = config["token0_decimals"]
            decimals1 = config["token1_decimals"]
            adjusted_price = price_base * (10 ** decimals0) / (10 ** decimals1)
            pool_prices[pool_name] = adjusted_price
    except Exception as e:
        logger.error(f"Помилка обробки події для пулу {pool_name}: {e}")


async def start_listeners():
    """
    Запуск прослуховування подій для всіх пулів.
    """
    tasks = []
    for pool_name, config in POOL_CONFIG.items():
        tasks.append(asyncio.create_task(listen_pool_swaps(pool_name, config)))
    await asyncio.gather(*tasks)


# Запуск прослуховування подій у фоновому режимі
loop = asyncio.get_event_loop()
loop.create_task(start_listeners())


async def get_uniswap_rate(input_currency: str, output_currency: str) -> float:
    """
    Функція повертає курс для пари input_currency/output_currency, використовуючи дані з Uniswap V3.

    Нормалізація: якщо користувач вводить ETH або BTC, вони перетворюються на WETH або WBTC відповідно.
    Якщо запитується SOL – повертається 0.0.

    Логіка:
      1. Якщо існує прямий пул – повертається його значення (при потребі з конверсією USDC -> USDT).
      2. Якщо прямого пулу немає – пробується двоступенева конверсія через WETH.
    Результат округлюється до 2 знаків.
    """
    base = input_currency.upper()
    quote = output_currency.upper()
    if base == "ETH":
        base = "WETH"
    if quote == "ETH":
        quote = "WETH"
    if base == "BTC":
        base = "WBTC"
    if quote == "BTC":
        quote = "WBTC"
    if base == "SOL" or quote == "SOL":
        return 0.0
    if base == quote:
        return 1.0

    direct_pool = None
    direct_config = None
    # Пошук прямого пулу (наші пули: "WETH/USDC" та "WBTC/ETH")
    # Якщо користувач запитує, наприклад, ETH/USDT, використовується пул "WETH/USDC" із конверсією USDC -> USDT.
    for pool_name, config in POOL_CONFIG.items():
        tokens = config["tokens"]
        if tokens == (base, quote) or tokens == (quote, base):
            direct_pool = pool_name
            direct_config = config
            break
        if base == "WETH" and quote == "USDT" and tokens in [("WETH", "USDC"), ("USDC", "WETH")]:
            direct_pool = pool_name
            direct_config = config
            break

    if direct_pool:
        price = pool_prices.get(direct_pool, 0.0)
        if price == 0.0:
            try:
                slot0 = direct_config["contract"].functions.slot0().call()
                sqrtPriceX96 = slot0[0]
                price_base = (sqrtPriceX96 ** 2) / (2 ** 192)
                decimals0 = direct_config["token0_decimals"]
                decimals1 = direct_config["token1_decimals"]
                price = price_base * (10 ** decimals0) / (10 ** decimals1)
            except Exception as e:
                logger.error(f"Помилка читання slot0 для пулу {direct_pool}: {e}")
                return 0.0
        tokens = direct_config["tokens"]
        if tokens == (base, quote):
            result = round(price, 2)
        elif tokens == (quote, base):
            result = round(1 / price, 2)
        elif base == "WETH" and quote == "USDT" and tokens in [("WETH", "USDC"), ("USDC", "WETH")]:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("https://api.binance.com/api/v3/ticker/price",
                                            params={"symbol": "USDCUSDT"})
                    usdc_to_usdt = float(resp.json()["price"])
            except Exception as e:
                logger.error(f"Помилка отримання курсу USDC->USDT: {e}")
                usdc_to_usdt = 1.0
            if tokens == ("WETH", "USDC"):
                result = round(price * usdc_to_usdt, 2)
            else:
                result = round((1 / price) * usdc_to_usdt, 2)
        else:
            result = 0.0
        return result

    if base != "WETH" and quote != "WETH":
        rate1 = await get_uniswap_rate(base, "WETH")
        rate2 = await get_uniswap_rate("WETH", quote)
        if rate1 > 0 and rate2 > 0:
            return round(rate1 * rate2, 2)
    return 0.0


# Для тестування (якщо запускаємо цей файл окремо)
if __name__ == "__main__":
    async def test():
        await asyncio.sleep(15)  # Чекаємо, щоб накопичились дані з подій або спрацював fallback до slot0
        rate1 = await get_uniswap_rate("ETH", "USDT")
        print("ETH/USDT:", rate1)
        rate2 = await get_uniswap_rate("BTC", "USDT")
        print("BTC/USDT:", rate2)


    loop.run_until_complete(test())
