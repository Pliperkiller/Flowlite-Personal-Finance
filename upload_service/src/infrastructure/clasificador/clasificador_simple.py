from ...domain.ports import ClasificadorPort


class ClasificadorSimple(ClasificadorPort):
    """
    Clasificador simple que retorna siempre 'Otro'
    En el futuro será reemplazado por un modelo de ML
    """

    async def clasificar(self, descripcion: str) -> str:
        # TODO: Integrar modelo de ML aquí
        return "Otro"
