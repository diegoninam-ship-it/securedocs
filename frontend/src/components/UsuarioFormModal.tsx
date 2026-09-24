import { useState, type FormEvent } from 'react'
import type { DepartamentoOut, EstadoUsuario, RolOut, UsuarioOut } from '../api/types'
import { Mensaje } from './Mensaje'

export interface UsuarioFormValores {
  nombre: string
  correo: string
  password: string
  rol_codigo: string
  departamento_codigo: string
  nivel_seguridad: number
  pais: string
  tipo_contrato: string
  estado: EstadoUsuario
}

const ESTADOS: EstadoUsuario[] = ['ACTIVO', 'INACTIVO', 'SUSPENDIDO']

export function UsuarioFormModal({
  usuario,
  roles,
  departamentos,
  onCancelar,
  onGuardar,
  guardando,
  error,
}: {
  usuario: UsuarioOut | null
  roles: RolOut[]
  departamentos: DepartamentoOut[]
  onCancelar: () => void
  onGuardar: (valores: UsuarioFormValores) => void
  guardando: boolean
  error?: string | null
}) {
  const esNuevo = usuario === null
  const [nombre, setNombre] = useState(usuario?.nombre ?? '')
  const [correo, setCorreo] = useState(usuario?.correo ?? '')
  const [password, setPassword] = useState('')
  const [rolCodigo, setRolCodigo] = useState(usuario?.rol ?? roles[0]?.codigo ?? '')
  const [departamentoCodigo, setDepartamentoCodigo] = useState(usuario?.departamento ?? '')
  const [nivel, setNivel] = useState(usuario?.nivel_seguridad ?? 1)
  const [pais, setPais] = useState(usuario?.pais ?? 'PE')
  const [tipoContrato, setTipoContrato] = useState(usuario?.tipo_contrato ?? 'INTERNO')
  const [estado, setEstado] = useState<EstadoUsuario>(usuario?.estado ?? 'ACTIVO')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    onGuardar({
      nombre,
      correo,
      password,
      rol_codigo: rolCodigo,
      departamento_codigo: departamentoCodigo,
      nivel_seguridad: nivel,
      pais,
      tipo_contrato: tipoContrato,
      estado,
    })
  }

  return (
    <div className="modal-fondo">
      <form className="modal" onSubmit={handleSubmit}>
        <h2>{esNuevo ? 'Nuevo usuario' : `Editar usuario · ${usuario.correo}`}</h2>

        {error && <Mensaje tipo="error" texto={error} />}

        <label>
          Nombre
          <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        </label>

        <label>
          Correo
          <input
            type="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            disabled={!esNuevo}
          />
        </label>

        {esNuevo && (
          <label>
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
        )}

        {esNuevo && (
          <label>
            Rol
            <select value={rolCodigo} onChange={(e) => setRolCodigo(e.target.value)}>
              {roles.map((r) => (
                <option key={r.codigo} value={r.codigo}>
                  {r.nombre}
                </option>
              ))}
            </select>
          </label>
        )}

        <label>
          Departamento
          <select value={departamentoCodigo} onChange={(e) => setDepartamentoCodigo(e.target.value)}>
            <option value="">— Sin departamento (invitado) —</option>
            {departamentos.map((d) => (
              <option key={d.codigo} value={d.codigo}>
                {d.nombre}
              </option>
            ))}
          </select>
        </label>

        <label>
          Nivel de seguridad
          <select value={nivel} onChange={(e) => setNivel(Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>

        <label>
          País
          <input type="text" maxLength={2} value={pais} onChange={(e) => setPais(e.target.value.toUpperCase())} />
        </label>

        <label>
          Tipo de contrato
          <select value={tipoContrato} onChange={(e) => setTipoContrato(e.target.value)}>
            <option value="INTERNO">INTERNO</option>
            <option value="EXTERNO">EXTERNO</option>
          </select>
        </label>

        {!esNuevo && (
          <label>
            Estado
            <select value={estado} onChange={(e) => setEstado(e.target.value as EstadoUsuario)}>
              {ESTADOS.map((e) => (
                <option key={e} value={e}>
                  {e}
                </option>
              ))}
            </select>
          </label>
        )}

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
