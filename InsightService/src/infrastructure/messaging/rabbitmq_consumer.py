import pika
import json
import logging
from typing import Callable, Optional
from uuid import UUID

from src.application.dtos import BatchProcessedMessage
from src.application.exceptions import ApplicationError

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """RabbitMQ consumer for batch processed events"""
    
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        queue_name: str,
        prefetch_count: int = 1
    ):
        """
        Initialize RabbitMQ consumer
        
        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            queue_name: Queue to consume from
            prefetch_count: Number of messages to prefetch
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count
        
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        
        logger.info(f"Initialized RabbitMQ consumer for queue={queue_name}")
    
    def connect(self):
        """Establishes connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (idempotent)
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise ApplicationError(f"Cannot connect to RabbitMQ: {str(e)}")
    
    def disconnect(self):
        """Closes RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")
    
    def _parse_message(self, body: bytes) -> BatchProcessedMessage:
        """
        Parses message body into BatchProcessedMessage DTO
        
        Args:
            body: Raw message body
            
        Returns:
            Parsed BatchProcessedMessage
            
        Raises:
            ValueError: If message format is invalid
        """
        try:
            data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['batch_id', 'status', 'userid']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse UUIDs
            batch_id = UUID(data['batch_id'])
            user_id = UUID(data['userid'])
            
            return BatchProcessedMessage(
                batch_id=batch_id,
                status=data['status'],
                user_id=user_id
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Invalid message format: {e}")
            raise ValueError(f"Invalid message format: {str(e)}")
    
    def start_consuming(self, message_handler: Callable[[BatchProcessedMessage], None]):
        """
        Starts consuming messages from the queue
        
        Args:
            message_handler: Callback function to process messages
                            Should accept BatchProcessedMessage as parameter
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")
        
        def callback(ch, method, properties, body):
            """Internal callback for message processing"""
            try:
                logger.info(f"Received message: {body.decode('utf-8')[:100]}...")
                
                # Parse message
                message = self._parse_message(body)
                
                # Only process if status is 'Processed'
                if not message.is_processed():
                    logger.info(f"Skipping message with status={message.status}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Call the handler
                message_handler(message)
                
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Successfully processed message for batch={message.batch_id}")
                
            except ValueError as e:
                # Invalid message format - reject and don't requeue
                logger.error(f"Invalid message format: {e}")
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                
            except Exception as e:
                # Processing error - reject and requeue for retry
                logger.error(f"Error processing message: {e}", exc_info=True)
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
        
        logger.info(f"Starting to consume from queue={self.queue_name}")
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
        finally:
            self.disconnect()

