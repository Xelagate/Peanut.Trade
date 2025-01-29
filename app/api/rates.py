from fastapi import APIRouter
from app.services.binance import get_binance_rate
from app.services.kucoin import get_kucoin_rate
from app.services.uniswap import get_uniswap_rate
from app.services.raydium import get_raydium_rate

router = APIRouter()

@router.get("/", tags=["Rates"])
async def get_rates(baseCurrency: str, quoteCurrency: str):
    rates = {
        "Binance": await get_binance_rate(baseCurrency, quoteCurrency),
        "KuCoin": await get_kucoin_rate(baseCurrency, quoteCurrency),
        "Uniswap": await get_uniswap_rate(baseCurrency, quoteCurrency),
        "Raydium": await get_raydium_rate(baseCurrency, quoteCurrency),
    }

    # Удаляем биржи, которые вернули None
    rates = [{"exchangeName": name, "rate": rate} for name, rate in rates.items() if rate is not None]

    return rates
