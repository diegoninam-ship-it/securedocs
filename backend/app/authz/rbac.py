from sqlalchemy.orm import Session

from app.models import Rol, RolPermiso, Permiso


def tiene_permiso(db: Session, rol_codigo: str, permiso_codigo: str) -> bool:
    resultado = (
        db.query(RolPermiso)
        .join(Rol, RolPermiso.rol_id == Rol.id)
        .join(Permiso, RolPermiso.permiso_id == Permiso.id)
        .filter(Rol.codigo == rol_codigo, Permiso.codigo == permiso_codigo)
        .first()
    )
    return resultado is not None