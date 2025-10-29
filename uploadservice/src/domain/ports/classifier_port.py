from abc import ABC, abstractmethod


class ClassifierPort(ABC):
    @abstractmethod
    async def classify(self, description: str) -> str:
        """
        Classify a transaction based on its description
        Returns the category name
        """
        pass
