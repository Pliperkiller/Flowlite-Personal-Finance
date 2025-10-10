from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Categoria:
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
