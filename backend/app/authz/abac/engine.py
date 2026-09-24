from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.authz.abac.registry import REGISTRO
from app.authz.context import Contexto
from app.models import Politica

from app.authz.abac import policies  # noqa: F401 — el import ejecuta los decoradores @politica


@dataclass
class ResultadoABAC:
    permitido: bool
    motivo: str | None = None
    politicas_fallidas: list[str] = field(default_factory=list)


def _aplica(politica_row: Politica, rol_codigo: str, accion: str) -> bool:
    operaciones = politica_row.operaciones or []
    if accion not in operaciones and "CUALQUIERA" not in operaciones:
        return False

    if politica_row.roles_aplicables:
        return rol_codigo in politica_row.roles_aplicables

    exentos = politica_row.roles_exentos or []
    return rol_codigo not in exentos


def evaluar_abac(db: Session, ctx: Contexto) -> ResultadoABAC:
    politicas_activas = db.query(Politica).filter(Politica.activa.is_(True)).all()

    motivos = []
    fallidas = []

    for p in politicas_activas:
        if not _aplica(p, ctx.sujeto.rol, ctx.accion):
            continue

        if ctx.recurso is None and p.codigo != "P7":
            # Sin recurso concreto (ej. LOGIN), solo P7 tiene algo que evaluar
            continue

        funcion = REGISTRO.get(p.codigo)
        if funcion is None:
            continue  # política configurada en BD pero sin implementación aún

        resultado = funcion(ctx, p.parametros or {})
        if not resultado.permitido:
            motivos.append(resultado.motivo)
            fallidas.append(p.codigo)

    if fallidas:
        return ResultadoABAC(permitido=False, motivo="; ".join(motivos), politicas_fallidas=fallidas)
    return ResultadoABAC(permitido=True)