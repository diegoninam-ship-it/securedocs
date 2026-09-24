# Matriz de roles y permisos — RBAC

SecureDocs implementa 6 roles y 8 permisos. La asignación rol↔permiso está **sembrada en base de datos** (tabla `rol_permiso`, ver [`modelo_base_datos.png`](modelo_base_datos.png)) y se evalúa en tiempo de ejecución con `tiene_permiso(db, rol, permiso)` (`backend/app/authz/rbac.py`). **Ningún router del código contiene condicionales como `if rol == "ADMIN"`** — es el requisito especial del enunciado (sección 16): RBAC vive únicamente en la tabla `rol_permiso`.

## Matriz

| Permiso | Administrador | Gerente | Supervisor | Empleado | Auditor | Invitado |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `DOC_CREAR` — Crear documento | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| `DOC_CONSULTAR` — Consultar documento | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `DOC_MODIFICAR` — Modificar documento | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| `DOC_ELIMINAR` — Eliminar documento | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| `DOC_APROBAR` — Aprobar documento | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `AUDITORIA_VER` — Ver auditoría | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `USUARIOS_GESTIONAR` — Gestionar usuarios | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `ROLES_ASIGNAR` — Asignar roles | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

Esta matriz coincide exactamente con la tabla mínima exigida en el enunciado del laboratorio (sección 4), con los mismos 6 roles y las mismas 8 operaciones.

## Descripción de cada rol

| Rol | Descripción |
|---|---|
| Administrador | Administra usuarios, roles y configuraciones. Único rol con `USUARIOS_GESTIONAR` y `ROLES_ASIGNAR`. |
| Gerente | Supervisa documentos de su área. Puede crear, consultar, modificar, eliminar, aprobar documentos y ver auditoría — pero no gestiona usuarios ni roles. |
| Supervisor | Revisa y aprueba documentos. Puede crear, consultar, modificar y aprobar, pero no eliminar ni ver auditoría. |
| Empleado | Crea y consulta documentos de su área. Puede crear, consultar y modificar, pero no eliminar, aprobar ni ver auditoría. |
| Auditor | Consulta documentos y registros de auditoría. Único permiso operativo sobre documentos es `DOC_CONSULTAR`; su función es de supervisión vía `AUDITORIA_VER`. |
| Invitado | Acceso temporal a determinados documentos. Solo `DOC_CONSULTAR`, y aun así queda sujeto a la política ABAC P8 (ver [`matriz_abac.md`](matriz_abac.md)). |

## Dónde vive esto en el código

- **Semilla:** `backend/app/seed.py` — diccionario `MATRIZ_RBAC` (rol → lista de permisos), sembrado en la tabla `rol_permiso` al ejecutar `python -m app.seed`.
- **Evaluación:** `backend/app/authz/rbac.py` — `tiene_permiso(db, rol_codigo, permiso_codigo)`, un `JOIN` sobre `roles` × `rol_permiso` × `permisos`.
- **Aplicación:** `backend/app/authz/dependencies.py` — `autorizar(permiso_rbac, accion_abac)`, dependencia de FastAPI usada en cada endpoint protegido (`backend/app/routers/*.py`). Si `tiene_permiso()` devuelve `False`, la petición se corta con `403 "No tienes permiso para esta operación"` **antes** de evaluar ABAC — RBAC es siempre la primera etapa (ver diagrama de flujo en `CONTEXT.md` sección 8).

**Importante:** que un rol tenga un permiso RBAC no garantiza el acceso — es solo la primera de dos etapas. La segunda etapa (ABAC) puede seguir denegando según los atributos del usuario, el recurso y el entorno. Ver [`matriz_abac.md`](matriz_abac.md).
