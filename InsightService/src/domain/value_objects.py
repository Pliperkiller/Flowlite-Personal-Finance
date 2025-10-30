from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal


@dataclass(frozen=True)
class UserId:
    """Value Object for user identifier"""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BatchId:
    """Value Object for batch identifier"""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    """Value Object to represent monetary values"""
    amount: Decimal
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def __str__(self) -> str:
        return f"${self.amount:,.2f}"


@dataclass(frozen=True)
class CategoryId:
    """Value Object for category identifier"""
    value: UUID
    
    def __str__(self) -> str:
        return str(self.value)
