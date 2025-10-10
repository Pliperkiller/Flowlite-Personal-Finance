from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class EstadoLote(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


@dataclass
class LoteTransaccion:
    id: Optional[int]
    usuario_id: int
    banco_id: int
    estado: EstadoLote
    total_registros: int
    registros_procesados: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def porcentaje_procesado(self) -> float:
        if self.total_registros == 0:
            return 0.0
        return (self.registros_procesados / self.total_registros) * 100
