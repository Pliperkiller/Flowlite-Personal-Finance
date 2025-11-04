from abc import ABC, abstractmethod
from uuid import UUID
from ..entities import Dashboard


class DashboardRepositoryPort(ABC):
    """
    Port for dashboard repository operations.
    """

    @abstractmethod
    async def get_dashboard_by_user(self, user_id: UUID) -> Dashboard:
        """
        Get complete dashboard data for a user.
        Includes:
        - User information
        - Balance summary (total, incomes, expenses)
        - Last 3 transactions
        - Top 2 recommendations by relevance
        """
        pass
