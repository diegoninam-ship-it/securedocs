from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(String(500), nullable=True)

    propietario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)

    nivel_confidencialidad = Column(Integer, nullable=False, default=1)
    estado = Column(String(15), nullable=False, default="PENDIENTE")
    pais = Column(String(2), nullable=False, default="PE")

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    aprobado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_aprobacion = Column(DateTime(timezone=True), nullable=True)

    propietario = relationship("Usuario", foreign_keys=[propietario_id])
    aprobador = relationship("Usuario", foreign_keys=[aprobado_por])
    departamento = relationship("Departamento")