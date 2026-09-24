import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { apiFetch, clearToken, getToken, setOnUnauthorized, setToken } from '../api/client'
import type { HealthOut, LoginResponse, PermisosOut, UsuarioMe } from '../api/types'

interface AuthContextValue {
  usuario: UsuarioMe | null
  permisos: string[]
  demoMode: boolean
  cargando: boolean
  login: (correo: string, password: string) => Promise<void>
  logout: () => Promise<void>
  tienePermiso: (permiso: string) => boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioMe | null>(null)
  const [permisos, setPermisos] = useState<string[]>([])
  const [demoMode, setDemoMode] = useState(false)
  const [cargando, setCargando] = useState(true)

  const cerrarSesionLocal = useCallback(() => {
    setUsuario(null)
    setPermisos([])
  }, [])

  useEffect(() => {
    setOnUnauthorized(cerrarSesionLocal)
  }, [cerrarSesionLocal])

  const cargarSesion = useCallback(async () => {
    try {
      const health = await apiFetch<HealthOut>('/health')
      setDemoMode(health.demo_mode)
    } catch {
      // el health check no requiere auth; si falla, se ignora y se asume demo_mode=false
    }

    if (!getToken()) {
      setCargando(false)
      return
    }

    try {
      const [me, permisosOut] = await Promise.all([
        apiFetch<UsuarioMe>('/auth/me'),
        apiFetch<PermisosOut>('/auth/me/permisos'),
      ])
      setUsuario(me)
      setPermisos(permisosOut.permisos)
    } catch {
      clearToken()
      cerrarSesionLocal()
    } finally {
      setCargando(false)
    }
  }, [cerrarSesionLocal])

  useEffect(() => {
    cargarSesion()
  }, [cargarSesion])

  const login = useCallback(async (correo: string, password: string) => {
    const respuesta = await apiFetch<LoginResponse>('/auth/login', {
      method: 'POST',
      body: { correo, password },
    })
    setToken(respuesta.access_token)
    const [me, permisosOut] = await Promise.all([
      apiFetch<UsuarioMe>('/auth/me'),
      apiFetch<PermisosOut>('/auth/me/permisos'),
    ])
    setUsuario(me)
    setPermisos(permisosOut.permisos)
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiFetch('/auth/logout', { method: 'POST' })
    } catch {
      // si el logout falla (ej. token ya vencido) igual limpiamos el lado del cliente
    }
    clearToken()
    cerrarSesionLocal()
  }, [cerrarSesionLocal])

  const tienePermiso = useCallback((permiso: string) => permisos.includes(permiso), [permisos])

  return (
    <AuthContext.Provider value={{ usuario, permisos, demoMode, cargando, login, logout, tienePermiso }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
