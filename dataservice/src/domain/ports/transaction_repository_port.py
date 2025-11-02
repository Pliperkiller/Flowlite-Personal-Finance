from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Tuple
from ..entities import Transaction


class TransactionRepositoryPort(ABC):
    """
    Port for transaction repository operations.
    """

    @abstractmethod
    async def get_transactions_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Transaction], int]:
        """
        Get paginated transactions for a user.

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (list of transactions, total count)
        """
        pass
