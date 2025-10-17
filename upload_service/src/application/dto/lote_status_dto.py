from pydantic import BaseModel
from datetime import datetime


class LoteStatusDTO(BaseModel):
    lote_id: int
    estado: str
    total_registros: int
    registros_procesados: int
    porcentaje_procesado: float
    created_at: datetime
    updated_at: datetime
