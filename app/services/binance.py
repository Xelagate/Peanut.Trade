import httpx

async def get_binance_rate(base_currency: str, quote_currency: str) -> float:
    """
    Получает обменный курс `base_currency` → `quote_currency` с Binance.
    """
    symbol = f"{base_currency}{quote_currency}".upper()
    url = f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if "price" in data:
                return float(data["price"])

            print(f"❌ Binance: Пара {symbol} не найдена")
            return 0.0  # Возвращаем 0, если пара не найдена

    except Exception as e:
        print(f"Ошибка Binance: {e}")
        return 0.0  # В случае ошибки возвращаем 0
