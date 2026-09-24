import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app as fastapi_app  # noqa: E402


async def app(scope, receive, send):
    """Punto de entrada ASGI de la Vercel Function.

    El frontend llama siempre a `/api/...` (mismo prefijo que recorta el proxy de
    Vite en desarrollo, ver frontend/vite.config.ts). Los routers de FastAPI no
    tienen ese prefijo (`/auth`, `/documentos`, ...), así que se recorta aquí
    antes de delegar, replicando en producción lo que hace `rewrite` en Vite.
    """
    if scope["type"] == "http" and scope["path"].startswith("/api"):
        scope = dict(scope)
        scope["path"] = scope["path"][len("/api"):] or "/"
    await fastapi_app(scope, receive, send)
