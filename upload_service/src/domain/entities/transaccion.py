from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaccion:
    id: Optional[int]
    usuario_id: int
    banco_id: int
    categoria_id: int
    lote_id: int
    fecha: datetime
    descripcion: str
    referencia: Optional[str]
    valor: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
