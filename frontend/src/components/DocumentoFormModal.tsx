import { useState, type FormEvent } from 'react'
import type { DocumentoOut } from '../api/types'
import { Mensaje } from './Mensaje'

export interface DocumentoFormValores {
  titulo: string
  descripcion: string
  nivel_confidencialidad: number
}

export function DocumentoFormModal({
  documento,
  onCancelar,
  onGuardar,
  guardando,
  error,
}: {
  documento: DocumentoOut | null
  onCancelar: () => void
  onGuardar: (valores: DocumentoFormValores) => void
  guardando: boolean
  error?: string | null
}) {
  const [titulo, setTitulo] = useState(documento?.titulo ?? '')
  const [descripcion, setDescripcion] = useState(documento?.descripcion ?? '')
  const [nivel, setNivel] = useState(documento?.nivel_confidencialidad ?? 1)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    onGuardar({ titulo, descripcion, nivel_confidencialidad: nivel })
  }

  return (
    <div className="modal-fondo">
      <form className="modal" onSubmit={handleSubmit}>
        <h2>{documento ? 'Editar documento' : 'Nuevo documento'}</h2>

        {error && <Mensaje tipo="error" texto={error} />}

        <label>
          Título
          <input type="text" value={titulo} onChange={(e) => setTitulo(e.target.value)} required />
        </label>

        <label>
          Descripción
          <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)} rows={3} />
        </label>

        <label>
          Nivel de confidencialidad
          <select value={nivel} onChange={(e) => setNivel(Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>

        <div className="modal-acciones">
          <button type="button" onClick={onCancelar} disabled={guardando}>
            Cancelar
          </button>
          <button type="submit" disabled={guardando}>
            {guardando ? 'Guardando…' : 'Guardar'}
          </button>
        </div>
      </form>
    </div>
  )
}
