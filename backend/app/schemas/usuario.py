from pydantic import BaseModel, EmailStr


class UsuarioCreate(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    rol_codigo: str
    departamento_codigo: str | None = None
    nivel_seguridad: int = 1
    pais: str = "PE"
    tipo_contrato: str = "INTERNO"


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    departamento_codigo: str | None = None
    nivel_seguridad: int | None = None
    pais: str | None = None
    tipo_contrato: str | None = None
    estado: str | None = None


class UsuarioRolUpdate(BaseModel):
    rol_codigo: str


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    departamento: str | None
    nivel_seguridad: int
    pais: str
    tipo_contrato: str
    estado: str

    class Config:
        from_attributes = True