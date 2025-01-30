from fastapi import FastAPI
from app.api.estimate import router as estimate_router
from app.api.rates import router as rates_router

app = FastAPI()

# Підключаємо роутери
app.include_router(estimate_router, prefix="/estimate")
app.include_router(rates_router, prefix="/rates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)