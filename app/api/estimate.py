from fastapi import APIRouter, HTTPException
from app.services.binance import get_binance_rate
from app.services.kucoin import get_kucoin_rate
from app.services.uniswap import get_uniswap_rate
from app.services.raydium import get_raydium_rate

router = APIRouter()


@router.post("/")
async def estimate(inputAmount: float, inputCurrency: str, outputCurrency: str):
    """
    Функція 'estimate' приймає:
      - inputAmount: кількість токенів для обміну,
      - inputCurrency: валюта, яку віддаємо,
      - outputCurrency: валюта, яку хочемо отримати.

    Функція запитує курси з усіх підтримуваних бірж (Binance, KuCoin, Uniswap, Raydium),
    фільтрує ті біржі, де курс більше 0, та обирає біржу з найбільш вигідним курсом (максимальним).
    Потім розраховує кількість вихідних токенів і повертає результат.
    """
    # Отримуємо курси з усіх бірж
    rates = {
        "binance": await get_binance_rate(inputCurrency, outputCurrency),
        "kucoin": await get_kucoin_rate(inputCurrency, outputCurrency),
        "uniswap": await get_uniswap_rate(inputCurrency, outputCurrency),
        "raydium": await get_raydium_rate(inputCurrency, outputCurrency),
    }

    # Фільтруємо біржі, які повернули коректний курс (більше 0)
    valid_rates = {exchange: rate for exchange, rate in rates.items() if rate > 0}

    # Якщо немає жодного валідного курсу, повертаємо помилку
    if not valid_rates:
        raise HTTPException(
            status_code=400,
            detail=f"❌ Немає доступних курсів для {inputCurrency}/{outputCurrency}"
        )

    # Обираємо біржу з найвигіднішим курсом (максимальним)
    best_exchange = max(valid_rates, key=valid_rates.get)
    output_amount = inputAmount * valid_rates[best_exchange]

    return {
        "exchangeName": best_exchange,
        "outputAmount": round(output_amount, 2)
    }
