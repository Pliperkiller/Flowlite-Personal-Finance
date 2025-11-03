from abc import ABC, abstractmethod
from typing import List
from ..entities import Bank


class BankRepositoryPort(ABC):
    """
    Port for bank repository operations.
    """

    @abstractmethod
    async def get_all_banks(self) -> List[Bank]:
        """
        Get all available banks.

        Returns:
            List of banks
        """
        pass
