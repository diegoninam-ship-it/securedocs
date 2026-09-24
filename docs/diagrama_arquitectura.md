# Diagrama de arquitectura — SecureDocs

Un único proyecto de Vercel sirve el frontend estático y el backend (como Vercel Function ASGI). El wrapper de la función recorta el prefijo `/api` y delega en el mismo FastAPI que corre en local, que aplica el flujo de dos etapas RBAC → ABAC antes de tocar cualquier documento, y audita cada intento contra Neon. Detalle completo en `CONTEXT.md` secciones 8 y 14.

```mermaid
flowchart TD
    Cliente["🌐 Navegador del usuario<br/>React SPA cargada"]

    subgraph Vercel["☁️ Vercel — proyecto único"]
        Frontend["Frontend estático<br/>React 19 + Vite<br/>(frontend/dist)"]

        subgraph Function["Vercel Function — api/index.py"]
            Wrapper["Wrapper ASGI<br/>recorta prefijo /api"]

            subgraph FastAPI["FastAPI — backend/app/main.py"]
                Auth["🔐 Authentication<br/>auth/security.py + dependencies.py<br/>JWT + token_version"]
                RBAC["🛡️ RBAC Service<br/>authz/rbac.py<br/>tiene_permiso()"]
                ABAC["⚖️ ABAC Policy Engine<br/>authz/abac/engine.py + policies.py<br/>P1–P9"]
                Routers["📄 Routers<br/>documentos · usuarios<br/>auditoria · catalogos"]
                Audit["📝 Audit Service<br/>audit/service.py<br/>registrar()"]

                Auth --> RBAC
                RBAC -->|"autorizar()"| ABAC
                ABAC -->|"verificar_abac()"| Routers
                Routers -->|"cada intento"| Audit
            end

            Wrapper -->|request| Auth
        end
    end

    Neon[("🗄️ PostgreSQL — Neon<br/>usuarios · roles · permisos · rol_permiso<br/>departamentos · documentos · politicas · auditoria")]

    Cliente -->|"GET /"| Frontend
    Cliente -->|"fetch('/api/...')<br/>Authorization: Bearer JWT"| Wrapper
    Auth -.->|SQLAlchemy| Neon
    Routers -.-> Neon
    Audit -.-> Neon

    style Cliente fill:#fef3c7,stroke:#92400e
    style Neon fill:#dcfce7,stroke:#166534
    style Frontend fill:#dbeafe,stroke:#1d4ed8
    style Wrapper fill:#e0e7ff,stroke:#4f46e5
```

> Fuente editable: [`diagrama_arquitectura.mmd`](diagrama_arquitectura.mmd) (abrir en [Mermaid Live](https://mermaid.live) para editar). Versión estática: [`diagrama_arquitectura.png`](diagrama_arquitectura.png).
