import os
import json
import logging
from web3 import AsyncWeb3

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Адреса токенов
TOKEN_ADDRESSES = {
    "ETH": "0xC02aaa39b223FE8D0A0e5C4F27ead9083C756Cc2",  # WETH
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "BTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # wBTC
    "SOL": "0xD31a59c85aE9D8edEFeC411D448f90841571b89c",  # wrapped SOL (Wormhole)
}

# Подключение к Infura
INFURA_URL = "wss://mainnet.infura.io/ws/v3/446dd1352b4042a4a9c905d676d8991b"
web3 = AsyncWeb3(AsyncWeb3.WebSocketProvider(INFURA_URL))

# Загрузка ABI
current_dir = os.path.dirname(os.path.abspath(__file__))
abis_dir = os.path.join(current_dir, "..", "..", "abis")

# Uniswap V2 Router
UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
with open(os.path.join(abis_dir, "uniswap_v2_router_abi.json"), "r", encoding="utf-8") as f:
    UNISWAP_V2_ROUTER_ABI = json.load(f)
uniswap_v2_router = web3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=UNISWAP_V2_ROUTER_ABI)

async def get_uniswap_rate(base_currency: str, quote_currency: str) -> float:
    """
    Получаем курс через Uniswap V2.
    """
    try:
        # Проверка подключения к WebSocket
        if not web3.is_connected():
            logger.error("WebSocket connection failed")
            return 0.0

        # Приводим валюты к верхнему регистру и убираем пробелы
        bc = base_currency.upper().strip()
        qc = quote_currency.upper().strip()

        # Проверяем, известны ли токены
        if bc not in TOKEN_ADDRESSES or qc not in TOKEN_ADDRESSES:
            logger.warning(f"Unknown token: {bc} or {qc}")
            return 0.0

        # Получаем адреса токенов
        base_address = web3.to_checksum_address(TOKEN_ADDRESSES[bc])
        quote_address = web3.to_checksum_address(TOKEN_ADDRESSES[qc])

        # Формируем путь для обмена
        path = [base_address, quote_address]

        # Указываем количество входных токенов (1 токен в wei)
        amount_in = web3.to_wei(1, 'ether')

        # Получаем количество выходных токенов
        amounts = await uniswap_v2_router.functions.getAmountsOut(amount_in, path).call()
        amount_out_wei = amounts[-1]

        # Конвертируем результат в ether
        raw_rate = web3.from_wei(amount_out_wei, 'ether')

        return float(raw_rate)

    except Exception as e:
        logger.error(f"[Uniswap] Error: {e}")
        return 0.0