import requests

async def get_binance_rate(base_currency: str, quote_currency: str) -> float:
    symbol = f"{base_currency}{quote_currency}"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data['price'])