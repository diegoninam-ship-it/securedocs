import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function RequireAuth({ children, permiso }: { children: ReactNode; permiso?: string }) {
  const { usuario, cargando, tienePermiso } = useAuth()

  if (cargando) return <p className="cargando">Cargando…</p>
  if (!usuario) return <Navigate to="/login" replace />
  if (permiso && !tienePermiso(permiso)) return <Navigate to="/documentos" replace />

  return <>{children}</>
}
