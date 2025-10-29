from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass
class TransactionBatch:
    id_batch: Optional[UUID]
    process_status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    batch_size: Optional[int] = None

    @property
    def processed_percentage(self) -> float:
        """Calculate the percentage of processed records"""
        if self.batch_size == 0 or self.batch_size is None:
            return 0.0
        # This would need additional logic to track progress
        # For now, based on status
        if self.process_status == "completed":
            return 100.0
        elif self.process_status == "processing":
            return 50.0
        return 0.0
