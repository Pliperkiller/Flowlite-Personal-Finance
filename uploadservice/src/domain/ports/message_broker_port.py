from abc import ABC, abstractmethod
from uuid import UUID


class MessageBrokerPort(ABC):
    """Port for publishing messages to a message broker"""

    @abstractmethod
    async def publish_batch_processed(
        self, batch_id: UUID, user_id: UUID, status: str
    ) -> None:
        """
        Publish a batch processed event to the message broker.

        Args:
            batch_id: UUID of the processed batch
            user_id: UUID of the user who owns the batch
            status: Status of the batch ("Processed", "Error", etc.)

        Raises:
            Exception: If publishing fails
        """
        pass

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the message broker"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the message broker"""
        pass
