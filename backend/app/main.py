from fastapi import FastAPI

from app.config import settings

app = FastAPI(title="SecureDocs API")


@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}