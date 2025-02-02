import httpx

async def get_kucoin_rate(base_currency: str, quote_currency: str) -> float:
    """
    Получает обменный курс `base_currency` → `quote_currency` с KuCoin.
    """
    symbol = f"{base_currency.upper()}-{quote_currency.upper()}"
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

            # Проверяем, есть ли ошибки в ответе
            if "code" in data and data["code"] != "200000":
                print(f"❌ KuCoin API вернул ошибку: {data}")
                return 0.0

            # Проверяем, есть ли данные в ответе
            if "data" not in data or data["data"] is None:
                print(f"❌ KuCoin: Пара {symbol} не найдена. Ответ: {data}")
                return 0.0

            if "price" in data["data"]:
                return float(data["data"]["price"])

            print(f"❌ KuCoin: Пара {symbol} не найдена в данных {data}")
            return 0.0

    except Exception as e:
        print(f"Ошибка KuCoin: {e}")
        return 0.0  # В случае ошибки возвращаем 0
