import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { apiFetch, ApiError } from '../api/client'
import type { AuditoriaOut } from '../api/types'
import { Mensaje } from '../components/Mensaje'

export function AuditoriaPage() {
  const [registros, setRegistros] = useState<AuditoriaOut[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [resultado, setResultado] = useState('')
  const [usuarioCorreo, setUsuarioCorreo] = useState('')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [limit, setLimit] = useState(100)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    const params = new URLSearchParams()
    if (resultado) params.set('resultado', resultado)
    if (usuarioCorreo) params.set('usuario_correo', usuarioCorreo)
    if (desde) params.set('desde', desde)
    if (hasta) params.set('hasta', hasta)
    params.set('limit', String(limit))

    try {
      const datos = await apiFetch<AuditoriaOut[]>(`/auditoria?${params.toString()}`)
      setRegistros(datos)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo cargar la auditoría')
    } finally {
      setCargando(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    cargar()
  }, [cargar])

  function handleFiltrar(e: FormEvent) {
    e.preventDefault()
    cargar()
  }

  return (
    <div>
      <h1>Auditoría</h1>

      <form className="filtros" onSubmit={handleFiltrar}>
        <label>
          Resultado
          <select value={resultado} onChange={(e) => setResultado(e.target.value)}>
            <option value="">Todos</option>
            <option value="PERMITIDO">PERMITIDO</option>
            <option value="DENEGADO">DENEGADO</option>
          </select>
        </label>
        <label>
          Correo
          <input type="text" value={usuarioCorreo} onChange={(e) => setUsuarioCorreo(e.target.value)} />
        </label>
        <label>
          Desde
          <input type="date" value={desde} onChange={(e) => setDesde(e.target.value)} />
        </label>
        <label>
          Hasta
          <input type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} />
        </label>
        <label>
          Límite
          <input
            type="number"
            min={1}
            max={500}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          />
        </label>
        <button type="submit">Filtrar</button>
      </form>

      {error && <Mensaje tipo="error" texto={error} />}

      {cargando ? (
        <p className="cargando">Cargando…</p>
      ) : (
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Usuario</th>
              <th>Recurso</th>
              <th>Acción</th>
              <th>Etapa</th>
              <th>Resultado</th>
              <th>Motivo</th>
              <th>Política fallida</th>
            </tr>
          </thead>
          <tbody>
            {registros.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.fecha).toLocaleString('es-PE')}</td>
                <td>{r.usuario_correo ?? '—'}</td>
                <td>{r.recurso}</td>
                <td>{r.accion}</td>
                <td>{r.etapa}</td>
                <td>
                  <span className={`estado ${r.resultado === 'PERMITIDO' ? 'estado-publicado' : 'estado-pendiente'}`}>
                    {r.resultado}
                  </span>
                </td>
                <td>{r.motivo ?? '—'}</td>
                <td>{r.politica_fallida ?? '—'}</td>
              </tr>
            ))}
            {registros.length === 0 && (
              <tr>
                <td colSpan={8} className="vacio">
                  No hay registros con estos filtros.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  )
}
