import { useCallback, useEffect, useState } from 'react'
import { apiFetch, ApiError } from '../api/client'
import type { DepartamentoOut, RolOut, UsuarioCreate, UsuarioOut, UsuarioUpdate } from '../api/types'
import { useAuth } from '../auth/AuthContext'
import { Mensaje } from '../components/Mensaje'
import { UsuarioFormModal, type UsuarioFormValores } from '../components/UsuarioFormModal'

export function UsuariosPage() {
  const { tienePermiso } = useAuth()
  const [usuarios, setUsuarios] = useState<UsuarioOut[]>([])
  const [roles, setRoles] = useState<RolOut[]>([])
  const [departamentos, setDepartamentos] = useState<DepartamentoOut[]>([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modal, setModal] = useState<'crear' | UsuarioOut | null>(null)
  const [guardando, setGuardando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const [listaUsuarios, listaRoles, listaDeptos] = await Promise.all([
        apiFetch<UsuarioOut[]>('/usuarios'),
        apiFetch<RolOut[]>('/catalogos/roles'),
        apiFetch<DepartamentoOut[]>('/catalogos/departamentos'),
      ])
      setUsuarios(listaUsuarios)
      setRoles(listaRoles)
      setDepartamentos(listaDeptos)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo cargar la lista de usuarios')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    cargar()
  }, [cargar])

  async function handleGuardar(valores: UsuarioFormValores) {
    setGuardando(true)
    setError(null)
    try {
      if (modal === 'crear') {
        const payload: UsuarioCreate = {
          nombre: valores.nombre,
          correo: valores.correo,
          password: valores.password,
          rol_codigo: valores.rol_codigo,
          departamento_codigo: valores.departamento_codigo || undefined,
          nivel_seguridad: valores.nivel_seguridad,
          pais: valores.pais,
          tipo_contrato: valores.tipo_contrato,
        }
        await apiFetch<UsuarioOut>('/usuarios', { method: 'POST', body: payload })
      } else if (modal) {
        const payload: UsuarioUpdate = {
          nombre: valores.nombre,
          departamento_codigo: valores.departamento_codigo || undefined,
          nivel_seguridad: valores.nivel_seguridad,
          pais: valores.pais,
          tipo_contrato: valores.tipo_contrato,
          estado: valores.estado,
        }
        await apiFetch<UsuarioOut>(`/usuarios/${modal.id}`, { method: 'PUT', body: payload })
      }
      setModal(null)
      await cargar()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo guardar el usuario')
    } finally {
      setGuardando(false)
    }
  }

  async function handleCambiarRol(usuario: UsuarioOut, rolCodigo: string) {
    if (rolCodigo === usuario.rol) return
    setError(null)
    try {
      await apiFetch<UsuarioOut>(`/usuarios/${usuario.id}/rol`, {
        method: 'PUT',
        body: { rol_codigo: rolCodigo },
      })
      await cargar()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo cambiar el rol')
    }
  }

  return (
    <div>
      <div className="pagina-cabecera">
        <h1>Usuarios</h1>
        <button type="button" onClick={() => { setError(null); setModal('crear') }}>
          Nuevo usuario
        </button>
      </div>

      {error && !modal && <Mensaje tipo="error" texto={error} />}

      {cargando ? (
        <p className="cargando">Cargando…</p>
      ) : (
        <table className="tabla">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Departamento</th>
              <th>Nivel</th>
              <th>País</th>
              <th>Contrato</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td>{u.nombre}</td>
                <td>{u.correo}</td>
                <td>
                  {tienePermiso('ROLES_ASIGNAR') ? (
                    <select value={u.rol} onChange={(e) => handleCambiarRol(u, e.target.value)}>
                      {roles.map((r) => (
                        <option key={r.codigo} value={r.codigo}>
                          {r.nombre}
                        </option>
                      ))}
                    </select>
                  ) : (
                    u.rol
                  )}
                </td>
                <td>{u.departamento ?? '—'}</td>
                <td>{u.nivel_seguridad}</td>
                <td>{u.pais}</td>
                <td>{u.tipo_contrato}</td>
                <td>
                  <span className={`estado estado-${u.estado.toLowerCase()}`}>{u.estado}</span>
                </td>
                <td className="acciones">
                  <button type="button" onClick={() => { setError(null); setModal(u) }}>
                    Editar
                  </button>
                </td>
              </tr>
            ))}
            {usuarios.length === 0 && (
              <tr>
                <td colSpan={9} className="vacio">
                  No hay usuarios registrados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      {modal && (
        <UsuarioFormModal
          usuario={modal === 'crear' ? null : modal}
          roles={roles}
          departamentos={departamentos}
          onCancelar={() => setModal(null)}
          onGuardar={handleGuardar}
          guardando={guardando}
          error={error}
        />
      )}
    </div>
  )
}
