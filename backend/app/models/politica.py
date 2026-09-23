from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db import Base


class Politica(Base):
    __tablename__ = "politicas"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(10), unique=True, nullable=False)  # P1, P2, ... P9
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(300), nullable=True)
    activa = Column(Boolean, nullable=False, default=True)

    roles_aplicables = Column(JSONB, nullable=True)  # null = todos los roles
    roles_exentos = Column(JSONB, nullable=True)      # [] = ninguno exento
    operaciones = Column(JSONB, nullable=False)        # ["CONSULTAR", "MODIFICAR", ...]
    parametros = Column(JSONB, nullable=True)          # {"hora_inicio": "08:00", ...}