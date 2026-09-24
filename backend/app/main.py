from fastapi import FastAPI

from app.config import settings
from app.routers import auth

app = FastAPI(title="SecureDocs API")

app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}