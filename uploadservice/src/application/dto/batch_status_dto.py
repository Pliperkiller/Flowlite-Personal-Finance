from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class BatchStatusDTO(BaseModel):
    id_batch: UUID
    process_status: str
    start_date: datetime
    end_date: Optional[datetime]
    batch_size: Optional[int]
    processed_percentage: float
