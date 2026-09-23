from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True)

    nivel_seguridad = Column(Integer, nullable=False, default=1)
    pais = Column(String(2), nullable=False, default="PE")
    tipo_contrato = Column(String(10), nullable=False, default="INTERNO")
    estado = Column(String(15), nullable=False, default="ACTIVO")
    token_version = Column(Integer, nullable=False, default=0)

    rol = relationship("Rol")
    departamento = relationship("Departamento")