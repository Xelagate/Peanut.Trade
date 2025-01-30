from fastapi import APIRouter
from app.services.binance import get_binance_rate
from app.services.kucoin import get_kucoin_rate
from app.services.uniswap import get_uniswap_rate
from app.services.raydium import get_raydium_rate

router = APIRouter()

@router.get("/")
async def get_rates(baseCurrency: str, quoteCurrency: str):
    rates = [
        {"exchangeName": "Binance", "rate": await get_binance_rate(baseCurrency, quoteCurrency)},
        {"exchangeName": "KuCoin", "rate": await get_kucoin_rate(baseCurrency, quoteCurrency)},
        {"exchangeName": "Uniswap", "rate": await get_uniswap_rate(baseCurrency, quoteCurrency)},
        {"exchangeName": "Raydium", "rate": await get_raydium_rate(baseCurrency, quoteCurrency)},
    ]
    return rates