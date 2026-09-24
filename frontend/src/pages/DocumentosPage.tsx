import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch, ApiError } from '../api/client'
import type { DocumentoCreate, DocumentoOut, DocumentoUpdate } from '../api/types'
import { useAuth } from '../auth/AuthContext'
import { DocumentoFormModal, type DocumentoFormValores } from '../components/DocumentoFormModal'
import { Mensaje } from '../components/Mensaje'

export function DocumentosPage() {
  const { tienePermiso } = useAuth()
  const [documentos, setDocumentos] = useState<DocumentoOut[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modal, setModal] = useState<'crear' | DocumentoOut | null>(null)
  const [guardando, setGuardando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const datos = await apiFetch<DocumentoOut[]>('/documentos')
      setDocumentos(datos)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo cargar la lista de documentos')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    cargar()
  }, [cargar])

  async function handleGuardar(valores: DocumentoFormValores) {
    setGuardando(true)
    setError(null)
    try {
      if (modal === 'crear') {
        const payload: DocumentoCreate = {
          titulo: valores.titulo,
          descripcion: valores.descripcion || undefined,
          nivel_confidencialidad: valores.nivel_confidencialidad,
        }
        await apiFetch<DocumentoOut>('/documentos', { method: 'POST', body: payload })
      } else if (modal) {
        const payload: DocumentoUpdate = {
          titulo: valores.titulo,
          descripcion: valores.descripcion || undefined,
          nivel_confidencialidad: valores.nivel_confidencialidad,
        }
        await apiFetch<DocumentoOut>(`/documentos/${modal.id}`, { method: 'PUT', body: payload })
      }
      setModal(null)
      await cargar()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo guardar el documento')
    } finally {
      setGuardando(false)
    }
  }

  async function handleEliminar(doc: DocumentoOut) {
    if (!confirm(`¿Eliminar "${doc.titulo}"?`)) return
    setError(null)
    try {
      await apiFetch(`/documentos/${doc.id}`, { method: 'DELETE' })
      await cargar()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo eliminar el documento')
    }
  }

  async function handleAprobar(doc: DocumentoOut) {
    setError(null)
    try {
      await apiFetch<DocumentoOut>(`/documentos/${doc.id}/aprobar`, { method: 'POST' })
      await cargar()
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError(`Conflicto: ${err.message}`)
      } else {
        setError(err instanceof ApiError ? err.message : 'No se pudo aprobar el documento')
      }
    }
  }

  return (
    <div>
      <div className="pagina-cabecera">
        <h1>Documentos</h1>
        {tienePermiso('DOC_CREAR') && (
          <button type="button" onClick={() => { setError(null); setModal('crear') }}>
            Nuevo documento
          </button>
        )}
      </div>

      {error && !modal && <Mensaje tipo="error" texto={error} />}

      {cargando ? (
        <p className="cargando">Cargando…</p>
      ) : (
        <table className="tabla">
          <thead>
            <tr>
              <th>Título</th>
              <th>Departamento</th>
              <th>Nivel</th>
              <th>Estado</th>
              <th>País</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {documentos.map((doc) => (
              <tr key={doc.id}>
                <td>
                  <Link to={`/documentos/${doc.id}`}>{doc.titulo}</Link>
                </td>
                <td>{doc.departamento ?? '—'}</td>
                <td>{doc.nivel_confidencialidad}</td>
                <td>
                  <span className={`estado estado-${doc.estado.toLowerCase()}`}>{doc.estado}</span>
                </td>
                <td>{doc.pais}</td>
                <td className="acciones">
                  {tienePermiso('DOC_MODIFICAR') && (
                    <button type="button" onClick={() => { setError(null); setModal(doc) }}>
                      Editar
                    </button>
                  )}
                  {tienePermiso('DOC_APROBAR') && doc.estado === 'PENDIENTE' && (
                    <button type="button" onClick={() => handleAprobar(doc)}>
                      Aprobar
                    </button>
                  )}
                  {tienePermiso('DOC_ELIMINAR') && (
                    <button type="button" className="peligro" onClick={() => handleEliminar(doc)}>
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {documentos.length === 0 && (
              <tr>
                <td colSpan={6} className="vacio">
                  No hay documentos visibles para tu usuario.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {modal && (
        <DocumentoFormModal
          documento={modal === 'crear' ? null : modal}
          onCancelar={() => setModal(null)}
          onGuardar={handleGuardar}
          guardando={guardando}
          error={error}
        />
      )}
    </div>
  )
}
