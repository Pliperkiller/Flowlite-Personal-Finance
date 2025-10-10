from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Banco:
    id: Optional[int]
    nombre: str
    codigo: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
