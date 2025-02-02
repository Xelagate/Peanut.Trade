from fastapi import APIRouter
from app.services.binance import get_binance_rate
from app.services.kucoin import get_kucoin_rate
from app.services.uniswap import get_uniswap_rate
from app.services.raydium import get_raydium_rate

router = APIRouter()


@router.get("/")
async def get_rates(baseCurrency: str, quoteCurrency: str):
    """
    Функція 'get_rates' приймає:
      - baseCurrency: базову валюту,
      - quoteCurrency: валюту котирування.

    Функція повертає список з курсами (ціною 1 baseCurrency в quoteCurrency) для кожної біржі.
    """
    rates = []

    # Отримуємо курси з усіх бірж
    binance_rate = await get_binance_rate(baseCurrency, quoteCurrency)
    kucoin_rate = await get_kucoin_rate(baseCurrency, quoteCurrency)
    uniswap_rate = await get_uniswap_rate(baseCurrency, quoteCurrency)
    raydium_rate = await get_raydium_rate(baseCurrency, quoteCurrency)

    # Формуємо список результатів з округленням до 2 знаків
    rates.append({"exchangeName": "binance", "rate": round(binance_rate, 2)})
    rates.append({"exchangeName": "kucoin", "rate": round(kucoin_rate, 2)})
    rates.append({"exchangeName": "uniswap", "rate": round(uniswap_rate, 2)})
    rates.append({"exchangeName": "raydium", "rate": round(raydium_rate, 2)})

    return rates
