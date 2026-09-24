from sqlalchemy.orm import Session

from app.authz.context import Contexto
from app.models import Auditoria


def registrar(
    db: Session,
    ctx: Contexto,
    recurso_nombre: str,
    resultado: str,
    etapa: str | None = None,
    motivo: str | None = None,
    politica_fallida: str | None = None,
):
    entrada = Auditoria(
        usuario_id=ctx.sujeto.id,
        usuario_correo=ctx.sujeto.correo,
        recurso=recurso_nombre,
        accion=ctx.accion,
        resultado=resultado,
        etapa=etapa,
        motivo=motivo,
        politica_fallida=politica_fallida,
        contexto={
            "ip": ctx.entorno.ip,
            "ubicacion": ctx.entorno.ubicacion,
            "dispositivo": ctx.entorno.dispositivo,
            "hora": ctx.entorno.hora_local,
        },
    )
    db.add(entrada)
    db.commit()