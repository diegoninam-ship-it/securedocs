from pydantic import BaseModel


class RolOut(BaseModel):
    codigo: str
    nombre: str

    class Config:
        from_attributes = True


class DepartamentoOut(BaseModel):
    codigo: str
    nombre: str

    class Config:
        from_attributes = True
