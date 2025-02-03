import os

# Дані для підключення до Infura (бере з змінних середовища, щоб не зберігати ключі у коді)
INFURA_WS_URL = os.getenv("INFURA_WS_URL", "wss://mainnet.infura.io/ws/v3/ВАШ_PROJECT_ID")
HTTP_PROVIDER_URL = os.getenv("HTTP_PROVIDER_URL", "https://mainnet.infura.io/v3/ВАШ_PROJECT_ID")

# Конфігурація пулів Uniswap V3 (адреси пулів можна змінювати через змінні середовища)
POOL_CONFIG = {
    "WETH/USDC": {
        "pool_address": os.getenv("POOL_WETH_USDC", "0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36"),  # Uniswap V3 WETH/USDC, комісія 0.3%
        "tokens": ("WETH", "USDC")
    },
    "WBTC/ETH": {
        "pool_address": os.getenv("POOL_WBTC_ETH", "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD"),  # Uniswap V3 WBTC/ETH, комісія 0.3%
        "tokens": ("WBTC", "WETH")
    }
}

# Шлях до файлу ABI пулу Uniswap V3 (можна вказати у змінних середовища)
ABI_PATH = os.getenv("ABI_PATH", "abis/uniswap_v3_pool.json")
