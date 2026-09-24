export interface LoginRequest {
  correo: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface UsuarioMe {
  id: number
  nombre: string
  correo: string
  rol: string
  departamento: string | null
  nivel_seguridad: number
  pais: string
}

export interface PermisosOut {
  permisos: string[]
}

export type EstadoDocumento = 'PENDIENTE' | 'PUBLICADO'

export interface DocumentoOut {
  id: number
  titulo: string
  descripcion: string | null
  departamento: string | null
  nivel_confidencialidad: number
  estado: EstadoDocumento
  pais: string
  propietario_id: number
  fecha_creacion: string
  aprobado_por: number | null
  fecha_aprobacion: string | null
}

export interface DocumentoCreate {
  titulo: string
  descripcion?: string
  nivel_confidencialidad: number
}

export interface DocumentoUpdate {
  titulo?: string
  descripcion?: string
  nivel_confidencialidad?: number
}

export type EstadoUsuario = 'ACTIVO' | 'INACTIVO' | 'SUSPENDIDO'

export interface UsuarioOut {
  id: number
  nombre: string
  correo: string
  rol: string
  departamento: string | null
  nivel_seguridad: number
  pais: string
  tipo_contrato: string
  estado: EstadoUsuario
}

export interface UsuarioCreate {
  nombre: string
  correo: string
  password: string
  rol_codigo: string
  departamento_codigo?: string
  nivel_seguridad: number
  pais: string
  tipo_contrato: string
}

export interface UsuarioUpdate {
  nombre?: string
  departamento_codigo?: string
  nivel_seguridad?: number
  pais?: string
  tipo_contrato?: string
  estado?: EstadoUsuario
}

export interface UsuarioRolUpdate {
  rol_codigo: string
}

export interface AuditoriaOut {
  id: number
  usuario_correo: string | null
  recurso: string
  accion: string
  fecha: string
  resultado: 'PERMITIDO' | 'DENEGADO'
  etapa: 'AUTH' | 'RBAC' | 'ABAC'
  motivo: string | null
  politica_fallida: string | null
}

export interface RolOut {
  codigo: string
  nombre: string
}

export interface DepartamentoOut {
  codigo: string
  nombre: string
}

export interface HealthOut {
  status: string
  demo_mode: boolean
}
