<div align="center">

# 🔐 SecureDocs

### Sistema de Gestión de Expedientes con RBAC + ABAC

*¿El rol permite la acción? → ¿Se cumplen las políticas de atributos en este contexto?*
*Solo se autoriza cuando **ambas** etapas lo permiten. Todo intento queda auditado.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)](backend)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](frontend)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)](https://neon.tech)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?logo=vercel&logoColor=white)](https://securedocs-ruby.vercel.app)

**[🚀 Ver demo en producción](https://securedocs-ruby.vercel.app)**

</div>

---

Laboratorio **GLAB-S06 (Cloud Security)**, curso *Desarrollo de Soluciones en la Nube*, Tecsup. Caso práctico: **TechCorp S.A.** necesita controlar el acceso a documentos internos de sus áreas — sin condicionales de rol dispersos por el código, con autorización centralizada y auditable.

> 🔑 **Prueba la demo:** `admin@securedocs.pe` / `Demo1234!`
> Más usuarios (con distintos roles) en [`docs/evidencias_casos_prueba.md`](docs/evidencias_casos_prueba.md).

## 📑 Contenido

- [Arquitectura](#️-arquitectura)
- [Funcionalidades](#-funcionalidades)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Instalación y ejecución local](#-instalación-y-ejecución-local)
- [Pruebas](#-pruebas)
- [Despliegue](#-despliegue)
- [Entregables del laboratorio](#-entregables-del-laboratorio)

## 🏗️ Arquitectura

<div align="center">
<img src="docs/diagrama_arquitectura.png" alt="Arquitectura de SecureDocs" width="620">
</div>

Un único proyecto de **Vercel** sirve el frontend estático y el backend como Vercel Function (ASGI). Diagrama editable en [`docs/diagrama_arquitectura.md`](docs/diagrama_arquitectura.md).

## ✨ Funcionalidades

| | |
|---|---|
| 🔐 **Autenticación** | JWT (`sub` + `token_version`); el logout revoca la sesión en **todos** los dispositivos |
| 🛡️ **RBAC** | 6 roles × 8 permisos, sembrados en base de datos — ningún router contiene `if rol == ...` |
| ⚖️ **ABAC** | 9 políticas (P1–P9): departamento, nivel de seguridad, propiedad, horario, país, dispositivo, estado del usuario, invitados, segregación de funciones — funciones puras + configuración en tabla `politicas` (JSONB, sin `eval()`) |
| 📄 **Documentos** | Crear, consultar, modificar, eliminar, aprobar. Ciclo de vida `PENDIENTE → PUBLICADO` |
| 👥 **Usuarios** | Crear, editar, activar/desactivar/suspender, asignar rol y departamento |
| 📝 **Auditoría** | Todo intento (permitido o denegado) queda registrado con motivo y política que falló |
| 🎛️ **Simulador de contexto** | Panel para simular ubicación/dispositivo (solo `DEMO_MODE`) — demuestra P4–P6 sin depender de IP real ni de un MDM corporativo |

## 📂 Estructura del repositorio

```
securedocs/
├── api/index.py        # entrypoint ASGI para Vercel (Vercel Function)
├── backend/             # FastAPI — API, modelos, motor RBAC+ABAC
├── frontend/             # React + Vite — interfaz web
├── docs/                 # entregables: diagramas, matrices, evidencias
├── requirements.txt       # dependencias Python (usado también por Vercel)
├── vercel.json             # configuración de despliegue
└── CONTEXT.md               # documento de trabajo detallado (decisiones de diseño, historial, bugs resueltos)
```

📘 Para el detalle completo de decisiones de diseño, modelo de datos, motor de autorización y API: [`CONTEXT.md`](CONTEXT.md).

## ⚙️ Instalación y ejecución local

### Requisitos previos

- Python 3.11+
- Node.js 18+ y npm
- Una base de datos PostgreSQL (se usó [Neon](https://neon.tech), plan gratuito)

### 1 · Clonar el repositorio

```bash
git clone https://github.com/diegoninam-ship-it/securedocs.git
cd securedocs
```

### 2 · Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate               # en Linux/Mac: source venv/bin/activate
pip install -r ..\requirements.txt
```

Crear `backend/.env` a partir de `backend/.env.example`:

```env
DATABASE_URL_POOLED=postgresql://usuario:password@host-pooler/db?sslmode=require
DATABASE_URL_UNPOOLED=postgresql://usuario:password@host/db?sslmode=require
JWT_SECRET=<generar con el comando de abajo>
JWT_EXPIRE_MINUTES=30
DEMO_MODE=true
TZ_APP=America/Lima
```

Generar un secreto para `JWT_SECRET`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

> ⚠️ **Cuidado con las comillas.** Si el valor de la URL de conexión viene entre comillas (algunos proveedores lo muestran así), no las incluyas al pegarlo en otro lugar (ej. variables de entorno de un hosting) — `python-dotenv` las tolera en `.env`, pero la mayoría de paneles de hosting las toman literalmente y rompen el parseo de la URL.

Aplicar el esquema y cargar los datos semilla:

```powershell
alembic upgrade head
python -m app.seed
```

Levantar el servidor:

```powershell
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000` (documentación interactiva en `/docs`).

### 3 · Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

El frontend queda en `http://127.0.0.1:5173` y llama al backend a través del proxy configurado en `vite.config.ts` (requiere el backend corriendo en el puerto 8000).

### 4 · Iniciar sesión

Todos los usuarios semilla usan la contraseña **`Demo1234!`**. Ejemplo: `admin@securedocs.pe` (ADMINISTRADOR). El listado completo de usuarios y sus roles está en [`docs/evidencias_casos_prueba.md`](docs/evidencias_casos_prueba.md) y en `CONTEXT.md` sección 10.

## 🧪 Pruebas

Los 17 casos de prueba (12 obligatorios del enunciado + 5 diseñados por el equipo) están documentados con evidencia real (peticiones HTTP + capturas de pantalla) en [`docs/evidencias_casos_prueba.md`](docs/evidencias_casos_prueba.md). El registro de auditoría real generado por esas pruebas está en [`docs/registro_auditoria.md`](docs/registro_auditoria.md).

Para reiniciar la base de datos a su estado semilla en cualquier momento (varias pruebas modifican datos):

```powershell
python -m app.seed
```

## 🚀 Despliegue

La aplicación está desplegada en Vercel: **https://securedocs-ruby.vercel.app**. El detalle de la arquitectura de despliegue (Vercel Function ASGI + frontend estático + rewrites) está en `CONTEXT.md` sección 14.

## 📦 Entregables del laboratorio

| # | Entregable | Ubicación |
|---|---|---|
| 1 | Código fuente | Este repositorio |
| 2 | Repositorio Git | [github.com/diegoninam-ship-it/securedocs](https://github.com/diegoninam-ship-it/securedocs) |
| 3 | README con instrucciones de instalación | Este archivo |
| 4 | Diagrama de arquitectura | [`docs/diagrama_arquitectura.md`](docs/diagrama_arquitectura.md) · [PNG](docs/diagrama_arquitectura.png) |
| 5 | Modelo de base de datos | [`docs/modelo_base_datos.md`](docs/modelo_base_datos.md) · [PNG](docs/modelo_base_datos.png) |
| 6 | Matriz de roles y permisos RBAC | [`docs/matriz_rbac.md`](docs/matriz_rbac.md) |
| 7 | Matriz de políticas ABAC | [`docs/matriz_abac.md`](docs/matriz_abac.md) |
| 8 | Evidencias de los casos de prueba | [`docs/evidencias_casos_prueba.md`](docs/evidencias_casos_prueba.md) |
| 9 | Registro de auditoría | [`docs/registro_auditoria.md`](docs/registro_auditoria.md) |
| 10 | Video / demostración de funcionamiento | *(a cargo del equipo)* |

<div align="center">

---

Hecho con FastAPI + React · Diego Nina · Tecsup 2026

</div>
