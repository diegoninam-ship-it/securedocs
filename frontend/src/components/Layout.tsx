import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { SimuladorPanel } from './SimuladorPanel'

export function Layout() {
  const { usuario, demoMode, logout, tienePermiso } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="layout">
      <header className="navbar">
        <div className="navbar-marca">SecureDocs</div>
        <nav className="navbar-links">
          <NavLink to="/documentos" className={({ isActive }) => (isActive ? 'activo' : '')}>
            Documentos
          </NavLink>
          {tienePermiso('USUARIOS_GESTIONAR') && (
            <NavLink to="/usuarios" className={({ isActive }) => (isActive ? 'activo' : '')}>
              Usuarios
            </NavLink>
          )}
          {tienePermiso('AUDITORIA_VER') && (
            <NavLink to="/auditoria" className={({ isActive }) => (isActive ? 'activo' : '')}>
              Auditoría
            </NavLink>
          )}
        </nav>
        <div className="navbar-usuario">
          {usuario && (
            <span>
              {usuario.nombre} · {usuario.rol}
              {usuario.departamento ? ` · ${usuario.departamento}` : ''} · Nivel {usuario.nivel_seguridad}
            </span>
          )}
          <button type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {demoMode && <SimuladorPanel />}

      <main className="contenido">
        <Outlet />
      </main>
    </div>
  )
}
