from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models import Departamento, Rol, Usuario
from app.schemas.catalogos import DepartamentoOut, RolOut

router = APIRouter(prefix="/catalogos", tags=["catalogos"])


@router.get("/roles", response_model=list[RolOut])
def listar_roles(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Rol).all()


@router.get("/departamentos", response_model=list[DepartamentoOut])
def listar_departamentos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Departamento).all()
