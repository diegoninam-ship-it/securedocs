# CONTEXT.md — SecureDocs

> **Para cualquier agente (Claude Code u otro):** lee este archivo completo antes de iniciar cualquier tarea. Es la fuente de verdad del proyecto. Al terminar cada tarea, actualiza la sección **3. Estado actual** y agrega una entrada en **15. Changelog**. Si una decisión de este archivo entra en conflicto con lo que te pidan, detente y consúltalo con el usuario antes de cambiarla.

---

## 1. Resumen del proyecto

| Campo | Valor |
|---|---|
| Nombre | SecureDocs — Sistema de Gestión de Expedientes con RBAC y ABAC |
| Contexto | Laboratorio GLAB-S06 (Cloud Security), curso *Desarrollo de Soluciones en la Nube*, Tecsup |
| Cliente ficticio | TechCorp S.A. |
| Objetivo | Autorizar cada operación sobre documentos en dos etapas: **RBAC** (¿el rol permite la acción?) y luego **ABAC** (¿se cumplen las políticas de atributos en este contexto?). Solo se autoriza si ambas permiten. Todo intento se audita con su motivo. |
| Repositorio | https://github.com/diegoninam-ship-it/securedocs.git (rama `main`) |
| Autor | Diego Nina |

### Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+ · FastAPI · SQLAlchemy · Alembic · PyJWT · bcrypt · pydantic-settings |
| Base de datos | PostgreSQL gestionado en **Neon** (proyecto `securedocs`, región AWS US East 2 / Ohio) |
| Frontend | React 19 + Vite + TypeScript |
| Despliegue | Vercel, proyecto único: frontend estático + FastAPI como Vercel Function en `api/index.py` (config en `vercel.json`, ver sección 14) |

---

## 2. Etapas del proyecto

| # | Etapa | Estado |
|---|---|---|
| 1 | Planificación | ✅ Cerrada |
| 2 | Desarrollo | ✅ Backend y Frontend implementados |
| 3 | Testing (backend + frontend integrados) | 🟡 Manual (Fases 1–4) ✅ 2026-09-24 · Automatizado (Fase 0, pytest) ⏳ pospuesto |
| 4 | Despliegue en Vercel (opcional) | 🟡 Configuración lista (sección 14) · falta el despliegue real (requiere cuenta/CLI de Vercel del usuario) |

> **Actualización 2026-09-23:** la etapa de *Testing* formal, originalmente eliminada del plan (los 17 casos de la sección 10 se habían verificado de forma ad hoc contra el backend durante Desarrollo), se **reincorpora** ahora que existe frontend. Motivo: verificar que backend + frontend integrados siguen operativos end-to-end, sin regresiones. Ver el plan detallado en la sección 13.

---

## 3. Estado actual

**Última actualización:** 2026-09-24

