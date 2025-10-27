#!/usr/bin/env python3
"""
Send a test message to RabbitMQ to trigger insight generation
"""

import sys
from pathlib import Path
import json
import logging
from uuid import UUID

import pika

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging

logger = logging.getLogger(__name__)


def send_test_message(user_id: str, batch_id: str):
    """
    Send a test batch processed message to RabbitMQ
    
    Args:
        user_id: User UUID as string
        batch_id: Batch UUID as string
    """
    
    settings = get_settings()
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("Sending test message to RabbitMQ")
    logger.info("=" * 60)
    
    # Validate UUIDs
    try:
        UUID(user_id)
        UUID(batch_id)
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        sys.exit(1)
    
    # Create message
    message = {
        "batch_id": batch_id,
        "status": "Processed",
        "userid": user_id
    }
    
    logger.info(f"Message content: {json.dumps(message, indent=2)}")
    
    # Connect to RabbitMQ
    try:
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declare queue (idempotent)
        channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=settings.rabbitmq_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        logger.info(f"Message sent to queue: {settings.rabbitmq_queue}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("   1. Make sure your service is running: python main.py")
        logger.info("   2. Check the logs for insight generation")
        logger.info("   3. Query the Insights table to see results")
        logger.info("=" * 60)
        
        connection.close()
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/send_test_message.py <user_id> <batch_id>")
        print("\nExample:")
        print("  python scripts/send_test_message.py 6df1b111-0f42-47ef-8b31-602815dbe341 71e8b5d7-05ab-4edf-b4e3-1ff074d29172")
        sys.exit(1)
    
    user_id = sys.argv[1]
    batch_id = sys.argv[2]
    
    send_test_message(user_id, batch_id)
