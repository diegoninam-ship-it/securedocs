from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.authz.dependencies import autorizar
from app.db import get_db
from app.models import Auditoria, Usuario
from app.schemas.auditoria import AuditoriaOut

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get("", response_model=list[AuditoriaOut])
def listar_auditoria(
    usuario: Usuario = Depends(autorizar("AUDITORIA_VER", "VER_AUDITORIA")),
    db: Session = Depends(get_db),
    resultado: str | None = Query(None, description="PERMITIDO o DENEGADO"),
    usuario_correo: str | None = Query(None),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    limit: int = Query(100, le=500),
):
    q = db.query(Auditoria)

    if resultado:
        q = q.filter(Auditoria.resultado == resultado)
    if usuario_correo:
        q = q.filter(Auditoria.usuario_correo == usuario_correo)
    if desde:
        q = q.filter(Auditoria.fecha >= desde)
    if hasta:
        q = q.filter(Auditoria.fecha <= hasta)

    return q.order_by(Auditoria.fecha.desc()).limit(limit).all()