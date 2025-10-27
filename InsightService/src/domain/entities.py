from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from decimal import Decimal

from .value_objects import UserId, BatchId, Money, CategoryId


@dataclass
class Transaction:
    """Entity representing a financial transaction"""
    id_transaction: UUID
    id_user: UserId
    id_category: CategoryId
    value: Money
    transaction_name: str
    transaction_date: datetime
    transaction_type: str
    id_batch: Optional[BatchId] = None
    id_bank: Optional[UUID] = None
    category_description: Optional[str] = None
    
    def __post_init__(self):
        if not self.transaction_name:
            raise ValueError("Transaction name is required")
        if self.transaction_type not in ['income', 'expense']:
            raise ValueError("Transaction type must be 'income' or 'expense'")


@dataclass
class Insight:
    """Entity representing a financial recommendation"""
    id_insight: UUID
    id_user: UserId
    id_category: CategoryId
    title: str
    text: str
    relevance: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.title:
            raise ValueError("Title is required")
        if not self.text:
            raise ValueError("Text is required")
        if not 1 <= self.relevance <= 10:
            raise ValueError("Relevance must be between 1 and 10")
    
    @classmethod
    def create(cls, id_user: UserId, id_category: CategoryId, 
               title: str, text: str, relevance: int) -> 'Insight':
        """Factory method to create a new Insight"""
        return cls(
            id_insight=uuid4(),
            id_user=id_user,
            id_category=id_category,
            title=title,
            text=text,
            relevance=relevance
        )


@dataclass
class TransactionBatch:
    """Entity representing a batch of processed transactions"""
    id_batch: BatchId
    process_status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    batch_size: Optional[int] = None
    
    def is_processed(self) -> bool:
        """Checks if the batch was successfully processed"""
        return self.process_status == "Processed"
