from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from ..entities import Insight


class InsightRepositoryPort(ABC):
    """
    Port for insight repository operations.
    """

    @abstractmethod
    async def get_insights_by_user(self, user_id: UUID) -> List[Insight]:
        """
        Get all insights for a user.

        Args:
            user_id: User ID

        Returns:
            List of insights
        """
        pass