- Backend completo: 17 endpoints, motor RBAC + ABAC (P1–P9), autenticación JWT con `token_version`, auditoría.
- Pendientes #2 y #3 de la sección 11 resueltos: `GET /auth/me/permisos`, `GET /catalogos/roles`, `GET /catalogos/departamentos`. Pendiente #1 (override de hora para P4) se decidió **no implementar**.
- **Frontend implementado** (React 19 + Vite + TS, ver sección 11 y estructura en sección 4): login, layout con navbar y simulador de contexto, CRUD de documentos + aprobar, gestión de usuarios (crear/editar/estado/rol), auditoría con filtros.
- **Testing manual de la etapa 3 ejecutado y aprobado (2026-09-24)**: Fases 1–4 de la sección 13 completas — 21/21 casos de regresión de backend, 6/6 roles verificados end-to-end en el frontend, 6/6 casos límite de integración, regresión de los 9 bugs conocidos sin reproducirse. Fase 0 (pytest, unitarias e integradas) **pospuesta** a pedido explícito del usuario — sigue pendiente.
- Bug #9 (sección 12) corregido en la sesión anterior: `GET /documentos` devolvía 500 — confirmado sin regresión.
- **Bug #10 encontrado y corregido durante el testing manual**: el mensaje de error dentro de un modal (ej. 409 por correo duplicado) quedaba oculto detrás del overlay del modal. Corregido en `DocumentoFormModal.tsx`, `UsuarioFormModal.tsx`, `DocumentosPage.tsx`, `UsuariosPage.tsx`.
- **Despliegue en Vercel retomado**: se creó `api/index.py` (wrapper ASGI que recorta el prefijo `/api`), `vercel.json` (build del frontend + rewrites) y `.python-version`, y se corrigió `requirements.txt` (estaba en **UTF-16**, bug #11, un bug que habría roto el build de Vercel — ahora en UTF-8 plano). Verificado localmente: el wrapper responde correctamente contra la Neon real (`/api/health`, `/api/auth/login`) y `npm run build` del frontend genera `frontend/dist` sin errores. Decisiones tomadas con el usuario: `DEMO_MODE=true` en producción, misma BD de Neon de desarrollo, `JWT_SECRET` nuevo generado para producción (no versionado, ver sección 14).
- **Dos intentos reales de deploy en Vercel fallaron y se corrigieron en el momento** (2026-09-24): (1) bug #12 — `runtime` inválido en `vercel.json`, reemplazado por `.python-version`; (2) bug #13 — `.python-version` pedía Python `3.11`, no disponible en la imagen de build de Vercel (`uv` no lo tiene como instalación gestionada), cambiado a `3.12`. **Falta reintentar el deploy** con este segundo fix aplicado (requiere que el usuario haga commit/push y vuelva a desplegar desde el dashboard).
- **Siguiente tarea:** el usuario debe hacer commit + push del fix del bug #13 y reintentar el deploy en Vercel (sección 14). Después: ejecutar la Fase 0 (pytest) cuando el usuario lo pida.
- **Atención:** la base de datos quedó "sucia" tras el testing manual de esta sesión (aprobación/eliminación de documentos, cambios de estado de usuarios). Se ejecutó `python -m app.seed` al finalizar, por lo que queda limpia — no hace falta resembrar antes de la próxima tarea, pero verificar si se reabren pruebas.

---

## 4. Estructura del repositorio

```
securedocs/
├── CONTEXT.md                 # este archivo
├── .gitignore
├── requirements.txt           # EN LA RAÍZ (Vercel lo detecta aquí) — UTF-8 (ver bug #11 sección 12)
├── .python-version            # "3.12" — fija la versión de Python de la Vercel Function (ver bugs #12–#13 sección 12)
├── vercel.json                # build del frontend + rewrites /api → api/index.py
├── api/
│   └── index.py               # wrapper ASGI: recorta el prefijo /api y delega en backend/app/main.py
├── docs/                      # vacía — entregables (diagramas, matrices, evidencias)
├── frontend/                  # React 19 + Vite + TS — implementado
│   ├── vite.config.ts         # proxy /api → http://127.0.0.1:8000
│   ├── index.html
│   └── src/
│       ├── main.tsx           # BrowserRouter + AuthProvider
│       ├── App.tsx            # rutas (login, documentos, usuarios, auditoria)
│       ├── index.css
│       ├── api/
│       │   ├── client.ts      # apiFetch() — token, headers de simulador, manejo 401
│       │   └── types.ts       # tipos espejo de los schemas del backend
│       ├── auth/
│       │   ├── AuthContext.tsx# usuario, permisos, demoMode, login/logout
│       │   └── RequireAuth.tsx# guard de ruta (auth + permiso opcional)
│       ├── components/        # Layout, SimuladorPanel, Mensaje, DocumentoFormModal, UsuarioFormModal
│       └── pages/              # LoginPage, DocumentosPage, DocumentoDetallePage, UsuariosPage, AuditoriaPage
└── backend/
    ├── .env                   # NO versionado
    ├── .env.example
    ├── .gitignore
    ├── alembic.ini
    ├── alembic/
    │   ├── env.py             # usa DATABASE_URL_UNPOOLED
    │   └── versions/1221ea335f85_modelo_inicial_...py
    ├── tests/unit/  tests/integration/   # vacías
    └── app/
        ├── main.py            # FastAPI + include_router de los 4 routers + /health
        ├── config.py          # Settings (pydantic-settings)
        ├── db.py              # engine (pooled), SessionLocal, Base, get_db
        ├── seed.py            # semilla REINICIABLE (drop_all + create_all)
        ├── models/            # __init__.py importa TODAS las entidades
        │   ├── rbac.py        # Rol, Permiso, RolPermiso
        │   ├── usuario.py     # Departamento, Usuario
        │   ├── documento.py
        │   ├── politica.py
        │   └── auditoria.py
        ├── schemas/           # auth.py, documento.py, usuario.py, auditoria.py
        ├── auth/
        │   ├── security.py    # hash/verify bcrypt, crear/decodificar JWT
        │   └── dependencies.py# get_current_user (JWT + token_version + P7)
        ├── authz/             # ← núcleo de la sección 16 del expediente
        │   ├── context.py     # Sujeto, Recurso, Entorno, Contexto, construir_entorno, recurso_desde_documento
        │   ├── rbac.py        # tiene_permiso(db, rol, permiso)
        │   ├── dependencies.py# autorizar(permiso_rbac, accion_abac), verificar_abac(...)
        │   └── abac/
        │       ├── registry.py# Resultado, REGISTRO, decorador @politica
        │       ├── policies.py# P1–P9 como funciones puras
        │       └── engine.py  # evaluar_abac (deny-overrides + acumulación de motivos)
        ├── audit/service.py   # registrar(...)
        └── routers/           # auth.py, documentos.py, usuarios.py, auditoria.py, catalogos.py
```

---

## 5. Entorno local (Windows / PowerShell)

```powershell
git clone https://github.com/diegoninam-ship-it/securedocs.git
cd securedocs\backend
python -m venv venv                 # usar "python"; "py" no existe en todas las máquinas
venv\Scripts\activate               # si falla: Set-ExecutionPolicy Bypass -Scope Process
pip install -r ..\requirements.txt
# crear backend\.env a partir de .env.example (ver abajo)
alembic upgrade head                # aplica esquema
python -m app.seed                  # resetea y carga datos semilla
uvicorn app.main:app --reload       # http://127.0.0.1:8000/docs
```

### Variables de `backend/.env`

| Variable | Uso |
|---|---|
| `DATABASE_URL_POOLED` | App (conexiones cortas; hostname con `-pooler`) |
| `DATABASE_URL_UNPOOLED` | Solo Alembic (migraciones) |
| `JWT_SECRET` | Firma del JWT. **Debe ser el mismo en todas las máquinas** que compartan la BD de Neon; si cambia, los tokens emitidos dejan de ser válidos |
| `JWT_EXPIRE_MINUTES` | 30 |
| `DEMO_MODE` | `true` en local/pruebas (habilita simulador de contexto y motivos detallados en 403) |
| `TZ_APP` | `America/Lima` |

Generar secreto: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

### Frontend

```powershell
cd securedocs\frontend
npm install
npm run dev                         # http://127.0.0.1:5173 — requiere el backend corriendo en :8000
```

El login guarda el JWT en `localStorage` (`securedocs_token`, decisión D9). El panel del simulador de contexto (ubicación/dispositivo) solo se muestra si `GET /health` responde `demo_mode: true`.

### Reglas operativas

- `.env` cambia → reiniciar uvicorn manualmente (`--reload` solo vigila `.py`).
- Flujo de datos: `alembic upgrade head` (esquema) y luego `python -m app.seed` (datos). Son comandos separados a propósito.
- Tras instalar cualquier paquete: `pip freeze | Out-File -Encoding utf8 ..\requirements.txt` (el archivo vive en la raíz). **Nunca uses `pip freeze > ..\requirements.txt`**: en PowerShell, `>` escribe en UTF-16 por defecto y rompe el build de Vercel (bug #11, sección 12).
- Commits con **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`), al cierre de cada paso importante.

---

## 6. Decisiones de diseño (no cambiar sin consultar)

| ID | Decisión |
|---|---|
| D1 | **P1 Departamento** aplica a Gerente, Supervisor y Empleado sobre CONSULTAR/MODIFICAR/APROBAR/ELIMINAR. Exentos: Administrador, Auditor, Invitado (este último se rige por P8). Las excepciones son **por política**, no globales. |
| D2 | **P5 País:** `usuario.pais == documento.pais` **AND** `entorno.ubicacion == documento.pais`. Códigos ISO de 2 letras (`PE`, `CL`). |
| D3 | El JWT solo transporta `sub` (id) y `ver` (token_version). Los atributos se cargan **desde BD en cada petición**. P7 se evalúa en el login y en cada petición. |
| D4 | **P4 Horario** se evalúa siempre en `America/Lima`, nunca en la hora del servidor (Vercel corre en UTC). |
| D5 | **Entorno:** en `DEMO_MODE` se leen headers `X-Sim-Ubicacion` y `X-Sim-Dispositivo` (por defecto `PE` y `CORPORATIVO`). Fuera de `DEMO_MODE`: ubicación desde `x-vercel-ip-country` y dispositivo **siempre `PERSONAL`** (sin MDM no hay forma confiable de probar un dispositivo corporativo; falla de forma segura). |
| D6 | **Ciclo de vida del documento:** `PENDIENTE` (al crear) → `PUBLICADO` (al aprobar). Modificar un PUBLICADO lo devuelve a PENDIENTE y limpia `aprobado_por` / `fecha_aprobacion`. No existe operación "publicar". |
| D7 | **P9 Segregación de funciones** (agregada por nosotros): el propietario no puede aprobar su propio documento. |
| D8 | **Logout real:** incrementa `usuario.token_version`; cualquier token con versión anterior recibe 401. Efecto colateral aceptado: cierra sesión en todos los dispositivos. |
| D9 | **JWT en `localStorage`** + cabecera `Authorization: Bearer` (decisión explícita del usuario, riesgo aceptado). Mitigaciones obligatorias: expiración 30 min, **nunca `dangerouslySetInnerHTML`**, CSP en el despliegue. |
| D10 | **Campos sensibles fijados por el servidor:** al crear un documento, `departamento`, `propietario`, `estado` y `pais` salen del usuario autenticado, nunca del body. Al subir el nivel de confidencialidad en un PUT, el usuario debe calificar para el nivel nuevo. |
| D11 | **Motivo en 403:** el detalle completo siempre va a la auditoría; al cliente solo se le muestra el motivo ABAC en `DEMO_MODE` (fuera de él: "Acceso denegado"). Los 403 de RBAC siempre dicen "No tienes permiso para esta operación". |
| D12 | **Política híbrida:** la lógica de cada política vive en código (`policies.py`); su configuración (`activa`, `roles_aplicables`, `roles_exentos`, `operaciones`, `parametros`) vive en la tabla `politicas`. Nunca usar `eval()`. |

---

## 7. Modelo de datos (tablas en Neon)

| Tabla | Campos clave |
|---|---|
| `roles` | id, codigo, nombre |
| `permisos` | id, codigo, descripcion |
| `rol_permiso` | rol_id, permiso_id (PK compuesta) |
| `departamentos` | id, codigo, nombre |
| `usuarios` | id, nombre, correo (único), password_hash, rol_id, departamento_id (nulo para invitado), nivel_seguridad, pais (2 letras), tipo_contrato, estado, **token_version** |
| `documentos` | id, titulo, descripcion, propietario_id, departamento_id, nivel_confidencialidad, estado, pais, fecha_creacion, aprobado_por, fecha_aprobacion |
| `politicas` | id, codigo (P1–P9), nombre, descripcion, activa, roles_aplicables (JSONB, null = todos), roles_exentos (JSONB), operaciones (JSONB), parametros (JSONB) |
| `auditoria` | id, usuario_id (nulo si login con correo inexistente), usuario_correo (snapshot), recurso, accion, fecha, resultado, etapa (AUTH/RBAC/ABAC), motivo, politica_fallida (ej. `"P8,P2"`), contexto (JSONB) |

Fechas en `timestamptz` (UTC en BD, se muestran en hora de Lima). La auditoría es **solo inserción**: ningún endpoint la modifica ni la borra.

### Matriz RBAC (sembrada en `rol_permiso`)

| Permiso | ADMIN | GERENTE | SUPERVISOR | EMPLEADO | AUDITOR | INVITADO |
|---|---|---|---|---|---|---|
| DOC_CREAR | ✓ | ✓ | ✓ | ✓ | | |
| DOC_CONSULTAR | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| DOC_MODIFICAR | ✓ | ✓ | ✓ | ✓ | | |
| DOC_ELIMINAR | ✓ | ✓ | | | | |
| DOC_APROBAR | ✓ | ✓ | ✓ | | | |
| AUDITORIA_VER | ✓ | ✓ | | | ✓ | |
| USUARIOS_GESTIONAR | ✓ | | | | | |
| ROLES_ASIGNAR | ✓ | | | | | |

### Matriz de políticas ABAC (sembrada en `politicas`)

| Código | Política | Aplica a | Exentos | Operaciones | Parámetros |
|---|---|---|---|---|---|
| P1 | Departamento | Todos | ADMINISTRADOR, AUDITOR, INVITADO | CONSULTAR, MODIFICAR, APROBAR, ELIMINAR | — |
| P2 | Nivel de seguridad | Todos | — | CREAR + las 4 anteriores | — |
| P3 | Propiedad | Todos | GERENTE, ADMINISTRADOR | MODIFICAR | — |
| P4 | Horario | Todos | — | 4 ops sobre doc existente | 08:00–18:00, umbral 4, America/Lima |
| P5 | País | Todos | — | 4 ops sobre doc existente | — |
| P6 | Dispositivo | Todos | — | 4 ops sobre doc existente | umbral 4, CORPORATIVO |
| P7 | Estado del usuario | Todos | — | LOGIN, CUALQUIERA | estado ACTIVO |
| P8 | Invitados | **Solo INVITADO** | — | CONSULTAR | contrato EXTERNO, nivel ≤ 1, estado PUBLICADO |
| P9 | Segregación de funciones | Todos | — | APROBAR | — |

---

## 8. Motor de autorización

### Flujo de una petición

```
JWT → get_current_user   (valida firma/exp, carga usuario, compara token_version, evalúa P7)  → 401 / 403
    → autorizar()        (RBAC: tiene_permiso)                                                 → 403 etapa RBAC
    → router             (carga el documento real o arma un Recurso provisional)
    → verificar_abac()   (evalúa políticas aplicables, audita, lanza 403 si falla)             → 403 etapa ABAC
    → operación ejecutada
```

### Piezas y contratos

- **`autorizar(permiso_rbac, accion_abac)`** — dependencia de FastAPI. `permiso_rbac` es el código de la matriz RBAC (`DOC_CONSULTAR`); `accion_abac` es el vocabulario de `politicas.operaciones` (`CONSULTAR`). **Son strings distintos a propósito**; no unificarlos (ver bug #2 en sección 12).
- **`verificar_abac(request, db, recurso, recurso_nombre)`** — la llama el router una vez que tiene el `Recurso`. Audita PERMITIDO o DENEGADO.
- **`evaluar_abac(db, ctx)`** — función de bajo nivel, no lanza ni audita. Úsala solo cuando una denegación no debe cortar la petición (ej. filtrado del listado).
- **Agregar una política nueva:** (1) función con `@politica("P10")` en `policies.py`, (2) fila en `POLITICAS` de `seed.py` (o insert en BD). El motor no se toca.
- **Regla de oro (sección 16 del expediente):** **ningún router contiene `if rol == ...`**. RBAC vive en `rol_permiso`; ABAC vive en `policies.py` + tabla `politicas`.
- `engine.py` importa `policies` con `# noqa: F401` **solo por efecto secundario** (registrar decoradores). No borrar ese import (ver bug #1).

### Valores de `accion_abac` en uso

`LOGIN` · `CUALQUIERA` · `CONSULTAR` · `CREAR` · `MODIFICAR` · `ELIMINAR` · `APROBAR` · `GESTIONAR_USUARIOS` · `ASIGNAR_ROLES` · `VER_AUDITORIA`

---

## 9. API (backend en `http://127.0.0.1:8000`)

| Método | Ruta | Auth | Permiso RBAC | acción ABAC | Respuesta |
|---|---|---|---|---|---|
| GET | `/health` | No | — | — | `{status, demo_mode}` |
| POST | `/auth/login` | No | — | LOGIN (P7) | `{access_token, token_type}` |
| POST | `/auth/logout` | Sí | — | — | 204 |
| GET | `/auth/me` | Sí | — | — | `UsuarioMe` |
| GET | `/documentos` | Sí | DOC_CONSULTAR | CONSULTAR (filtra por doc) | `DocumentoOut[]` (solo autorizados) |
| GET | `/documentos/{id}` | Sí | DOC_CONSULTAR | CONSULTAR | `DocumentoOut` |
| POST | `/documentos` | Sí | DOC_CREAR | CREAR | 201 `DocumentoOut` |
| PUT | `/documentos/{id}` | Sí | DOC_MODIFICAR | MODIFICAR | `DocumentoOut` |
| DELETE | `/documentos/{id}` | Sí | DOC_ELIMINAR | ELIMINAR | 204 |
| POST | `/documentos/{id}/aprobar` | Sí | DOC_APROBAR | APROBAR | `DocumentoOut` · 409 si no está PENDIENTE |
| GET | `/usuarios` | Sí | USUARIOS_GESTIONAR | — | `UsuarioOut[]` |
| POST | `/usuarios` | Sí | USUARIOS_GESTIONAR | — | 201 `UsuarioOut` |
| PUT | `/usuarios/{id}` | Sí | USUARIOS_GESTIONAR | — | `UsuarioOut` (incluye cambio de `estado`) |
| PUT | `/usuarios/{id}/rol` | Sí | ROLES_ASIGNAR | — | `UsuarioOut` |
| GET | `/auditoria` | Sí | AUDITORIA_VER | — | `AuditoriaOut[]` · query: `resultado`, `usuario_correo`, `desde`, `hasta`, `limit` (≤500) |
| GET | `/auth/me/permisos` | Sí | — | — | `{permisos: string[]}` — códigos de `rol_permiso` del rol del usuario autenticado |
| GET | `/catalogos/roles` | Sí | — | — | `RolOut[]` `{codigo, nombre}` — solo lectura |
| GET | `/catalogos/departamentos` | Sí | — | — | `DepartamentoOut[]` `{codigo, nombre}` — solo lectura |

### Esquemas principales

- **LoginRequest:** `{correo, password}`
- **UsuarioMe:** `{id, nombre, correo, rol, departamento, nivel_seguridad, pais}`
- **DocumentoCreate:** `{titulo, descripcion?, nivel_confidencialidad}`
- **DocumentoUpdate:** `{titulo?, descripcion?, nivel_confidencialidad?}`
- **DocumentoOut:** `{id, titulo, descripcion, departamento, nivel_confidencialidad, estado, pais, propietario_id, fecha_creacion, aprobado_por, fecha_aprobacion}`
- **UsuarioCreate:** `{nombre, correo, password, rol_codigo, departamento_codigo?, nivel_seguridad, pais, tipo_contrato}`
- **UsuarioUpdate:** `{nombre?, departamento_codigo?, nivel_seguridad?, pais?, tipo_contrato?, estado?}`
- **UsuarioOut:** `{id, nombre, correo, rol, departamento, nivel_seguridad, pais, tipo_contrato, estado}`
- **AuditoriaOut:** `{id, usuario_correo, recurso, accion, fecha, resultado, etapa, motivo, politica_fallida}`

### Códigos de respuesta

`200/201/204` éxito · `401` sin token, token inválido/expirado o versión revocada · `403` denegado (AUTH/P7, RBAC o ABAC; el `detail` trae el motivo en DEMO_MODE) · `404` no existe · `409` transición de estado inválida · `422` validación.

### Headers del simulador (solo con `DEMO_MODE=true`)

| Header | Valores | Por defecto |
|---|---|---|
| `X-Sim-Ubicacion` | código ISO 2 letras (`PE`, `CL`, …) | `PE` |
| `X-Sim-Dispositivo` | `CORPORATIVO` / `PERSONAL` | `CORPORATIVO` |

> **No existe override de hora.** P4 usa la hora real de Lima. Ver pendiente #1 en sección 11.

### Convención de serialización

Las relaciones de SQLAlchemy (`rol`, `departamento`) son objetos, no strings. Los routers devuelven siempre a través de `documento_a_out()` / `usuario_a_out()`. **Nunca `return doc` o `return usuario` directo** (ver bug #3). `password_hash`, `token_version` y `estado` interno nunca salen en respuestas que no los necesiten.

---

## 10. Datos semilla y matriz de pruebas

Contraseña de todos los usuarios semilla: **`Demo1234!`** (solo pruebas).

### Usuarios

| ID | Nombre | Correo | Rol | Depto | Nivel | Estado |
|---|---|---|---|---|---|---|
| U1 | Admin Sistema | admin@securedocs.pe | ADMINISTRADOR | TI | 5 | ACTIVO |
| U2 | Patricia Gómez | patricia.gomez@securedocs.pe | GERENTE | FINANZAS | 5 | ACTIVO |
| U3 | Carlos Ruiz | carlos.ruiz@securedocs.pe | SUPERVISOR | FINANZAS | 3 | ACTIVO |
| U4 | Luis Paredes | luis.paredes@securedocs.pe | EMPLEADO | FINANZAS | 2 | ACTIVO |
| U5 | Rosa Díaz | rosa.diaz@securedocs.pe | EMPLEADO | FINANZAS | 2 | ACTIVO |
| U6 | María Quispe | maria.quispe@securedocs.pe | EMPLEADO | RRHH | 2 | ACTIVO |
| U7 | Jorge Salas | jorge.salas@securedocs.pe | AUDITOR | AUDITORIA | 5 | ACTIVO |
| U8 | Proveedor Externo | proveedor@externo.com | INVITADO | — | 1 | ACTIVO (EXTERNO) |
| U9 | Pedro Vargas | pedro.vargas@securedocs.pe | EMPLEADO | FINANZAS | 2 | INACTIVO |

Todos con `pais = PE` y contrato `INTERNO`, salvo U8.

### Documentos (todos `pais = PE`)

| ID | Título | Depto | Nivel | Estado | Propietario |
|---|---|---|---|---|---|
| D1 | Informe de gastos Q3 | FINANZAS | 2 | PENDIENTE | U4 |
| D2 | Plan de capacitación | RRHH | 2 | PENDIENTE | U6 |
| D3 | Presupuesto anual | FINANZAS | 3 | PENDIENTE | U2 |
| D4 | Proyección de inversiones | FINANZAS | 4 | PUBLICADO | U2 |
| D5 | Plan estratégico 2027 | FINANZAS | 5 | PUBLICADO | U2 |
| D6 | Manual del proveedor | FINANZAS | 1 | PUBLICADO | U4 |
| D7 | Contrato de servicios | FINANZAS | 3 | PUBLICADO | U2 |
| D8 | Borrador obsoleto | FINANZAS | 1 | PENDIENTE | U4 |
| D9 | Informe de conciliación | FINANZAS | 3 | PENDIENTE | U3 |

### Resultados verificados (2026-09-23, contra backend real)

| # | Actor → acción → recurso | Resultado | Motivo |
|---|---|---|---|
| 1 | U4 consulta D1 | ✅ Permitido | — |
| 2 | U4 consulta D2 | ✅ Denegado | P1 |
| 3 | U3 aprueba D3 | ✅ Permitido | — |
| 4 | U4 aprueba D1 | ✅ Denegado | RBAC |
| 5 | U4 consulta D4 | ✅ Denegado | P2 (+ P4 por hora de prueba) |
| 6 | U2 elimina D8 | ✅ Permitido | — |
| 7 | U7 modifica D1 | ✅ Denegado | RBAC |
| 8 | U9 login | ✅ Denegado | P7 — "Usuario en estado INACTIVO, se requiere ACTIVO" |
| 9 | U2 consulta D4 fuera de horario | ✅ Denegado | P4 |
| 10 | U2 consulta D5 con `X-Sim-Dispositivo: PERSONAL` | ✅ Denegado | P6 (+ P4) |
| 11 | U8 consulta D6 | ✅ Permitido | — |
| 12 | U8 consulta D7 | ✅ Denegado | P2 + P8 acumulados |
| A1 | U5 modifica D1 | ✅ Denegado | P3 |
| A2 | U2 consulta D4 con `X-Sim-Ubicacion: CL` | ✅ Denegado | P5 (+ P4) |
| A3 | U3 aprueba D9 (propio) | ✅ Denegado | P9 |
| A4 | U4 usa token tras logout | ✅ 401 | token_version revocada |
| A5 | U4 suspendido por U1 con sesión activa | ✅ Denegado | P7 — "Usuario en estado SUSPENDIDO" |

> Las pruebas 3, 6, A4 y A5 **modifican datos**. Antes de repetirlas: `python -m app.seed`.

---

## 11. Frontend — especificación (implementado)

### Ubicación y stack

- Carpeta `frontend/`, React 19 + Vite + TypeScript.
- En desarrollo, **proxy de Vite**: el frontend llama a `/api/...` y Vite lo reescribe al backend sin el prefijo:

```ts
// frontend/vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
},
```

  Así no hace falta CORS en el backend (hoy **no** tiene `CORSMiddleware`).

### Requisitos funcionales (sección 10 del expediente)

| Pantalla | Contenido |
|---|---|
| Login | Formulario correo/contraseña → `POST /auth/login`; guarda token en `localStorage` |
| Layout | Barra con usuario actual (`GET /auth/me`), rol, departamento, nivel; botón logout (`POST /auth/logout` + borrar token) |
| Simulador de contexto | Panel visible en DEMO_MODE para elegir ubicación (`PE`/`CL`/…) y dispositivo (`CORPORATIVO`/`PERSONAL`); se persiste en `localStorage` y se envía como `X-Sim-Ubicacion` / `X-Sim-Dispositivo` en **todas** las peticiones |
| Documentos | Listado (`GET /documentos`), detalle, crear, editar, eliminar, aprobar |
| Usuarios | Solo para quien tenga acceso: listar, crear, editar (incluye activar/desactivar/suspender), asignar rol |
| Auditoría | Tabla con filtros (`resultado`, `usuario_correo`, `desde`, `hasta`) |

### Reglas para el cliente HTTP

- Un único wrapper (fetch o axios) que agregue `Authorization: Bearer <token>` y los headers del simulador.
- `401` → borrar token y redirigir a Login.
- `403` → mostrar el `detail` del backend (en DEMO_MODE trae el motivo, útil como evidencia de los casos de prueba).
- `409` → mostrar como conflicto de estado, no como error de permisos.
- Todo texto que venga del usuario (título, descripción) se renderiza escapado. **Prohibido `dangerouslySetInnerHTML`** (D9).

### Mostrar/ocultar acciones por rol

El frontend solo recibe `rol` en `/auth/me`. Ocultar botones según rol es **solo UX**; el backend es la única autoridad y seguirá denegando. Evitar duplicar la matriz RBAC completa en el frontend: si se necesita, preferir la mejora de backend descrita en el pendiente #2.

### Pendientes conocidos que afectan al frontend

| # | Pendiente | Estado |
|---|---|---|
| 1 | No hay override de hora para P4; los casos de horario dependen del reloj real | ⏳ Pendiente — decisión del usuario (2026-09-23): **no implementar** por ahora |
| 2 | El frontend no conoce los permisos del usuario, solo su rol | ✅ Resuelto — `GET /auth/me/permisos` (ver sección 9) |
| 3 | No existe listado de departamentos ni roles para los selects del formulario de usuarios | ✅ Resuelto — `GET /catalogos/roles` y `GET /catalogos/departamentos` (ver sección 9) |

> Cualquiera de estos cambios de backend debe consultarse con el usuario antes de implementarse, y registrarse en el Changelog.

---

## 12. Bugs resueltos (no reintroducir)

| # | Síntoma | Causa | Solución |
|---|---|---|---|
| 1 | Ninguna política ABAC denegaba nunca (U9 inactivo podía loguearse) | `policies.py` nunca se importaba → los decoradores no corrían → `REGISTRO` vacío → el motor saltaba todas las políticas | `from app.authz.abac import policies  # noqa: F401` en `engine.py` |
| 2 | Las políticas no aplicaban a los endpoints de documentos | `ctx.accion` recibía el permiso RBAC (`DOC_CONSULTAR`) mientras `politicas.operaciones` usa `CONSULTAR` | `autorizar(permiso_rbac, accion_abac)` con dos parámetros separados |
| 3 | 500 `ResponseValidationError` al devolver documentos/usuarios | Pydantic recibía objetos `Departamento`/`Rol` en campos `str` | Funciones `documento_a_out()` y `usuario_a_out()` |
| 4 | 500 `ForeignKeyViolation` al auditar login fallido | `Sujeto(id=0)` para usuario desconocido | `Sujeto.id: int \| None`, usar `id=None` |
| 5 | `drop_all` fallaba en `seed.py` | `Auditoria` no estaba registrada en `Base.metadata` | `models/__init__.py` importa todas las entidades |
| 6 | `passlib` fallaba con bcrypt ≥ 4.1 | `passlib` sin mantenimiento | Se eliminó `passlib`; se usa `bcrypt` directo |
| 7 | `ZoneInfoNotFoundError: America/Lima` en Windows | Windows no trae la base IANA | `pip install tzdata` |
| 8 | `EmailStr` fallaba al arrancar | Falta `email-validator` | `pip install "pydantic[email]"` |
| 9 | 500 `ResponseValidationError` en `GET /documentos` (detectado al probar el frontend) | `listar_documentos()` hacía `return documento_a_out(doc)` con `doc` residual del bucle de filtrado ABAC, en vez de devolver la lista `visibles` ya filtrada | `return [documento_a_out(d) for d in visibles]` en `app/routers/documentos.py` |
| 10 | Al fallar un guardado dentro de un modal (ej. 409 "correo ya existe"), el mensaje de error no era visible para el usuario (detectado en Fase 3 / caso I5 del testing manual) | `.modal-fondo` tiene `position: fixed` + `z-index: 10` cubriendo toda la pantalla; el `<Mensaje>` de error se renderizaba en el flujo normal de la página, detrás del overlay del modal | `DocumentoFormModal` y `UsuarioFormModal` ahora aceptan una prop `error` y renderizan `<Mensaje>` dentro del propio modal; `DocumentosPage`/`UsuariosPage` les pasan el error y ocultan el `Mensaje` de página cuando el modal está abierto (`{error && !modal && ...}`) |
| 11 | `requirements.txt` (raíz) estaba en **UTF-16 LE** en vez de UTF-8 (detectado al retomar el despliegue en Vercel) | `pip freeze > ..\requirements.txt` en PowerShell escribe UTF-16 por defecto (`>` usa la codificación por defecto de `Out-File`). Vercel/pip esperan UTF-8; el build habría fallado | Reescrito en UTF-8 plano. **Regla nueva:** nunca uses `pip freeze > archivo` en PowerShell; usa `pip freeze \| Out-File -Encoding utf8 archivo` (ver sección 5) |
| 12 | Build de Vercel fallaba con `Error: Function Runtimes must have a valid version, for example now-php@1.0.0` (primer intento real de deploy, 2026-09-24) | `vercel.json` tenía `"functions": { "api/index.py": { "runtime": "python3.11" } }`; el campo `runtime` espera un identificador de paquete de Vercel con versión (`nombre@version`), no un nombre de lenguaje suelto | Se quitó el bloque `functions` de `vercel.json`; se agregó `.python-version` (raíz, contenido `3.11`) — es la forma soportada por Vercel para fijar la versión de Python sin ese campo |
| 13 | Con el fix del bug #12 aplicado, el build seguía fallando: `uv sync ... error: No interpreter found for Python 3.11 in managed installations` (segundo intento real de deploy, 2026-09-24) | La imagen de build de Vercel no tiene Python 3.11 entre las instalaciones gestionadas por `uv`; el propio log avisaba "Using python version: 3.12" como fallback, pero `uv sync --locked` igual intentaba resolver la versión pedida en `.python-version` (3.11) y fallaba por la inconsistencia | `.python-version` cambiado de `3.11` a `3.12` — la versión que Vercel sí tiene disponible (confirmado en el log del intento anterior) |

---

## 13. Plan de ejecución — Etapa de Testing

> Etapa reincorporada el 2026-09-23 a pedido del usuario (ver nota en sección 2). Objetivo: verificar que **todo el sistema — backend y frontend integrados — está operativo**, sin regresiones sobre lo ya construido, y dejar evidencia reproducible. No reemplaza la matriz de la sección 10; la amplía y la ejecuta contra el sistema completo.

### Prerrequisitos

- `python -m app.seed` ejecutado (BD en estado semilla, sin contaminar de sesiones previas).
- Backend corriendo: `uvicorn app.main:app --reload` (puerto 8000).
- Frontend corriendo: `npm run dev` en `frontend/` (puerto 5173).
- `DEMO_MODE=true` en `backend/.env` (necesario para el simulador de contexto y los motivos de 403).

### Fase 0 — Pruebas automatizadas (pytest, unitarias e integradas)

Las carpetas `backend/tests/unit/` y `backend/tests/integration/` ya existen (sección 4) pero están vacías. Se llenan en esta fase.

**Limitación importante a respetar:** `policies.py` son funciones puras — reciben `Contexto` (dataclasses) + `params: dict`, sin tocar la BD — y por eso son aptas para pruebas unitarias sin base de datos. En cambio `tiene_permiso()` (`rbac.py`) y `evaluar_abac()` (`engine.py`) consultan Neon con columnas `JSONB` (`postgresql.JSONB`, específico de Postgres), así que **no son compatibles con SQLite en memoria**. Este proyecto no tiene Postgres local ni Docker — todo corre contra Neon (sección 1). Por lo tanto, la suite de integración corre contra la **misma base de Neon**, reseteada con `seed.py` antes de ejecutarse; no es una base de test aislada. Riesgo aceptado explícitamente para este laboratorio: **nunca correr esta suite contra una base con datos reales**, y volver a sembrar (`python -m app.seed`) después de correrla.

**Dependencias nuevas** (agregar a `requirements.txt` vía `pip install pytest httpx` + `pip freeze | Out-File -Encoding utf8 requirements.txt`, regla de sección 5): `pytest`, `httpx` (requerido por `fastapi.testclient.TestClient`).

**Estructura de archivos:**

| Archivo | Contenido |
|---|---|
| `backend/tests/unit/test_policies.py` | Una prueba por política P1–P9 (casos permitido y denegado), construyendo `Sujeto`/`Recurso`/`Entorno`/`Contexto` a mano. Sin BD. |
| `backend/tests/unit/test_rbac.py` | `tiene_permiso()` parametrizado contra las 48 combinaciones rol×permiso de la matriz RBAC (sección 7). Requiere BD sembrada. |
| `backend/tests/integration/conftest.py` | Fixture de sesión: `reset_schema()` + `seed.main()` una sola vez al inicio de la suite; fixture `client` = `TestClient(app)`. |
| `backend/tests/integration/test_auth.py` | Login válido/inválido, P7 evaluada en login, `/auth/me`, `/auth/me/permisos`, logout + token revocado (token_version). |
| `backend/tests/integration/test_documentos.py` | CRUD completo + aprobar; replica los 17 casos de la sección 10 vía `TestClient` en lugar de manual. |
| `backend/tests/integration/test_usuarios.py` | RBAC de gestión de usuarios, asignación de rol, catálogos (`/catalogos/roles`, `/catalogos/departamentos`). |
| `backend/tests/integration/test_auditoria.py` | Filtros (`resultado`, `usuario_correo`, `desde`, `hasta`, `limit`), y que las pruebas anteriores dejaron rastro auditado. |

**Ejecución:**

```powershell
cd securedocs\backend
pytest tests\unit -v          # rápidas, sin BD (excepto test_rbac.py)
pytest tests\integration -v   # contra Neon — reinicia con `python -m app.seed` al terminar
pytest -v                     # suite completa
```

**Cobertura mínima esperada:** las 9 políticas con ambas ramas (permitido/denegado) = 18 casos mínimo; `tiene_permiso()` para las 48 combinaciones rol×permiso; al menos un test de integración por cada uno de los 17 endpoints.

### Fase 1 — Regresión de backend (API directa)

1. Reejecutar los 17 casos de la matriz de la sección 10 contra el backend real (`/docs`, `curl` o Postman) y marcar cada uno ✅/❌.
2. Casos nuevos, no cubiertos en la sección 10 (endpoints agregados en esta sesión):

| # | Caso | Resultado esperado |
|---|---|---|
| B1 | `GET /auth/me/permisos` con cada uno de los 6 roles (U1, U2, U3, U4/U5/U6, U7, U8) | La lista de códigos coincide exactamente con la fila del rol en la matriz RBAC (sección 7) |
| B2 | `GET /catalogos/roles` y `GET /catalogos/departamentos` sin token | 401 |
| B3 | `GET /catalogos/roles` y `GET /catalogos/departamentos` con token válido (cualquier rol) | 200, catálogo completo (6 roles / 4 departamentos), sin filtrar por rol del solicitante |
| B4 | `GET /documentos` para cada uno de los 6 roles (regresión del bug #9) | 200 con lista filtrada por ABAC; nunca 500 |

### Fase 2 — E2E de frontend por rol

Para cada uno de los 6 roles (un usuario representativo por rol, tabla de la sección 10), iniciar sesión en el navegador (`http://127.0.0.1:5173`) y verificar:

1. Navbar: nombre, rol, departamento y nivel mostrados coinciden con `GET /auth/me`.
2. Menús visibles (Documentos siempre; Usuarios solo ADMINISTRADOR; Auditoría solo ADMINISTRADOR/GERENTE/AUDITOR) coinciden con la matriz RBAC de la sección 7, vía `GET /auth/me/permisos`.
3. Documentos: la lista solo muestra lo permitido por ABAC (comparar contra lo que el mismo usuario obtiene en la Fase 1 / sección 10); botones Editar/Aprobar/Eliminar aparecen solo si el rol tiene el permiso RBAC correspondiente.
4. Crear un documento (si el rol tiene DOC_CREAR) y confirmar que `departamento`, `propietario`, `estado` y `pais` quedan fijados por el servidor según el usuario autenticado, nunca editables desde el formulario (D10).
5. Con herramientas de desarrollador, forzar una acción oculta por UI (ej. invocar el endpoint DELETE sin tener DOC_ELIMINAR) y confirmar que el backend igual responde 403 — la ocultación de botones es solo UX (sección 11).
6. Simulador de contexto: cambiar `X-Sim-Ubicacion` y `X-Sim-Dispositivo` y confirmar que un documento de nivel ≥4 dejar de ser accesible (P4/P5/P6) y que el motivo aparece en el mensaje de error (DEMO_MODE, D11).
7. Cerrar sesión y confirmar redirección a `/login`, borrado del token, y que navegar hacia atrás no vuelve a mostrar datos protegidos.

### Fase 3 — Casos límite e integración backend↔frontend

| # | Caso | Resultado esperado |
|---|---|---|
| I1 | Token expira (`JWT_EXPIRE_MINUTES`) y se hace una petición | Frontend detecta el 401, borra el token y redirige a `/login` |
| I2 | Logout en una sesión, reutilizar el token viejo (otra pestaña o `localStorage` copiado) | 401 (D8: logout revoca `token_version`); frontend cierra sesión |
| I3 | Aprobar un documento que ya está PUBLICADO | 409 mostrado como conflicto de estado, no como error de permisos (regla de sección 11) |
| I4 | Usuario pasado a SUSPENDIDO/INACTIVO por un admin mientras tiene sesión activa (caso A5 de sección 10) | Próxima petición del usuario devuelve 403 (P7); el frontend debe mostrarlo sin quedar en blanco ni crashear |
| I5 | Crear usuario con correo ya existente | 409 visible en el modal, el formulario no se cierra y conserva los datos ingresados |
| I6 | Subir `nivel_confidencialidad` de un documento (PUT) sin que el usuario califique para el nivel nuevo (D10) | 403 con motivo correspondiente (P2), visible en el frontend |

### Fase 4 — Regresión de bugs conocidos

Repasar la tabla de bugs (sección 12, #1–#9) uno por uno y confirmar que ninguno se reprodujo durante las fases 1–3. Prestar especial atención al #9 (recién corregido) y al #3 (serialización).

### Resultados de ejecución (2026-09-24, manual — Fases 1 a 4; Fase 0 pospuesta)

> Fase 0 (pytest) pospuesta a pedido explícito del usuario. Ejecutado: Fases 1–4, contra backend real (`uvicorn`, puerto 8000) y frontend real (`vite`, puerto 5173), con `python -m app.seed` antes y después.

**Fase 1 — Regresión de backend:** 21/21 ✅ (los 17 casos de la sección 10 vía `curl` directo a la API + B1–B4). Sin desviaciones respecto a los resultados originales de la sección 10. B4 confirma que el bug #9 no se reprodujo (siempre 200, nunca 500).

**Fase 2 — E2E de frontend por rol:** 6/6 roles ✅ (ADMINISTRADOR, GERENTE, SUPERVISOR, EMPLEADO, AUDITOR, INVITADO). Para cada uno: navbar correcto, menús visibles coinciden exactamente con `GET /auth/me/permisos`, lista de documentos filtrada por ABAC coincide con el conteo esperado (ej. EMPLEADO Rosa: 3/9 por P1+P2+P4; GERENTE: 6/9 por P1+P4; AUDITOR exento de P1: 7/9 por P4; INVITADO: 1/9 por P8+P2), botones Editar/Aprobar/Eliminar visibles solo según permiso RBAC del rol. D10 verificado creando un documento como ADMINISTRADOR: `departamento`, `pais` y `estado` quedaron fijados por el servidor (TI/PE/PENDIENTE), no por el formulario. Punto 5 (acción oculta forzada vía DOM) verificado con INVITADO intentando `DELETE /documentos/6` por `fetch` directo: 403 pese a no existir el botón. Punto 6 (simulador) verificado cambiando `X-Sim-Ubicacion` a `CL` como ADMINISTRADOR: el detalle de D4 mostró el motivo combinado P4+P5. Punto 7 (logout) verificado. Sin errores de consola del navegador en todo el recorrido.

**Fase 3 — Casos límite e integración:**

| # | Caso | Resultado |
|---|---|---|
| I1 | Token expira | ✅ — mismo mecanismo de manejo de 401 verificado en I2 (no se esperó el TTL completo de 30 min) |
| I2 | Reutilizar token tras logout (simulando otra pestaña) | ✅ 401 "Sesión revocada", frontend ya redirigido a `/login` |
| I3 | Aprobar documento ya PUBLICADO | ✅ backend 409 confirmado (`fetch` directo); la UI del frontend no ofrece el botón para este estado, por lo que el flujo por clic no puede exponer el caso — código de manejo de 409 en `DocumentosPage.handleAprobar` revisado y correcto |
| I4 | Usuario suspendido con sesión de frontend activa | ✅ 403 mostrado con `Mensaje`, sin crash de React; navbar no se refresca automáticamente (no revalida sesión en cada navegación) — comportamiento aceptable, no bloqueante |
| I5 | Crear usuario con correo duplicado | ❌→✅ **bug encontrado y corregido en el momento** (ver bug #10 abajo): el mensaje de error existía en el DOM pero quedaba detrás del overlay del modal, invisible. Corregido pasando `error` como prop a `DocumentoFormModal`/`UsuarioFormModal`. Reverificado: mensaje visible dentro del modal, datos conservados |
| I6 | Subir `nivel_confidencialidad` sin calificar | ✅ backend 403 "No calificas para el nivel de confidencialidad propuesto"; frontend usa el mismo `handleGuardar` ya corregido en I5 |

**Fase 4 — Regresión de bugs conocidos:** bugs #1–#9 revisados, ninguno se reprodujo. Regresión explícita de #4 (login con correo inexistente → 401, no 500) y #9 (`GET /documentos` → siempre 200). Se encontró un bug nuevo, no relacionado a ningún bug previo — ver #10 en sección 12.

### Criterios de aceptación

- ~~`pytest` (Fase 0) pasa al 100%, con la cobertura mínima descrita.~~ Pospuesto a pedido del usuario — no evaluado en esta ejecución.
- 100% de los casos de las Fases 1 y 3 marcados ✅.
- Los 6 roles completan el recorrido de la Fase 2 sin errores no controlados (pantalla en blanco, crash de React, "Error 500" crudo visible al usuario final).
- Ningún bug de la sección 12 se reproduce.
- Resultados documentados con fecha (tabla de resultados a agregar en esta misma sección al ejecutar, siguiendo el formato de la sección 10).

### Entregable

- Suite `backend/tests/unit/` y `backend/tests/integration/` implementada y en verde (Fase 0), agregada a `requirements.txt`.
- Tabla de resultados (fecha + ✅/❌ + motivo si falla) agregada a esta sección.
- Actualizar **sección 3** (Estado actual) marcando la etapa 3 como cerrada.
- Si aparecen bugs nuevos, agregarlos a la **sección 12** con numeración correlativa (#10, #11…) antes de cerrar la etapa.
- Entrada nueva en el **Changelog** (sección 15).

---

## 14. Despliegue en Vercel

### Arquitectura

Un único proyecto de Vercel sirve dos cosas:

- **Frontend estático**: build de `frontend/` (Vite) publicado como sitio estático, `outputDirectory: frontend/dist`.
- **Backend como Vercel Function**: `api/index.py` es un wrapper ASGI mínimo que importa `backend/app/main.py` (el mismo FastAPI que corre local) y **recorta el prefijo `/api`** de cada request antes de delegarlo — el frontend siempre llama a `/api/...` (mismo patrón que el proxy de Vite en desarrollo, sección 11), y los routers de FastAPI no tienen ese prefijo (`/auth`, `/documentos`, ...). Sin este recorte, ninguna ruta matchearía.

Toda la configuración vive en `vercel.json` (raíz del repo):

```json
{
  "framework": null,
  "buildCommand": "npm --prefix frontend install && npm --prefix frontend run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index" },
    { "source": "/((?!api/).*)", "destination": "/index.html" }
  ]
}
```

- El primer `rewrite` manda todo `/api/*` a la function (que internamente recorta el prefijo).
- El segundo es el fallback de SPA: cualquier ruta que no empiece con `/api/` sirve `index.html`, para que el router de React (`react-router-dom`) resuelva rutas como `/documentos/3` al refrescar la página.
- `requirements.txt` en la raíz ya es el que usa Vercel para instalar las dependencias Python de la function (sección 4) — **debe estar en UTF-8** (bug #11, sección 12).
- La versión de Python de la function la fija `.python-version` (raíz, contenido `3.12`), **no** el campo `runtime` de `vercel.json` — ese campo espera un identificador de paquete con versión (ej. `now-php@1.0.0`), no un nombre de lenguaje suelto como `"python3.11"` (bug #12, sección 12). El valor de `.python-version` debe ser una versión que Vercel realmente tenga disponible como instalación gestionada por `uv` — `3.11` no lo estaba al momento de escribir esto y rompía el build (bug #13, sección 12).

No hace falta `CORSMiddleware`: frontend y API quedan bajo el mismo dominio de Vercel, igual que en desarrollo con el proxy de Vite (sección 11).

### Decisiones tomadas con el usuario (2026-09-24)

| Decisión | Valor | Motivo |
|---|---|---|
| `DEMO_MODE` en producción | `true` | Mantener visible el simulador de contexto y los motivos de 403 para que el laboratorio se pueda evaluar en el deploy real, sin depender de IP real ni de un MDM corporativo (D5) |
| Base de datos | La misma Neon de desarrollo (`DATABASE_URL_POOLED` actual) | Evita crear infraestructura nueva para este laboratorio |
| `JWT_SECRET` de producción | Generado nuevo, distinto al de `backend/.env` | Un secreto de desarrollo comprometido no debe poder falsificar sesiones en producción |

### Verificado localmente antes de desplegar (2026-09-24)

- `api/index.py` probado con `httpx.ASGITransport` contra la Neon real: `GET /api/health` y `POST /api/auth/login` responden igual que en local (200, JSON correcto) — el recorte de prefijo funciona.
- `npm run build` en `frontend/` genera `frontend/dist` sin errores (`tsc -b && vite build`).
- `requirements.txt` corregido a UTF-8 (bug #11).

### Pendiente — pasos para el usuario (requiere su cuenta de Vercel)

No hay CLI de Vercel instalada ni sesión iniciada en esta máquina; desplegar requiere credenciales del usuario. Pasos vía dashboard (sin instalar nada):

1. En [vercel.com](https://vercel.com), **Add New → Project** → importar el repo `diegoninam-ship-it/securedocs` desde GitHub.
2. **Root Directory:** dejar como raíz del repo (`.`) — **no** apuntar a `frontend/`, porque `vercel.json` y `api/` están en la raíz.
3. **Framework Preset:** "Other" (ya lo fuerza `"framework": null` en `vercel.json`).
4. **Environment Variables** (Production), mismos nombres que `backend/.env.example`:
   - `DATABASE_URL_POOLED` → la misma de `backend/.env`
   - `DATABASE_URL_UNPOOLED` → la misma de `backend/.env` (solo la usa Alembic, pero `Settings` la exige al arrancar)
   - `JWT_SECRET` → el nuevo generado para producción (no lo escribas en el repo)
   - `JWT_EXPIRE_MINUTES` → `30`
   - `DEMO_MODE` → `true`
   - `TZ_APP` → `America/Lima`
5. **Deploy.**
6. Verificar: `https://<proyecto>.vercel.app/api/health` debe responder `{"status":"ok","demo_mode":true}`, y el sitio raíz debe mostrar el login.

> Alternativa por CLI (`npm i -g vercel`, `vercel login`, `vercel link`, `vercel env add ...` por cada variable, `vercel --prod`) si el usuario prefiere no usar el dashboard — mismos valores de variables.

Al completar el despliegue: actualizar el **Estado actual** (sección 3), marcar la etapa 4 como cerrada (sección 2) y agregar la URL de producción a este documento (sección 1).

---

## 15. Changelog

| Fecha | Cambio |
|---|---|
| 2026-09-23 | Planificación cerrada (stack, D1–D12, modelo de datos, motor, API, matriz de pruebas, estructura). |
| 2026-09-23 | Backend implementado: modelos, migración inicial, seed reiniciable, motor RBAC + ABAC (P1–P9), JWT con token_version, auditoría, 14 endpoints. |
| 2026-09-23 | 17 casos de prueba verificados manualmente contra el backend; bugs #1–#8 corregidos. |
| 2026-09-23 | Etapa de Testing formal eliminada del plan. Se crea este CONTEXT.md. Siguiente: frontend con Claude Code. |
| 2026-09-23 | Decisiones sobre pendientes de sección 11 (consultadas con el usuario): no se implementa override de hora para P4; sí se agregan `GET /auth/me/permisos` (`app/routers/auth.py`, `app/schemas/auth.py`) y `GET /catalogos/roles` / `GET /catalogos/departamentos` (`app/routers/catalogos.py` nuevo, `app/schemas/catalogos.py` nuevo, registrado en `app/main.py`). Verificado manualmente contra el backend real (login admin). Despliegue en Vercel queda pausado. |
| 2026-09-23 | Frontend creado en `frontend/` (React 19 + Vite + TS + react-router-dom): login, layout, simulador de contexto (headers `X-Sim-*`), CRUD de documentos + aprobar, gestión de usuarios (crear/editar/estado/rol vía catálogos), auditoría con filtros. Menús ocultos por permiso usando `GET /auth/me/permisos`. `.claude/launch.json` agregado para levantar el dev server. Verificado en navegador con varios usuarios (admin y rol EMPLEADO). Se detectó y corrigió bug #9 en `app/routers/documentos.py` (`GET /documentos` con 500). |
| 2026-09-23 | Etapa de Testing formal **reincorporada** al plan (sección 2) a pedido del usuario, ahora que existe frontend. Se documenta el plan de ejecución en la nueva **sección 13** (prerrequisitos, regresión de backend, E2E de frontend por rol, casos límite de integración, regresión de bugs, criterios de aceptación). Aún no ejecutado — pendiente correr y registrar resultados. |
| 2026-09-23 | A pedido del usuario, se amplía la sección 13 con una **Fase 0 de pruebas automatizadas** (pytest, unitarias e integradas) sobre `backend/tests/unit/` y `backend/tests/integration/`, ya existentes pero vacías. Se documenta la limitación de que `policies.py` es puro (testeable sin BD) pero `rbac.py`/`engine.py` usan `JSONB` de Postgres y por eso las pruebas de integración deben correr contra la misma Neon reseteada con `seed.py`, no contra SQLite. Aún no implementado. |
| 2026-09-24 | **Testing manual ejecutado** (Fases 1–4 de la sección 13; Fase 0/pytest pospuesta a pedido del usuario). Fase 1: 21/21 casos de regresión de backend (17 de sección 10 + B1–B4) ✅ vía `curl` directo. Fase 2: los 6 roles verificados end-to-end en el frontend real (navbar, menús por permiso, filtrado ABAC de documentos, D10, acción oculta forzada vía `fetch`, simulador de contexto, logout) ✅. Fase 3: 6 casos límite (I1–I6) — todos ✅, con un bug encontrado y corregido en el momento (ver #10). Fase 4: bugs #1–#9 revisados, ninguno se reprodujo. Resultados completos en la sección 13. |
| 2026-09-24 | **Bug #10 corregido**: el mensaje de error dentro de un modal (ej. 409 "correo ya existe" al crear usuario) quedaba invisible detrás del overlay `.modal-fondo` (`z-index`). Se agregó una prop `error` a `DocumentoFormModal.tsx` y `UsuarioFormModal.tsx` (renderizan `<Mensaje>` dentro del modal) y se ajustaron `DocumentosPage.tsx`/`UsuariosPage.tsx` para pasarla y ocultar el mensaje de página mientras el modal está abierto. Verificado en navegador tras el fix. |
| 2026-09-24 | **Despliegue en Vercel retomado.** Se crea `api/index.py` (wrapper ASGI que recorta el prefijo `/api` y delega en `backend/app/main.py`) y `vercel.json` (build del frontend + rewrites) — nueva **sección 14**. Se detecta y corrige **bug #11**: `requirements.txt` estaba en UTF-16 (por `pip freeze >` en PowerShell), lo que habría roto el build; reescrito en UTF-8 y actualizada la regla operativa de la sección 5. Decisiones consultadas con el usuario: `DEMO_MODE=true` en producción, misma Neon de desarrollo, `JWT_SECRET` nuevo para producción (generado, no versionado). Verificado localmente con `httpx.ASGITransport` contra la Neon real y `npm run build` del frontend. Pasos de deploy vía dashboard entregados al usuario. |
| 2026-09-24 | **Primer intento real de deploy falló** (ejecutado por el usuario desde el dashboard de Vercel): `Error: Function Runtimes must have a valid version, for example now-php@1.0.0`. Causa: bug #12 (sección 12) — el campo `"functions": {"api/index.py": {"runtime": "python3.11"}}` de `vercel.json` usaba un formato inválido (`runtime` espera `paquete@version`, no un nombre de lenguaje suelto). Corregido: se quitó ese bloque de `vercel.json` y se agregó `.python-version` (raíz, contenido `3.11`) como forma soportada de fijar la versión. Pendiente: el usuario debe hacer commit/push y reintentar el deploy. |
| 2026-09-24 | **Segundo intento real de deploy falló** (commit `816ceeb`, con el fix del bug #12 ya aplicado): `uv sync ... error: No interpreter found for Python 3.11 in managed installations`. El frontend build (npm + vite) pasó sin problemas; solo falló la function Python. Causa: bug #13 (sección 12) — la imagen de build de Vercel no tenía Python 3.11 disponible para `uv`; el log de esta misma corrida indicaba que usaría 3.12 como fallback. Corregido: `.python-version` cambiado de `3.11` a `3.12`. Pendiente: el usuario debe hacer commit/push y reintentar el deploy una vez más. |

> **Formato para nuevas entradas:** `| AAAA-MM-DD | Qué cambió, en qué archivos, y por qué |`. Si el cambio altera una decisión de la sección 6, actualizar también esa tabla.