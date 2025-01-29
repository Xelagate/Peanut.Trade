import requests

async def get_kucoin_rate(base_currency: str, quote_currency: str) -> float:
    symbol = f"{base_currency}-{quote_currency}"
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data['data']['price'])