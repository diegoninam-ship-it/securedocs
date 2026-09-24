from fastapi import FastAPI

from app.config import settings
from app.routers import auditoria, auth, catalogos, documentos, usuarios

app = FastAPI(title="SecureDocs API")

app.include_router(auth.router)
app.include_router(documentos.router)
app.include_router(usuarios.router)
app.include_router(auditoria.router)
app.include_router(catalogos.router)

@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}