from domain.vo.value_objects import LoteId, TransaccionId, CategoriaId
from domain.enums.enums import EstadoLote
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from abc import ABC, abstractmethod



@dataclass
class DomainEvent:
    """Evento base del dominio"""
    ocurrido_en: datetime = field(default_factory=datetime.now)


@dataclass
class LoteCargadoEvent(DomainEvent):
    """Evento: Lote cargado exitosamente"""
    lote_id: LoteId


@dataclass
class LoteProcesadoEvent(DomainEvent):
    """Evento: Lote procesado completamente"""
    lote_id: LoteId
    estado: EstadoLote


@dataclass
class TransaccionClasificadaEvent(DomainEvent):
    """Evento: Transacción clasificada"""
    transaccion_id: TransaccionId
    categoria_id: CategoriaId
    confianza: Decimal


class EventPublisher(ABC):
    """Puerto para publicador de eventos"""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publica un evento de dominio"""
        pass