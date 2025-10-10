from dataclasses import dataclass
from decimal import Decimal
from abc import ABC, abstractmethod
from domain.vo.value_objects import CategoriaId, Money


@dataclass
class ResultadoClasificacion:
    """DTO para resultado de clasificación"""
    categoria_id: CategoriaId
    confianza: Decimal


class ModeloClasificacionService(ABC):
    """Puerto para servicio de clasificación ML"""
    
    @abstractmethod
    def clasificar(
        self, 
        descripcion: str, 
        valor: Money
    ) -> ResultadoClasificacion:
        """Clasifica una transacción"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Obtiene la versión del modelo"""
        pass


class FileStorage(ABC):
    """Puerto para almacenamiento de archivos"""
    
    @abstractmethod
    def guardar(self, archivo: bytes, nombre: str) -> str:
        """Guarda un archivo y retorna la ruta"""
        pass
    
    @abstractmethod
    def calcular_hash(self, archivo: bytes) -> str:
        """Calcula el hash MD5 del archivo"""
        pass
