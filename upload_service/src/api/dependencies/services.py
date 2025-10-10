from ...infrastructure.clasificador import ClasificadorSimple
from ...domain.ports import ClasificadorPort


def get_clasificador() -> ClasificadorPort:
    return ClasificadorSimple()
