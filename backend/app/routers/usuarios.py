from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit.service import registrar
from app.auth.security import hash_password
from app.authz.dependencies import autorizar
from app.db import get_db
from app.models import Departamento, Rol, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioRolUpdate, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

def usuario_a_out(u: Usuario) -> UsuarioOut:
    return UsuarioOut(
        id=u.id,
        nombre=u.nombre,
        correo=u.correo,
        rol=u.rol.codigo,
        departamento=u.departamento.codigo if u.departamento else None,
        nivel_seguridad=u.nivel_seguridad,
        pais=u.pais,
        tipo_contrato=u.tipo_contrato,
        estado=u.estado,
    )


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    request: Request,
    usuario: Usuario = Depends(autorizar("USUARIOS_GESTIONAR", "GESTIONAR_USUARIOS")),
    db: Session = Depends(get_db),
):
    ctx = request.state.ctx_autorizar
    registrar(db, ctx, "usuarios (listado)", "PERMITIDO", etapa="RBAC")
    return [usuario_a_out(u) for u in db.query(Usuario).all()]


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    datos: UsuarioCreate,
    request: Request,
    usuario: Usuario = Depends(autorizar("USUARIOS_GESTIONAR", "GESTIONAR_USUARIOS")),
    db: Session = Depends(get_db),
):
    rol = db.query(Rol).filter(Rol.codigo == datos.rol_codigo).first()
    if rol is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Rol '{datos.rol_codigo}' no existe")

    depto = None
    if datos.departamento_codigo:
        depto = db.query(Departamento).filter(Departamento.codigo == datos.departamento_codigo).first()
        if depto is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Departamento '{datos.departamento_codigo}' no existe")

    if db.query(Usuario).filter(Usuario.correo == datos.correo).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese correo")

    nuevo = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        rol_id=rol.id,
        departamento_id=depto.id if depto else None,
        nivel_seguridad=datos.nivel_seguridad,
        pais=datos.pais,
        tipo_contrato=datos.tipo_contrato,
        estado="ACTIVO",
    )
    db.add(nuevo)

    ctx = request.state.ctx_autorizar
    registrar(db, ctx, f"usuario-nuevo:{datos.correo}", "PERMITIDO", etapa="RBAC")

    db.commit()
    db.refresh(nuevo)
    return usuario_a_out(nuevo)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def modificar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    request: Request,
    usuario_actor: Usuario = Depends(autorizar("USUARIOS_GESTIONAR", "GESTIONAR_USUARIOS")),
    db: Session = Depends(get_db),
):
    objetivo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if objetivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    if datos.nombre is not None:
        objetivo.nombre = datos.nombre
    if datos.nivel_seguridad is not None:
        objetivo.nivel_seguridad = datos.nivel_seguridad
    if datos.pais is not None:
        objetivo.pais = datos.pais
    if datos.tipo_contrato is not None:
        objetivo.tipo_contrato = datos.tipo_contrato
    if datos.estado is not None:
        objetivo.estado = datos.estado
    if datos.departamento_codigo is not None:
        depto = db.query(Departamento).filter(Departamento.codigo == datos.departamento_codigo).first()
        if depto is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Departamento '{datos.departamento_codigo}' no existe")
        objetivo.departamento_id = depto.id

    ctx = request.state.ctx_autorizar
    registrar(db, ctx, f"usuario-{usuario_id}", "PERMITIDO", etapa="RBAC")

    db.commit()
    db.refresh(objetivo)
    return usuario_a_out(objetivo)


@router.put("/{usuario_id}/rol", response_model=UsuarioOut)
def asignar_rol(
    usuario_id: int,
    datos: UsuarioRolUpdate,
    request: Request,
    usuario_actor: Usuario = Depends(autorizar("ROLES_ASIGNAR", "ASIGNAR_ROLES")),
    db: Session = Depends(get_db),
):
    objetivo = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if objetivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    rol = db.query(Rol).filter(Rol.codigo == datos.rol_codigo).first()
    if rol is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Rol '{datos.rol_codigo}' no existe")

    objetivo.rol_id = rol.id

    ctx = request.state.ctx_autorizar
    registrar(db, ctx, f"usuario-{usuario_id}", "PERMITIDO", etapa="RBAC")

    db.commit()
    db.refresh(objetivo)
    return usuario_a_out(objetivo)