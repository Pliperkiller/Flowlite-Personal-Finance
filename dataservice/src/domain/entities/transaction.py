from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Transaction:
    """
    Domain entity representing a transaction.
    """
    id_transaction: UUID
    id_user: UUID
    id_category: str  # Category IDs are strings like "cat-001-retiros-efectivo"
    id_bank: UUID | str | None  # Can be UUID or bank code string
    id_batch: UUID | str | None  # Can be UUID or batch code string
    transaction_name: str
    value: Decimal
    transaction_date: datetime
    transaction_type: str  # income, expense
    category_description: str | None = None
    bank_name: str | None = None
