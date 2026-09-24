from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings


@dataclass
class Sujeto:
    id: int | None
    correo: str
    rol: str
    departamento: str | None
    nivel_seguridad: int
    pais: str
    tipo_contrato: str
    estado: str


@dataclass
class Recurso:
    id: int | None
    departamento: str | None
    nivel_confidencialidad: int | None
    estado: str | None
    pais: str | None
    propietario_id: int | None


@dataclass
class Entorno:
    hora_local: str       # "HH:MM" en zona TZ_APP
    fecha_local: str
    ubicacion: str         # código de país, ej. "PE"
    dispositivo: str       # "CORPORATIVO" | "PERSONAL"
    ip: str | None


@dataclass
class Contexto:
    sujeto: Sujeto
    recurso: Recurso | None
    accion: str
    entorno: Entorno


def construir_entorno(request) -> Entorno:
    ahora = datetime.now(ZoneInfo(settings.tz_app))

    if settings.demo_mode:
        # En DEMO_MODE, el simulador del frontend envía estos headers (Paso 9)
        ubicacion = request.headers.get("X-Sim-Ubicacion", "PE")
        dispositivo = request.headers.get("X-Sim-Dispositivo", "CORPORATIVO")
    else:
        ubicacion = request.headers.get("x-vercel-ip-country", "PE")
        dispositivo = "PERSONAL"  # sin MDM real, nunca se asume corporativo en producción

    return Entorno(
        hora_local=ahora.strftime("%H:%M"),
        fecha_local=ahora.strftime("%Y-%m-%d"),
        ubicacion=ubicacion,
        dispositivo=dispositivo,
        ip=request.headers.get("x-real-ip") or request.client.host,
    )