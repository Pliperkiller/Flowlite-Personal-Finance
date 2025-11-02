from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import Transaction, Insight, TransactionBatch
from .value_objects import UserId, BatchId


class TransactionRepository(ABC):
    """Port for transaction data access"""
    
    @abstractmethod
    def find_by_user_and_batch(self, user_id: UserId, batch_id: BatchId) -> List[Transaction]:
        """Gets all transactions for a user in a specific batch"""
        pass
    
    @abstractmethod
    def find_by_user(self, user_id: UserId, limit: Optional[int] = None) -> List[Transaction]:
        """Gets transactions for a user (optionally limited)"""
        pass


class InsightRepository(ABC):
    """Port for insight persistence"""

    @abstractmethod
    def save(self, insight: Insight) -> Insight:
        """Persists a new insight"""
        pass

    @abstractmethod
    def save_batch(self, insights: List[Insight]) -> List[Insight]:
        """Persists multiple insights efficiently"""
        pass

    @abstractmethod
    def find_by_user(self, user_id: UserId) -> List[Insight]:
        """Gets all insights for a user"""
        pass

    @abstractmethod
    def delete_by_user(self, user_id: UserId) -> int:
        """Deletes all insights for a user"""
        pass


class BatchRepository(ABC):
    """Port for transaction batch access"""
    
    @abstractmethod
    def find_by_id(self, batch_id: BatchId) -> Optional[TransactionBatch]:
        """Finds a batch by its ID"""
        pass
