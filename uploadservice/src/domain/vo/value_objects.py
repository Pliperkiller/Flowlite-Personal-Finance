from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class TransaccionId:
    """Value Object para ID de Transacción"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("TransaccionId no puede estar vacío")


@dataclass(frozen=True)
class LoteId:
    """Value Object para ID de Lote"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("LoteId no puede estar vacío")


@dataclass(frozen=True)
class CategoriaId:
    """Value Object para ID de Categoría"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("CategoriaId no puede estar vacío")


@dataclass(frozen=True)
class ClasificacionId:
    """Value Object para ID de Clasificación"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("ClasificacionId no puede estar vacío")


@dataclass(frozen=True)
class BancoId:
    """Value Object para ID de Banco"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("BancoId no puede estar vacío")


@dataclass(frozen=True)
class UserId:
    """Value Object para ID de Usuario"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("UserId no puede estar vacío")


@dataclass(frozen=True)
class Money:
    """Value Object para Dinero"""
    cantidad: Decimal
    moneda: str = "COP"
    
    def __post_init__(self):
        if self.moneda is None or not self.moneda.strip():
            object.__setattr__(self, 'moneda', 'COP')
        
        # Redondear a 2 decimales
        object.__setattr__(self, 'cantidad', self.cantidad.quantize(Decimal('0.01')))
    
    def es_negativo(self) -> bool:
        return self.cantidad < Decimal('0')
    
    def es_positivo(self) -> bool:
        return self.cantidad > Decimal('0')
    
    def es_cero(self) -> bool:
        return self.cantidad == Decimal('0')
    
    def sumar(self, otro: 'Money') -> 'Money':
        self._validar_misma_moneda(otro)
        return Money(self.cantidad + otro.cantidad, self.moneda)
    
    def restar(self, otro: 'Money') -> 'Money':
        self._validar_misma_moneda(otro)
        return Money(self.cantidad - otro.cantidad, self.moneda)
    
    def valor_absoluto(self) -> 'Money':
        return Money(abs(self.cantidad), self.moneda)
    
    def _validar_misma_moneda(self, otro: 'Money'):
        if self.moneda != otro.moneda:
            raise ValueError(f"No se pueden operar monedas diferentes: {self.moneda} vs {otro.moneda}")
        
@dataclass(frozen=True)
class ArchivoOrigenId:
    value: str
    def __post_init__(self):
        if not self.value:
            raise ValueError("ArchivoOrigenId no puede estar vacío")

@dataclass(frozen=True)
class ArchivoOrigen:
    """Representa un archivo origen en un lote"""
    id: ArchivoOrigenId
    nombre: str
    ruta: str
    hash_md5: str
    tamanio_bytes: int
    fecha_carga: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Nombre de archivo requerido")
        if not self.hash_md5:
            raise ValueError("Hash MD5 requerido")