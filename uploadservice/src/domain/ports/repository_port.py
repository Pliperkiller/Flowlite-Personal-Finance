from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from ..entities import Transaction, Bank, Category, TransactionBatch


class TransactionRepositoryPort(ABC):
    @abstractmethod
    async def save_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """Save a batch of transactions"""
        pass

    @abstractmethod
    async def get_by_id(self, id_transaction: UUID) -> Optional[Transaction]:
        """Get transaction by ID"""
        pass


class BankRepositoryPort(ABC):
    @abstractmethod
    async def get_by_name(self, bank_name: str) -> Optional[Bank]:
        """Get bank by name"""
        pass

    @abstractmethod
    async def save(self, bank: Bank) -> Bank:
        """Save bank"""
        pass

    @abstractmethod
    async def get_by_id(self, id_bank: str) -> Optional[Bank]:
        """Get bank by ID"""
        pass


class CategoryRepositoryPort(ABC):
    @abstractmethod
    async def get_by_description(self, description: str) -> Optional[Category]:
        """Get category by description"""
        pass

    @abstractmethod
    async def save(self, category: Category) -> Category:
        """Save category"""
        pass

    @abstractmethod
    async def get_by_id(self, id_category: str) -> Optional[Category]:
        """Get category by ID (id_category is a string like 'cat-001-retiros-efectivo')"""
        pass


class TransactionBatchRepositoryPort(ABC):
    @abstractmethod
    async def save(self, batch: TransactionBatch) -> TransactionBatch:
        """Save transaction batch"""
        pass

    @abstractmethod
    async def get_by_id(self, id_batch: UUID) -> Optional[TransactionBatch]:
        """Get transaction batch by ID"""
        pass

    @abstractmethod
    async def update(self, batch: TransactionBatch) -> TransactionBatch:
        """Update transaction batch"""
        pass


class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, id_user: UUID) -> bool:
        """Check if user exists in database"""
        pass
