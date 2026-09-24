from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit.service import registrar
from app.auth.dependencies import get_current_user
from app.authz.abac.engine import evaluar_abac
from app.authz.context import Contexto, Recurso
from app.authz.rbac import tiene_permiso
from app.config import settings
from app.db import get_db
from app.models import Usuario


def autorizar(permiso_rbac: str, recurso_nombre: str = "documento"):
    def dependencia(
        request: Request,
        usuario: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ctx_base = request.state.contexto_base  # armado en get_current_user
        ctx = Contexto(
            sujeto=ctx_base.sujeto,
            recurso=None,
            accion=permiso_rbac,
            entorno=ctx_base.entorno,
        )

        # --- RBAC ---
        if not tiene_permiso(db, ctx.sujeto.rol, permiso_rbac):
            registrar(db, ctx, recurso_nombre, "DENEGADO", etapa="RBAC", motivo="El rol no tiene este permiso")
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esta operación")

        request.state.ctx_autorizar = ctx  # el router completa ctx.recurso y llama a verificar_abac()
        return usuario

    return dependencia


def verificar_abac(request: Request, db: Session, recurso: Recurso, recurso_nombre: str = "documento"):
    """Se llama DESDE el router, una vez que este arma el Recurso real (con datos de la BD o del body)."""
    ctx = request.state.ctx_autorizar
    ctx.recurso = recurso

    resultado = evaluar_abac(db, ctx)
    if not resultado.permitido:
        registrar(
            db, ctx, recurso_nombre, "DENEGADO", etapa="ABAC",
            motivo=resultado.motivo, politica_fallida=",".join(resultado.politicas_fallidas),
        )
        detalle = resultado.motivo if settings.demo_mode else "Acceso denegado"
        raise HTTPException(status.HTTP_403_FORBIDDEN, detalle)

    registrar(db, ctx, recurso_nombre, "PERMITIDO", etapa="ABAC")