from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioMe(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    departamento: str | None
    nivel_seguridad: int
    pais: str

    class Config:
        from_attributes = True


class PermisosOut(BaseModel):
    permisos: list[str]