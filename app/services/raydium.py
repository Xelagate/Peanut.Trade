import asyncio
import logging

logger = logging.getLogger(__name__)

async def get_raydium_rate(base_currency: str, quote_currency: str) -> float:
    """
    Заглушка для Raydium. Поки не реалізовано отримання даних.
    Повертає 0.0.
    """
    logger.info(f"Raydium: не реалізовано для пари {base_currency}/{quote_currency}. Повертаємо 0.0")
    await asyncio.sleep(0)
    return 0.0
