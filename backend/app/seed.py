from app.db import SessionLocal
from app.models.rbac import Rol, Permiso, RolPermiso
from app.models.usuario import Departamento
from app.models.politica import Politica
import bcrypt
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.db import SessionLocal, Base, engine
from app.models.auditoria import Auditoria 



ROLES = ["ADMINISTRADOR", "GERENTE", "SUPERVISOR", "EMPLEADO", "AUDITOR", "INVITADO"]

PERMISOS = [
    "DOC_CREAR", "DOC_CONSULTAR", "DOC_MODIFICAR", "DOC_ELIMINAR", "DOC_APROBAR",
    "AUDITORIA_VER", "USUARIOS_GESTIONAR", "ROLES_ASIGNAR",
]

# Matriz RBAC exacta de la sección 4 del expediente
MATRIZ_RBAC = {
    "ADMINISTRADOR": PERMISOS,  # tiene los 8
    "GERENTE": ["DOC_CREAR", "DOC_CONSULTAR", "DOC_MODIFICAR", "DOC_ELIMINAR", "DOC_APROBAR", "AUDITORIA_VER"],
    "SUPERVISOR": ["DOC_CREAR", "DOC_CONSULTAR", "DOC_MODIFICAR", "DOC_APROBAR"],
    "EMPLEADO": ["DOC_CREAR", "DOC_CONSULTAR", "DOC_MODIFICAR"],
    "AUDITOR": ["DOC_CONSULTAR", "AUDITORIA_VER"],
    "INVITADO": ["DOC_CONSULTAR"],
}


def seed_rbac(db):
    roles = {}
    for codigo in ROLES:
        rol = Rol(codigo=codigo, nombre=codigo.capitalize())
        db.add(rol)
        roles[codigo] = rol

    permisos = {}
    for codigo in PERMISOS:
        permiso = Permiso(codigo=codigo, descripcion=codigo.replace("_", " ").title())
        db.add(permiso)
        permisos[codigo] = permiso

    db.flush()  # asigna IDs sin cerrar la transacción, para poder usarlos abajo

    for rol_codigo, permisos_del_rol in MATRIZ_RBAC.items():
        for permiso_codigo in permisos_del_rol:
            db.add(RolPermiso(rol_id=roles[rol_codigo].id, permiso_id=permisos[permiso_codigo].id))

    return roles



DEPARTAMENTOS = ["TI", "FINANZAS", "RRHH", "AUDITORIA"]


def seed_departamentos(db):
    deptos = {}
    for codigo in DEPARTAMENTOS:
        depto = Departamento(codigo=codigo, nombre=codigo.capitalize())
        db.add(depto)
        deptos[codigo] = depto
    db.flush()
    return deptos


OPERACIONES_DOC_EXISTENTE = ["CONSULTAR", "MODIFICAR", "APROBAR", "ELIMINAR"]

POLITICAS = [
    dict(
        codigo="P1", nombre="Departamento",
        descripcion="El usuario solo accede a documentos de su propio departamento.",
        roles_aplicables=None,
        roles_exentos=["ADMINISTRADOR", "AUDITOR", "INVITADO"],
        operaciones=OPERACIONES_DOC_EXISTENTE,
        parametros=None,
    ),
    dict(
        codigo="P2", nombre="Nivel de seguridad",
        descripcion="El nivel de seguridad del usuario debe ser >= al nivel de confidencialidad del documento.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=["CREAR"] + OPERACIONES_DOC_EXISTENTE,
        parametros=None,
    ),
    dict(
        codigo="P3", nombre="Propiedad",
        descripcion="Solo el propietario puede modificar el documento.",
        roles_aplicables=None,
        roles_exentos=["GERENTE", "ADMINISTRADOR"],
        operaciones=["MODIFICAR"],
        parametros=None,
    ),
    dict(
        codigo="P4", nombre="Horario",
        descripcion="Documentos con confidencialidad >= 4 solo se acceden en horario laboral.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=OPERACIONES_DOC_EXISTENTE,
        parametros={"hora_inicio": "08:00", "hora_fin": "18:00", "umbral": 4, "zona": "America/Lima"},
    ),
    dict(
        codigo="P5", nombre="País",
        descripcion="El usuario y su ubicación deben coincidir con el país del documento.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=OPERACIONES_DOC_EXISTENTE,
        parametros=None,
    ),
    dict(
        codigo="P6", nombre="Dispositivo",
        descripcion="Documentos con confidencialidad >= 4 solo se acceden desde dispositivo corporativo.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=OPERACIONES_DOC_EXISTENTE,
        parametros={"umbral": 4, "dispositivo_requerido": "CORPORATIVO"},
    ),
    dict(
        codigo="P7", nombre="Estado del usuario",
        descripcion="Un usuario suspendido o inactivo no puede acceder al sistema.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=["LOGIN", "CUALQUIERA"],
        parametros={"estado_requerido": "ACTIVO"},
    ),
    dict(
        codigo="P8", nombre="Invitados",
        descripcion="Los invitados solo consultan documentos publicados de nivel 1 o inferior.",
        roles_aplicables=["INVITADO"],
        roles_exentos=[],
        operaciones=["CONSULTAR"],
        parametros={"tipo_contrato_requerido": "EXTERNO", "nivel_maximo": 1, "estado_requerido": "PUBLICADO"},
    ),
    dict(
        codigo="P9", nombre="Segregación de funciones",
        descripcion="El propietario de un documento no puede aprobarlo.",
        roles_aplicables=None,
        roles_exentos=[],
        operaciones=["APROBAR"],
        parametros=None,
    ),
]


