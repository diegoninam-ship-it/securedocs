import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { apiFetch, ApiError } from '../api/client'
import type { DocumentoOut } from '../api/types'
import { Mensaje } from '../components/Mensaje'

export function DocumentoDetallePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [documento, setDocumento] = useState<DocumentoOut | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    let activo = true
    setCargando(true)
    apiFetch<DocumentoOut>(`/documentos/${id}`)
      .then((doc) => activo && setDocumento(doc))
      .catch((err) => activo && setError(err instanceof ApiError ? err.message : 'No se pudo cargar el documento'))
      .finally(() => activo && setCargando(false))
    return () => {
      activo = false
    }
  }, [id])

  if (cargando) return <p className="cargando">Cargando…</p>
  if (error) return <Mensaje tipo="error" texto={error} />
  if (!documento) return null

  return (
    <div className="detalle">
      <Link to="/documentos">← Volver a documentos</Link>
      <h1>{documento.titulo}</h1>
      <dl>
        <dt>Descripción</dt>
        <dd>{documento.descripcion || '—'}</dd>
        <dt>Departamento</dt>
        <dd>{documento.departamento ?? '—'}</dd>
        <dt>Nivel de confidencialidad</dt>
        <dd>{documento.nivel_confidencialidad}</dd>
        <dt>Estado</dt>
        <dd>
          <span className={`estado estado-${documento.estado.toLowerCase()}`}>{documento.estado}</span>
        </dd>
        <dt>País</dt>
        <dd>{documento.pais}</dd>
        <dt>Propietario</dt>
        <dd>Usuario #{documento.propietario_id}</dd>
        <dt>Fecha de creación</dt>
        <dd>{new Date(documento.fecha_creacion).toLocaleString('es-PE')}</dd>
        <dt>Aprobado por</dt>
        <dd>{documento.aprobado_por ? `Usuario #${documento.aprobado_por}` : '—'}</dd>
        <dt>Fecha de aprobación</dt>
        <dd>{documento.fecha_aprobacion ? new Date(documento.fecha_aprobacion).toLocaleString('es-PE') : '—'}</dd>
      </dl>
      <button type="button" onClick={() => navigate(-1)}>
        Volver
      </button>
    </div>
  )
}
