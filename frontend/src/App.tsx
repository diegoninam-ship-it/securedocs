import { Navigate, Route, Routes } from 'react-router-dom'
import { RequireAuth } from './auth/RequireAuth'
import { Layout } from './components/Layout'
import { AuditoriaPage } from './pages/AuditoriaPage'
import { DocumentoDetallePage } from './pages/DocumentoDetallePage'
import { DocumentosPage } from './pages/DocumentosPage'
import { LoginPage } from './pages/LoginPage'
import { UsuariosPage } from './pages/UsuariosPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route path="/documentos" element={<DocumentosPage />} />
        <Route path="/documentos/:id" element={<DocumentoDetallePage />} />
        <Route
          path="/usuarios"
          element={
            <RequireAuth permiso="USUARIOS_GESTIONAR">
              <UsuariosPage />
            </RequireAuth>
          }
        />
        <Route
          path="/auditoria"
          element={
            <RequireAuth permiso="AUDITORIA_VER">
              <AuditoriaPage />
            </RequireAuth>
          }
        />
      </Route>

      <Route path="/" element={<Navigate to="/documentos" replace />} />
      <Route path="*" element={<Navigate to="/documentos" replace />} />
    </Routes>
  )
}
