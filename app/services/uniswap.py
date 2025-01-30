from web3 import Web3
import json
import os

# Получаем абсолютный путь к файлу ABI
current_dir = os.path.dirname(os.path.abspath(__file__))  # Текущая директория (app/services)
abis_dir = os.path.join(current_dir, "..", "abis")  # Переход на уровень выше и вход в папку abis
ABI_PATH = os.path.join(abis_dir, "uniswap_v2_router_abi.json")  # Полный путь к файлу ABI

# Подключение к Infura
INFURA_URL = "https://mainnet.infura.io/v3/446dd1352b4042a4a9c905d676d8991b"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Адрес контракта Uniswap V2 Router
UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Загрузка ABI из файла
with open(ABI_PATH, "r") as f:
    UNISWAP_V2_ROUTER_ABI = json.load(f)

# Создание объекта контракта
uniswap_router = web3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=UNISWAP_V2_ROUTER_ABI)


async def get_uniswap_rate(base_currency: str, quote_currency: str) -> float:
    try:
        # Преобразуем адреса токенов в правильный формат
        base_address = web3.toChecksumAddress(base_currency)
        quote_address = web3.toChecksumAddress(quote_currency)

        # Путь для обмена (например, ETH -> USDT)
        path = [base_address, quote_address]

        # Количество базового токена (например, 1 ETH)
        amount_in = web3.toWei(1, 'ether')

        # Получаем ожидаемое количество quote токена
        amounts = uniswap_router.functions.getAmountsOut(amount_in, path).call()
        amount_out = amounts[-1]  # Последний элемент массива — это количество quote токена

        # Преобразуем количество quote токена в читаемый формат
        rate = web3.fromWei(amount_out, 'ether')
        return float(rate)
    except Exception as e:
        print(f"Error fetching Uniswap rate: {e}")
        return 0.0
