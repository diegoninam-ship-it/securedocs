from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.security import decodificar_token
from app.authz.abac.engine import evaluar_abac
from app.authz.context import Contexto, Sujeto, construir_entorno
from app.db import get_db
from app.models import Usuario

bearer_scheme = HTTPBearer()


def get_current_user(
    request: Request,
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = decodificar_token(credenciales.credentials)
    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expirado")
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == int(payload["sub"])).first()
    if usuario is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")

    if payload["ver"] != usuario.token_version:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión revocada, vuelve a iniciar sesión")

    # P7 evaluada aquí: en cada petición, no solo al login (D3)
    sujeto = Sujeto(
        id=usuario.id,
        correo=usuario.correo,
        rol=usuario.rol.codigo,
        departamento=usuario.departamento.codigo if usuario.departamento else None,
        nivel_seguridad=usuario.nivel_seguridad,
        pais=usuario.pais,
        tipo_contrato=usuario.tipo_contrato,
        estado=usuario.estado,
    )
    entorno = construir_entorno(request)
    ctx = Contexto(sujeto=sujeto, recurso=None, accion="CUALQUIERA", entorno=entorno)

    resultado = evaluar_abac(db, ctx)
    if not resultado.permitido:
        raise HTTPException(status.HTTP_403_FORBIDDEN, resultado.motivo)

    request.state.contexto_base = ctx  # reutilizado en autorizar() — Paso 7.4
    return usuario