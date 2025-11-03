from abc import ABC, abstractmethod
from typing import List
from ..entities import TransactionCategory, InsightCategory


class CategoryRepositoryPort(ABC):
    """
    Port for category repository operations.
    """

    @abstractmethod
    async def get_all_transaction_categories(self) -> List[TransactionCategory]:
        """
        Get all available transaction categories.

        Returns:
            List of transaction categories
        """
        pass

    @abstractmethod
    async def get_all_insight_categories(self) -> List[InsightCategory]:
        """
        Get all available insight categories.

        Returns:
            List of insight categories
        """
        pass
