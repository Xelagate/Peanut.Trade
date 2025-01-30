from web3 import Web3
import json

# Подключение к Infura
INFURA_URL = "https://mainnet.infura.io/v3/446dd1352b4042a4a9c905d676d8991b"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Адрес и ABI контракта Uniswap V2 Router
UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
with open("uniswap_v2_router_abi.json", "r") as f:
    UNISWAP_V2_ROUTER_ABI = json.load(f)

# Создание объекта контракта
uniswap_router = web3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=UNISWAP_V2_ROUTER_ABI)

async def get_uniswap_rate(base_currency: str, quote_currency: str) -> float:
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