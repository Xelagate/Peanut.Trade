import os
import json


# Заглушка для получения курса на Raydium
# Представь, что это вместо настоящей функции
# пока вы не реализуете логику доступа к Solana/Raydium
async def get_raydium_rate(base_currency: str, quote_currency: str) -> float:
    """
    Это просто заглушка, которая всегда
    возвращает одно значение (1.2345).

    По-настоящему здесь должен быть код, который:
    1. Подключается к Solana.
    2. Находит пул Raydium.
    3. Вычисляет цену (rate) между токенами base_currency и quote_currency.
    """

    print("Вызвана заглушка get_raydium_rate — возвращаем фиксированное число.")
    return 1.2345
