# config.py
# Файл налаштувань – тут зберігаються всі індивідуальні параметри, які користувач може змінювати.

# Дані для підключення до Infura (вкажіть свій Project ID)
INFURA_WS_URL = "wss://mainnet.infura.io/ws/v3/ВАШ_PROJECT_ID"
HTTP_PROVIDER_URL = "https://mainnet.infura.io/v3/ВАШ_PROJECT_ID"

# Конфігурація пулів Uniswap V3
# Перший пул – фактично WETH/USDC (адреса: 0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36)
# Другий пул – WBTC/ETH (оскільки ETH нормалізується до WETH)
POOL_CONFIG = {
    "WETH/USDC": {
        "pool_address": "0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36",  # Uniswap V3 WETH/USDC, комісія 0.3%
        "tokens": ("WETH", "USDC")
    },
    "WBTC/ETH": {
        "pool_address": "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD",  # Uniswap V3 WBTC/ETH, комісія 0.3%
        "tokens": ("WBTC", "WETH")
    }
}

# Шлях до файлу ABI пулу Uniswap V3 (вкажіть коректний шлях відносно кореня проекту)
ABI_PATH = "abis/uniswap_v3_pool.json"
