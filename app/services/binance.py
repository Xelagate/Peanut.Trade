import httpx

async def get_binance_rate(base_currency: str, quote_currency: str) -> float:
    """
    Отримує обмінний курс base_currency → quote_currency з Binance.
    Символ формується як <BASE><QUOTE> у верхньому регістрі (наприклад, BTCUSDT).
    """
    symbol = f"{base_currency}{quote_currency}".upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            # Перевіряємо HTTP статус
            if response.status_code != 200:
                print(f"❌ Binance: HTTP {response.status_code} для символу {symbol}: {response.text}")
                return 0.0
            
            data = response.json()
            
            if "price" in data:
                return float(data["price"])
            
            print(f"❌ Binance: Пара {symbol} не знайдена. Отримані дані: {data}")
            return 0.0

    except Exception as e:
        print(f"Помилка Binance: {e}")
        return 0.0
