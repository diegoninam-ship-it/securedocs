# Matriz de políticas — ABAC

SecureDocs implementa **9 políticas** ABAC (el enunciado exige un mínimo de 8; se agregó una novena — P9, segregación de funciones — por decisión propia del equipo). Cada política es una **función pura** en `backend/app/authz/abac/policies.py` (recibe `Contexto` + `parametros`, no toca la base de datos), registrada con el decorador `@politica("P#")`. Su **configuración** (si está activa, a qué roles aplica, qué operaciones cubre, sus parámetros) vive en la tabla `politicas` — es la **política híbrida** documentada como decisión de diseño D12 en `CONTEXT.md`: la lógica está en código, la configuración en base de datos, y nunca se usa `eval()`.

Una operación solo se autoriza si **RBAC Y ABAC** la permiten. ABAC evalúa **todas** las políticas aplicables (no se detiene en la primera que falla) y acumula los motivos — estrategia *deny-overrides* con motivos concatenados (`backend/app/authz/abac/engine.py`).

## Matriz

| Código | Política | Aplica a | Exentos | Operaciones | Regla |
|---|---|---|---|---|---|
| **P1** | Departamento | Todos | Administrador, Auditor, Invitado (este se rige por P8) | Consultar, Modificar, Aprobar, Eliminar | `usuario.departamento == documento.departamento` |
| **P2** | Nivel de seguridad | Todos | — | Crear + las 4 anteriores | `usuario.nivel_seguridad >= documento.nivel_confidencialidad` |
| **P3** | Propiedad | Todos | Gerente, Administrador | Modificar | `usuario.id == documento.propietario_id` |
| **P4** | Horario | Todos | — | Consultar, Modificar, Aprobar, Eliminar (documento existente) | Si `nivel_confidencialidad >= 4`: solo entre 08:00–18:00 hora de Lima |
| **P5** | País | Todos | — | Consultar, Modificar, Aprobar, Eliminar (documento existente) | `usuario.pais == documento.pais` **Y** `entorno.ubicacion == documento.pais` |
| **P6** | Dispositivo | Todos | — | Consultar, Modificar, Aprobar, Eliminar (documento existente) | Si `nivel_confidencialidad >= 4`: `entorno.dispositivo == "CORPORATIVO"` |
| **P7** | Estado del usuario | Todos | — | Login, Cualquiera | `usuario.estado == "ACTIVO"` |
| **P8** | Invitados | **Solo Invitado** | — | Consultar | `tipo_contrato == "EXTERNO"` **Y** `nivel_confidencialidad <= 1` **Y** `documento.estado == "PUBLICADO"` |
| **P9** † | Segregación de funciones | Todos | — | Aprobar | `usuario.id != documento.propietario_id` (el propietario no puede aprobar su propio documento) |

† P9 no está en el mínimo del enunciado — se agregó porque el equipo consideró que sin ella un Gerente o Supervisor podría autoaprobar su propio documento, rompiendo el principio de separación de responsabilidades típico de un control de acceso serio.

## Ejemplo de evaluación combinada (igual al del enunciado, verificado contra el sistema real)

Actor: Carlos Ruiz (SUPERVISOR, FINANZAS, nivel 3, PE, ACTIVO) intenta **aprobar** el documento "Presupuesto anual" (FINANZAS, nivel 3, PENDIENTE, PE, propietario: Patricia Gómez), desde Perú, dispositivo corporativo, 11:30 a.m.

1. **RBAC:** `SUPERVISOR` tiene `DOC_APROBAR` → **PERMITIDO**.
2. **ABAC:**
   - P1 (departamento): `FINANZAS == FINANZAS` ✓
   - P2 (nivel): `3 >= 3` ✓
   - P4 (horario): nivel 3 < umbral 4 → no aplica ✓
   - P5 (país): `PE == PE` y ubicación `PE == PE` ✓
   - P6 (dispositivo): nivel 3 < umbral 4 → no aplica ✓
   - P7 (estado): `ACTIVO` ✓
   - P9 (segregación): Carlos (id 3) ≠ propietario (Patricia, id 2) ✓
   - **Resultado: PERMITIDO**

Este caso corresponde al caso de prueba #3 (ver [`evidencias_casos_prueba.md`](evidencias_casos_prueba.md)), verificado contra el backend real.

## Ejemplo de acceso denegado (igual al del enunciado)

Actor: una empleada de RRHH (nivel 2) intenta **modificar** un documento de FINANZAS con nivel de confidencialidad 4.

1. **RBAC:** `EMPLEADO` tiene `DOC_MODIFICAR` → **PERMITIDO**.
2. **ABAC:** P1 falla (`RRHH != FINANZAS`) y P2 falla (`2 < 4`) → **DENEGADO**, con ambos motivos acumulados.
3. **Resultado final: DENEGADO**, pese a tener el permiso RBAC. Este es exactamente el punto que exige demostrar la sección 9 del enunciado: tener un permiso por rol no implica autorización sobre el recurso concreto.

## Dónde vive esto en el código

- **Lógica (pura, sin BD):** `backend/app/authz/abac/policies.py` — una función por política.
- **Registro de políticas:** `backend/app/authz/abac/registry.py` — decorador `@politica`, diccionario `REGISTRO`.
- **Motor de evaluación:** `backend/app/authz/abac/engine.py` — `evaluar_abac(db, ctx)`, consulta las políticas activas en BD, filtra las aplicables al rol/operación, ejecuta cada función y acumula motivos.
- **Configuración (BD):** tabla `politicas`, sembrada por `POLITICAS` en `backend/app/seed.py`. Agregar una política nueva no requiere tocar el motor: solo una función `@politica("P10")` + una fila en la tabla.
- **Aplicación:** `backend/app/authz/dependencies.py` — `verificar_abac(request, db, recurso, recurso_nombre)`, llamada desde cada router después de que RBAC ya autorizó.

Ver `CONTEXT.md` sección 6 (decisiones D1–D12) para el razonamiento detrás de cada regla, y sección 8 para el flujo completo de una petición.
