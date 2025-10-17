from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities import Transaccion, Banco, Categoria, LoteTransaccion


class TransaccionRepositoryPort(ABC):
    @abstractmethod
    async def save_batch(self, transacciones: List[Transaccion]) -> List[Transaccion]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Transaccion]:
        pass


class BancoRepositoryPort(ABC):
    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[Banco]:
        pass

    @abstractmethod
    async def save(self, banco: Banco) -> Banco:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Banco]:
        pass


class CategoriaRepositoryPort(ABC):
    @abstractmethod
    async def get_by_nombre(self, nombre: str) -> Optional[Categoria]:
        pass

    @abstractmethod
    async def save(self, categoria: Categoria) -> Categoria:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Categoria]:
        pass


class LoteTransaccionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, lote: LoteTransaccion) -> LoteTransaccion:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[LoteTransaccion]:
        pass

    @abstractmethod
    async def update(self, lote: LoteTransaccion) -> LoteTransaccion:
        pass


class UsuarioRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> bool:
        """Verifica si el usuario existe en la base de datos"""
        pass
