import json
import logging
from typing import Optional
from uuid import UUID
import aio_pika
from aio_pika import Connection, Channel, ExchangeType

from ...domain.ports import MessageBrokerPort

logger = logging.getLogger(__name__)


class RabbitMQProducer(MessageBrokerPort):
    """RabbitMQ producer implementation for publishing batch processed events"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        queue_name: str,
    ):
        """
        Initialize RabbitMQ producer.

        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            queue_name: Queue to publish messages to
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name

        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None

        logger.info(f"Initialized RabbitMQ producer for queue={queue_name}")

    async def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            # Create connection URL
            url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/"

            # Establish connection
            self.connection = await aio_pika.connect_robust(
                url,
                heartbeat=600,
                client_properties={"connection_name": "upload-service-producer"},
            )

            # Create channel
            self.channel = await self.connection.channel()

            # Declare queue (idempotent)
            await self.channel.declare_queue(
                self.queue_name,
                durable=True,
            )

            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to RabbitMQ"""
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()

            if self.connection and not self.connection.is_closed:
                await self.connection.close()

            logger.info("Disconnected from RabbitMQ")

        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")

    async def publish_batch_processed(
        self, batch_id: UUID, user_id: UUID, status: str
    ) -> None:
        """
        Publish a batch processed event to RabbitMQ.

        The message format matches what the InsightService consumer expects:
        {
            "batch_id": "uuid-string",
            "status": "Processed",
            "userid": "uuid-string"
        }

        Args:
            batch_id: UUID of the processed batch
            user_id: UUID of the user who owns the batch
            status: Status of the batch ("Processed", "Error", etc.)

        Raises:
            Exception: If publishing fails
        """
        if not self.channel or self.channel.is_closed:
            logger.warning("Channel not connected, attempting to reconnect...")
            await self.connect()

        try:
            # Create message payload matching InsightService format
            message = {
                "batch_id": str(batch_id),
                "status": status,
                "userid": str(user_id),
            }

            # Serialize to JSON
            message_body = json.dumps(message).encode("utf-8")

            # Publish message
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Make message persistent
                    content_type="application/json",
                ),
                routing_key=self.queue_name,
            )

            logger.info(
                f"Published batch processed event: batch_id={batch_id}, "
                f"user_id={user_id}, status={status}"
            )

        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {e}")
            raise
