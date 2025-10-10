from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.entities import Banco, Categoria, ClasificacionTransaccion, LoteCarga, Transaccion
from domain.vo.value_objects import BancoId, CategoriaId, ClasificacionId, LoteId, TransaccionId, UserId
from domain.enums.enums import EstadoTransaccion

class TransaccionRepository(ABC):
    """Puerto para repositorio de Transacciones"""
    
    @abstractmethod
    def save(self, transaccion: Transaccion) -> None:
        """Guarda una transacción"""
        pass
    
    @abstractmethod
    def save_all(self, transacciones: List[Transaccion]) -> None:
        """Guarda múltiples transacciones"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: TransaccionId) -> Optional[Transaccion]:
        """Busca una transacción por ID"""
        pass
    
    @abstractmethod
    def find_by_lote_id_and_estado(
        self, 
        lote_id: LoteId, 
        estado: EstadoTransaccion
    ) -> List[Transaccion]:
        """Busca transacciones por lote y estado"""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: UserId) -> List[Transaccion]:
        """Busca transacciones de un usuario"""
        pass
    
    @abstractmethod
    def next_id(self) -> TransaccionId:
        """Genera el siguiente ID"""
        pass


class LoteRepository(ABC):
    """Puerto para repositorio de Lotes"""
    
    @abstractmethod
    def save(self, lote: LoteCarga) -> None:
        """Guarda un lote"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: LoteId) -> Optional[LoteCarga]:
        """Busca un lote por ID"""
        pass
    
    @abstractmethod
    def exists_by_hash(self, hash_md5: str) -> bool:
        """Verifica si existe un lote con el hash dado"""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: UserId) -> List[LoteCarga]:
        """Busca lotes de un usuario"""
        pass
    
    @abstractmethod
    def next_id(self) -> LoteId:
        """Genera el siguiente ID"""
        pass


class ClasificacionRepository(ABC):
    """Puerto para repositorio de Clasificaciones"""
    
    @abstractmethod
    def save(self, clasificacion: ClasificacionTransaccion) -> None:
        """Guarda una clasificación"""
        pass
    
    @abstractmethod
    def find_by_transaccion_id(
        self, 
        transaccion_id: TransaccionId
    ) -> Optional[ClasificacionTransaccion]:
        """Busca clasificación por ID de transacción"""
        pass
    
    @abstractmethod
    def next_id(self) -> ClasificacionId:
        """Genera el siguiente ID"""
        pass


class CategoriaRepository(ABC):
    """Puerto para repositorio de Categorías"""
    
    @abstractmethod
    def find_by_id(self, id: CategoriaId) -> Optional[Categoria]:
        """Busca una categoría por ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Categoria]:
        """Obtiene todas las categorías"""
        pass
    
    @abstractmethod
    def find_by_codigo(self, codigo: str) -> Optional[Categoria]:
        """Busca una categoría por código"""
        pass


class BancoRepository(ABC):
    """Puerto para repositorio de Bancos"""
    
    @abstractmethod
    def find_by_id(self, id: BancoId) -> Optional[Banco]:
        """Busca un banco por ID"""
        pass
    
    @abstractmethod
    def find_by_nombre(self, nombre: str) -> Optional[Banco]:
        """Busca un banco por nombre"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Banco]:
        """Obtiene todos los bancos"""
        pass