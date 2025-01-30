from fastapi import APIRouter, HTTPException
from app.services.binance import get_binance_rate
from app.services.kucoin import get_kucoin_rate
from app.services.uniswap import get_uniswap_rate
from app.services.raydium import get_raydium_rate

router = APIRouter()

@router.post("/")
async def estimate(inputAmount: float, inputCurrency: str, outputCurrency: str):
    rates = {
        "Binance": await get_binance_rate(inputCurrency, outputCurrency),
        "KuCoin": await get_kucoin_rate(inputCurrency, outputCurrency),
        "Uniswap": await get_uniswap_rate(inputCurrency, outputCurrency),
        "Raydium": await get_raydium_rate(inputCurrency, outputCurrency),
    }

    best_exchange = max(rates, key=rates.get)
    output_amount = inputAmount * rates[best_exchange]

    return {
        "exchangeName": best_exchange,
        "outputAmount": output_amount
    }