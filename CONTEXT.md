# CONTEXT.md — SecureDocs

> **Para cualquier agente (Claude Code u otro):** lee este archivo completo antes de iniciar cualquier tarea. Es la fuente de verdad del proyecto. Al terminar cada tarea, actualiza la sección **3. Estado actual** y agrega una entrada en **13. Changelog**. Si una decisión de este archivo entra en conflicto con lo que te pidan, detente y consúltalo con el usuario antes de cambiarla.

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
| Frontend | React 19 + Vite + TypeScript (**pendiente**, carpeta `frontend/` vacía) |
| Despliegue | Vercel, proyecto único: frontend estático + FastAPI como Vercel Function en `api/` (**pendiente, opcional**) |

---

## 2. Etapas del proyecto

| # | Etapa | Estado |
|---|---|---|
| 1 | Planificación | ✅ Cerrada |
| 2 | Desarrollo | 🟡 Backend ✅ · Frontend ⏳ |
| 3 | Despliegue en Vercel (opcional) | ⏳ Pendiente |

> La etapa de *Testing* formal fue **eliminada** del plan. Los 17 casos de la matriz (sección 10) ya se verificaron manualmente contra el backend real durante Desarrollo.

---

## 3. Estado actual

**Última actualización:** 2026-09-23

- Backend completo: 14 endpoints, motor RBAC + ABAC (P1–P9), autenticación JWT con `token_version`, auditoría.
- Los 17 casos de prueba verificados contra el sistema real (ver sección 10).
- **Siguiente tarea:** construir el frontend en `frontend/` (ver sección 11).
- **Atención:** la base de datos quedó "sucia" tras las pruebas (D3 publicado, D8 eliminado, Luis suspendido). Ejecutar `python -m app.seed` antes de trabajar (ver sección 5).

---

## 4. Estructura del repositorio

```
securedocs/
├── CONTEXT.md                 # este archivo
├── .gitignore
├── requirements.txt           # EN LA RAÍZ (Vercel lo detecta aquí)
├── api/                       # vacía — pendiente api/index.py para Vercel
├── docs/                      # vacía — entregables (diagramas, matrices, evidencias)
├── frontend/                  # vacía — PENDIENTE
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
        └── routers/           # auth.py, documentos.py, usuarios.py, auditoria.py
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

### Reglas operativas

- `.env` cambia → reiniciar uvicorn manualmente (`--reload` solo vigila `.py`).
- Flujo de datos: `alembic upgrade head` (esquema) y luego `python -m app.seed` (datos). Son comandos separados a propósito.
- Tras instalar cualquier paquete: `pip freeze > ..\requirements.txt` (el archivo vive en la raíz).
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

## 11. Frontend — especificación (PENDIENTE)

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

| # | Pendiente | Propuesta |
|---|---|---|
| 1 | No hay override de hora para P4; los casos de horario dependen del reloj real | Agregar en `construir_entorno()` un header `X-Sim-Hora` (`HH:MM`) respetado solo en DEMO_MODE, y un selector de hora en el simulador |
| 2 | El frontend no conoce los permisos del usuario, solo su rol | Endpoint `GET /auth/me/permisos` que devuelva los códigos de `rol_permiso` del usuario (mantiene la matriz en un solo lugar) |
| 3 | No existe listado de departamentos ni roles para los selects del formulario de usuarios | Endpoints de solo lectura `GET /catalogos/roles` y `GET /catalogos/departamentos`, o constantes temporales en el frontend |

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

---

## 13. Changelog

| Fecha | Cambio |
|---|---|
| 2026-09-23 | Planificación cerrada (stack, D1–D12, modelo de datos, motor, API, matriz de pruebas, estructura). |
| 2026-09-23 | Backend implementado: modelos, migración inicial, seed reiniciable, motor RBAC + ABAC (P1–P9), JWT con token_version, auditoría, 14 endpoints. |
| 2026-09-23 | 17 casos de prueba verificados manualmente contra el backend; bugs #1–#8 corregidos. |
| 2026-09-23 | Etapa de Testing formal eliminada del plan. Se crea este CONTEXT.md. Siguiente: frontend con Claude Code. |

> **Formato para nuevas entradas:** `| AAAA-MM-DD | Qué cambió, en qué archivos, y por qué |`. Si el cambio altera una decisión de la sección 6, actualizar también esa tabla.