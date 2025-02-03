import httpx

async def get_binance_rate(base_currency: str, quote_currency: str) -> float:
    symbol = f"{base_currency}{quote_currency}".upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()

            if "price" in data:
                return float(data["price"])

            print(f"❌ Binance: Пара {symbol} не найдена")
            return 0.0  

    except Exception as e:
        print(f"Ошибка Binance: {e}")
        return 0.0  
