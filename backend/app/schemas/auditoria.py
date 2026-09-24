from datetime import datetime

from pydantic import BaseModel


class AuditoriaOut(BaseModel):
    id: int
    usuario_correo: str
    recurso: str
    accion: str
    fecha: datetime
    resultado: str
    etapa: str | None
    motivo: str | None
    politica_fallida: str | None

    class Config:
        from_attributes = True