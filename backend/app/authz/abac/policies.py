from datetime import time

from app.authz.abac.registry import politica, Resultado
from app.authz.context import Contexto


@politica("P1")
def departamento(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.departamento == ctx.recurso.departamento:
        return Resultado.ok()
    return Resultado.deny(
        f"Departamento distinto ({ctx.sujeto.departamento} ≠ {ctx.recurso.departamento})"
    )


@politica("P2")
def nivel_seguridad(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.nivel_seguridad >= ctx.recurso.nivel_confidencialidad:
        return Resultado.ok()
    return Resultado.deny(
        f"Nivel de seguridad insuficiente "
        f"({ctx.sujeto.nivel_seguridad} < {ctx.recurso.nivel_confidencialidad})"
    )


@politica("P3")
def propiedad(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.id == ctx.recurso.propietario_id:
        return Resultado.ok()
    return Resultado.deny("El usuario no es propietario del documento")


@politica("P4")
def horario(ctx: Contexto, params: dict) -> Resultado:
    if ctx.recurso.nivel_confidencialidad < params["umbral"]:
        return Resultado.ok()  # no aplica a este nivel de confidencialidad

    hora_actual = time.fromisoformat(ctx.entorno.hora_local)
    inicio = time.fromisoformat(params["hora_inicio"])
    fin = time.fromisoformat(params["hora_fin"])

    if inicio <= hora_actual <= fin:
        return Resultado.ok()
    return Resultado.deny(
        f"Fuera del horario autorizado ({params['hora_inicio']}-{params['hora_fin']}, "
        f"hora actual: {ctx.entorno.hora_local})"
    )


@politica("P5")
def pais(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.pais == ctx.recurso.pais and ctx.entorno.ubicacion == ctx.recurso.pais:
        return Resultado.ok()
    return Resultado.deny(
        f"País no coincide (usuario: {ctx.sujeto.pais}, "
        f"ubicación: {ctx.entorno.ubicacion}, documento: {ctx.recurso.pais})"
    )


@politica("P6")
def dispositivo(ctx: Contexto, params: dict) -> Resultado:
    if ctx.recurso.nivel_confidencialidad < params["umbral"]:
        return Resultado.ok()

    if ctx.entorno.dispositivo == params["dispositivo_requerido"]:
        return Resultado.ok()
    return Resultado.deny(
        f"Documento de nivel {ctx.recurso.nivel_confidencialidad} requiere dispositivo "
        f"{params['dispositivo_requerido']} (actual: {ctx.entorno.dispositivo})"
    )


@politica("P7")
def estado_usuario(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.estado == params["estado_requerido"]:
        return Resultado.ok()
    return Resultado.deny(f"Usuario en estado {ctx.sujeto.estado}, se requiere ACTIVO")


@politica("P8")
def invitados(ctx: Contexto, params: dict) -> Resultado:
    if (
        ctx.sujeto.tipo_contrato == params["tipo_contrato_requerido"]
        and ctx.recurso.nivel_confidencialidad <= params["nivel_maximo"]
        and ctx.recurso.estado == params["estado_requerido"]
    ):
        return Resultado.ok()
    return Resultado.deny(
        "Invitado no cumple las condiciones de acceso "
        f"(contrato={ctx.sujeto.tipo_contrato}, nivel={ctx.recurso.nivel_confidencialidad}, "
        f"estado={ctx.recurso.estado})"
    )


@politica("P9")
def segregacion_funciones(ctx: Contexto, params: dict) -> Resultado:
    if ctx.sujeto.id != ctx.recurso.propietario_id:
        return Resultado.ok()
    return Resultado.deny("El propietario de un documento no puede aprobarlo")