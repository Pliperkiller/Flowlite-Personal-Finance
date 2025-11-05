from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Transaction:
    id_transaction: Optional[UUID]
    id_user: UUID
    id_category: str  # Category IDs are strings like "cat-001-retiros-efectivo"
    id_bank: Optional[str]  # Bank IDs are strings, not UUIDs
    id_batch: Optional[UUID]
    transaction_name: str
    value: Decimal
    transaction_date: datetime
    transaction_type: str
