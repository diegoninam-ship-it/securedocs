from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.authz.context import Recurso, recurso_desde_documento
from app.audit.service import registrar
from app.authz.dependencies import autorizar, verificar_abac
from app.db import get_db
from app.models import Documento, Usuario
from app.schemas.documento import DocumentoCreate, DocumentoOut, DocumentoUpdate
from app.authz.abac.engine import evaluar_abac
from app.authz.context import Contexto

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/{documento_id}", response_model=DocumentoOut)
def obtener_documento(
    documento_id: int,
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_CONSULTAR", "CONSULTAR")),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")

    verificar_abac(request, db, recurso_desde_documento(doc), recurso_nombre=f"documento-{documento_id}")

    return doc

@router.post("", response_model=DocumentoOut, status_code=status.HTTP_201_CREATED)
def crear_documento(
    datos: DocumentoCreate,
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_CREAR", "CREAR")),
    db: Session = Depends(get_db),
):
    # Recurso "provisional": el documento aún no existe en BD, pero P2 necesita
    # evaluar el nivel de confidencialidad que se está proponiendo.
    recurso_provisional = Recurso(
        id=None,
        departamento=usuario.departamento.codigo if usuario.departamento else None,
        nivel_confidencialidad=datos.nivel_confidencialidad,
        estado="PENDIENTE",
        pais=usuario.pais,
        propietario_id=usuario.id,
    )
    verificar_abac(request, db, recurso_provisional, recurso_nombre="documento-nuevo")

    doc = Documento(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        propietario_id=usuario.id,
        departamento_id=usuario.departamento_id,
        nivel_confidencialidad=datos.nivel_confidencialidad,
        estado="PENDIENTE",
        pais=usuario.pais,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.put("/{documento_id}", response_model=DocumentoOut)
def modificar_documento(
    documento_id: int,
    datos: DocumentoUpdate,
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_MODIFICAR", "MODIFICAR")),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")

    # 1. ABAC contra el estado ACTUAL del documento (P1, P2, P3, P4, P5, P6)
    verificar_abac(request, db, recurso_desde_documento(doc), recurso_nombre=f"documento-{documento_id}")

    # 2. Si se propone subir el nivel de confidencialidad, el usuario debe
    #    calificar también para el nivel NUEVO — no solo el actual.
    nuevo_nivel = datos.nivel_confidencialidad if datos.nivel_confidencialidad is not None else doc.nivel_confidencialidad
    if nuevo_nivel > doc.nivel_confidencialidad and usuario.nivel_seguridad < nuevo_nivel:
        ctx = request.state.ctx_autorizar
        registrar(
            db, ctx, f"documento-{documento_id}", "DENEGADO", etapa="ABAC",
            motivo=f"Nivel de seguridad insuficiente para el nuevo nivel propuesto "
                   f"({usuario.nivel_seguridad} < {nuevo_nivel})",
            politica_fallida="P2",
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No calificas para el nivel de confidencialidad propuesto")

    # 3. Aplicar cambios
    if datos.titulo is not None:
        doc.titulo = datos.titulo
    if datos.descripcion is not None:
        doc.descripcion = datos.descripcion
    if datos.nivel_confidencialidad is not None:
        doc.nivel_confidencialidad = datos.nivel_confidencialidad

    # 4. D6: modificar un documento PUBLICADO lo regresa a PENDIENTE
    if doc.estado == "PUBLICADO":
        doc.estado = "PENDIENTE"
        doc.aprobado_por = None
        doc.fecha_aprobacion = None

    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_documento(
    documento_id: int,
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_ELIMINAR", "ELIMINAR")),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")

    verificar_abac(request, db, recurso_desde_documento(doc), recurso_nombre=f"documento-{documento_id}")

    db.delete(doc)
    db.commit()


@router.post("/{documento_id}/aprobar", response_model=DocumentoOut)
def aprobar_documento(
    documento_id: int,
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_APROBAR", "APROBAR")),
    db: Session = Depends(get_db),
):
    doc = db.query(Documento).filter(Documento.id == documento_id).first()
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")

    if doc.estado != "PENDIENTE":
        raise HTTPException(status.HTTP_409_CONFLICT, f"El documento está en estado {doc.estado}, no PENDIENTE")

    # Evalúa P1, P2, P4, P5, P6 (departamento, nivel, horario, país, dispositivo)
    # y P9 (segregación: el propietario no puede aprobar su propio documento)
    verificar_abac(request, db, recurso_desde_documento(doc), recurso_nombre=f"documento-{documento_id}")

    doc.estado = "PUBLICADO"
    doc.aprobado_por = usuario.id
    doc.fecha_aprobacion = func.now()
    db.commit()
    db.refresh(doc)
    return doc

@router.get("", response_model=list[DocumentoOut])
def listar_documentos(
    request: Request,
    usuario: Usuario = Depends(autorizar("DOC_CONSULTAR", "CONSULTAR")),
    db: Session = Depends(get_db),
):
    todos = db.query(Documento).all()
    ctx_base = request.state.ctx_autorizar

    visibles = []
    politicas_vistas = set()

    for doc in todos:
        ctx = Contexto(
            sujeto=ctx_base.sujeto,
            recurso=recurso_desde_documento(doc),
            accion="CONSULTAR",
            entorno=ctx_base.entorno,
        )
        resultado = evaluar_abac(db, ctx)
        if resultado.permitido:
            visibles.append(doc)
        else:
            politicas_vistas.update(resultado.politicas_fallidas)

    registrar(
        db, ctx_base, "documentos (listado)", "PERMITIDO",
        etapa="ABAC",
        motivo=f"{len(visibles)} visibles de {len(todos)} totales"
               + (f"; filtrados por: {','.join(sorted(politicas_vistas))}" if politicas_vistas else ""),
    )

    return visibles