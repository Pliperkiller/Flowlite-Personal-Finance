from abc import ABC, abstractmethod


class ClasificadorPort(ABC):
    @abstractmethod
    async def clasificar(self, descripcion: str) -> str:
        """
        Clasifica una transacción basándose en su descripción
        Retorna el nombre de la categoría
        """
        pass
