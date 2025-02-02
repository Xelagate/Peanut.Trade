# main.py
# Основний файл для запуску API-сервісу за допомогою FastAPI

from fastapi import FastAPI
from app.api import estimate, rates  # імпортуємо модулі ендпоінтів

app = FastAPI()

# Підключаємо роутери для ендпоінтів
app.include_router(estimate.router, prefix="/estimate")
app.include_router(rates.router, prefix="/rates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
