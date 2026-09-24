from datetime import datetime

from pydantic import BaseModel


class DocumentoCreate(BaseModel):
    titulo: str
    descripcion: str | None = None
    nivel_confidencialidad: int = 1


class DocumentoUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    nivel_confidencialidad: int | None = None


class DocumentoOut(BaseModel):
    id: int
    titulo: str
    descripcion: str | None
    departamento: str
    nivel_confidencialidad: int
    estado: str
    pais: str
    propietario_id: int
    fecha_creacion: datetime
    aprobado_por: int | None
    fecha_aprobacion: datetime | None

    class Config:
        from_attributes = True