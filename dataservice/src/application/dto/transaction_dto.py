from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional


class TransactionDTO(BaseModel):
    """
    DTO for transaction data.
    """
    id: str
    name: str
    value: float
    date: str  # ISO format datetime string
    type: str  # income, expense
    category: str
    bank: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionsPaginatedResponse(BaseModel):
    """
    Paginated response for transactions.
    """
    transactions: list[TransactionDTO]
    page: int
    pageSize: int
    totalPages: int
    totalTransactions: int

    class Config:
        from_attributes = True
