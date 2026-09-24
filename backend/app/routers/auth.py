from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit.service import registrar
from app.auth.dependencies import get_current_user
from app.auth.security import crear_token, verificar_password
from app.authz.context import Contexto, Entorno, Sujeto, construir_entorno
from app.db import get_db
from app.models import Usuario
from app.schemas.auth import LoginRequest, LoginResponse, UsuarioMe

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, request: Request, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == datos.correo).first()

    entorno = construir_entorno(request)

    if usuario is None or not verificar_password(datos.password, usuario.password_hash):
        ctx_fallido = Contexto(
            sujeto=Sujeto(id=None, correo=datos.correo, rol="DESCONOCIDO", departamento=None,
                          nivel_seguridad=0, pais="", tipo_contrato="", estado=""),
            recurso=None, accion="LOGIN", entorno=entorno,
        )
        registrar(db, ctx_fallido, "auth", "DENEGADO", etapa="AUTH", motivo="Credenciales inválidas")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos")

    sujeto = Sujeto(
        id=usuario.id, correo=usuario.correo, rol=usuario.rol.codigo,
        departamento=usuario.departamento.codigo if usuario.departamento else None,
        nivel_seguridad=usuario.nivel_seguridad, pais=usuario.pais,
        tipo_contrato=usuario.tipo_contrato, estado=usuario.estado,
    )
    ctx = Contexto(sujeto=sujeto, recurso=None, accion="LOGIN", entorno=entorno)

    from app.authz.abac.engine import evaluar_abac
    resultado = evaluar_abac(db, ctx)  # evalúa P7: ¿usuario ACTIVO?
    if not resultado.permitido:
        registrar(db, ctx, "auth", "DENEGADO", etapa="ABAC", motivo=resultado.motivo)
        raise HTTPException(status.HTTP_403_FORBIDDEN, resultado.motivo)

    token = crear_token(usuario.id, usuario.token_version)
    registrar(db, ctx, "auth", "PERMITIDO", etapa="ABAC")
    return LoginResponse(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    usuario.token_version += 1
    db.commit()


@router.get("/me", response_model=UsuarioMe)
def me(usuario: Usuario = Depends(get_current_user)):
    return UsuarioMe(
        id=usuario.id, nombre=usuario.nombre, correo=usuario.correo,
        rol=usuario.rol.codigo,
        departamento=usuario.departamento.codigo if usuario.departamento else None,
        nivel_seguridad=usuario.nivel_seguridad, pais=usuario.pais,
    )