from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    usuario_correo = Column(String(120), nullable=False)

    recurso = Column(String(100), nullable=False)
    accion = Column(String(30), nullable=False)

    fecha = Column(DateTime(timezone=True), server_default=func.now())

    resultado = Column(String(15), nullable=False)  # PERMITIDO / DENEGADO
    etapa = Column(String(10), nullable=True)         # AUTH / RBAC / ABAC
    motivo = Column(String(500), nullable=True)
    politica_fallida = Column(String(50), nullable=True)  # "P1,P2" si son varias

    contexto = Column(JSONB, nullable=True)

    usuario = relationship("Usuario")