import websockets
import json

async def get_uniswap_rate(base_currency: str, quote_currency: str) -> float:
    async with websockets.connect("wss://uniswap.socket") as websocket:
        await websocket.send(json.dumps({"action": "subscribe", "pair": f"{base_currency}/{quote_currency}"}))
        response = await websocket.recv()
        data = json.loads(response)
        return float(data['price'])