def seed_politicas(db):
    for p in POLITICAS:
        db.add(Politica(**p, activa=True))


# (rol_codigo, depto_codigo o None, nivel, pais, tipo_contrato, estado)
USUARIOS = {
    "U1": ("Admin Sistema", "admin@securedocs.pe", "ADMINISTRADOR", "TI", 5, "PE", "INTERNO", "ACTIVO"),
    "U2": ("Patricia Gómez", "patricia.gomez@securedocs.pe", "GERENTE", "FINANZAS", 5, "PE", "INTERNO", "ACTIVO"),
    "U3": ("Carlos Ruiz", "carlos.ruiz@securedocs.pe", "SUPERVISOR", "FINANZAS", 3, "PE", "INTERNO", "ACTIVO"),
    "U4": ("Luis Paredes", "luis.paredes@securedocs.pe", "EMPLEADO", "FINANZAS", 2, "PE", "INTERNO", "ACTIVO"),
    "U5": ("Rosa Díaz", "rosa.diaz@securedocs.pe", "EMPLEADO", "FINANZAS", 2, "PE", "INTERNO", "ACTIVO"),
    "U6": ("María Quispe", "maria.quispe@securedocs.pe", "EMPLEADO", "RRHH", 2, "PE", "INTERNO", "ACTIVO"),
    "U7": ("Jorge Salas", "jorge.salas@securedocs.pe", "AUDITOR", "AUDITORIA", 5, "PE", "INTERNO", "ACTIVO"),
    "U8": ("Proveedor Externo", "proveedor@externo.com", "INVITADO", None, 1, "PE", "EXTERNO", "ACTIVO"),
    "U9": ("Pedro Vargas", "pedro.vargas@securedocs.pe", "EMPLEADO", "FINANZAS", 2, "PE", "INTERNO", "INACTIVO"),
}

PASSWORD_DEMO = "Demo1234!"  # misma clave para todos los usuarios semilla, solo para pruebas


def seed_usuarios(db, roles, deptos):
    usuarios = {}
    hash_demo = bcrypt.hashpw(PASSWORD_DEMO.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    for clave, (nombre, correo, rol_cod, depto_cod, nivel, pais, contrato, estado) in USUARIOS.items():
        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password_hash=hash_demo,
            rol_id=roles[rol_cod].id,
            departamento_id=deptos[depto_cod].id if depto_cod else None,
            nivel_seguridad=nivel,
            pais=pais,
            tipo_contrato=contrato,
            estado=estado,
        )
        db.add(usuario)
        usuarios[clave] = usuario

    db.flush()
    return usuarios


# (titulo, depto_codigo, nivel, estado, propietario_clave)
DOCUMENTOS = {
    "D1": ("Informe de gastos Q3", "FINANZAS", 2, "PENDIENTE", "U4"),
    "D2": ("Plan de capacitación", "RRHH", 2, "PENDIENTE", "U6"),
    "D3": ("Presupuesto anual", "FINANZAS", 3, "PENDIENTE", "U2"),
    "D4": ("Proyección de inversiones", "FINANZAS", 4, "PUBLICADO", "U2"),
    "D5": ("Plan estratégico 2027", "FINANZAS", 5, "PUBLICADO", "U2"),
    "D6": ("Manual del proveedor", "FINANZAS", 1, "PUBLICADO", "U4"),
    "D7": ("Contrato de servicios", "FINANZAS", 3, "PUBLICADO", "U2"),
    "D8": ("Borrador obsoleto", "FINANZAS", 1, "PENDIENTE", "U4"),
    "D9": ("Informe de conciliación", "FINANZAS", 3, "PENDIENTE", "U3"),
}


def seed_documentos(db, deptos, usuarios):
    for clave, (titulo, depto_cod, nivel, estado, propietario_clave) in DOCUMENTOS.items():
        db.add(Documento(
            titulo=titulo,
            departamento_id=deptos[depto_cod].id,
            nivel_confidencialidad=nivel,
            estado=estado,
            pais="PE",
            propietario_id=usuarios[propietario_clave].id,
        ))


def reset_schema():
    """Borra y recrea todas las tablas — deja la BD exactamente en blanco."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def main():
    reset_schema()
    db = SessionLocal()
    try:
        roles = seed_rbac(db)
        deptos = seed_departamentos(db)
        seed_politicas(db)
        usuarios = seed_usuarios(db, roles, deptos)
        seed_documentos(db, deptos, usuarios)
        db.commit()
        print("Semilla cargada correctamente: 9 usuarios, 9 documentos, 9 políticas.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()