from dataclasses import dataclass, field


@dataclass
class Resultado:
    permitido: bool
    motivo: str | None = None

    @staticmethod
    def ok() -> "Resultado":
        return Resultado(permitido=True)

    @staticmethod
    def deny(motivo: str) -> "Resultado":
        return Resultado(permitido=False, motivo=motivo)


REGISTRO: dict[str, callable] = {}


def politica(codigo: str):
    """Decorador que registra una función de política bajo su código (P1, P2, ...)."""
    def wrapper(func):
        REGISTRO[codigo] = func
        return func
    return wrapper