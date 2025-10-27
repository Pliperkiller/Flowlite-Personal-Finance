#!/usr/bin/env python3
"""
Financial Insights Service - Main Entry Point

This service consumes batch processed events from RabbitMQ,
generates financial insights using an LLM, and persists them to the database.
"""

import logging
import signal
import sys
from typing import Optional

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging
from src.infrastructure.di.container import Container
from src.interfaces.message_handler import MessageHandler

logger = logging.getLogger(__name__)

# Global reference for graceful shutdown
consumer: Optional[object] = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if consumer:
        consumer.disconnect()
    sys.exit(0)


def main():
    """Main entry point for the service"""
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load settings
        settings = get_settings()
        
        # Setup logging
        setup_logging(level=settings.log_level, log_format=settings.log_format)
        
        logger.info("=" * 60)
        logger.info("Starting Financial Insights Service")
        logger.info("=" * 60)
        logger.info(f"Database: {settings.database_url.split('@')[-1]}")  # Hide credentials
        logger.info(f"RabbitMQ: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        logger.info(f"LLM Model: {settings.llm_model}")
        logger.info(f"Queue: {settings.rabbitmq_queue}")
        logger.info("=" * 60)
        
        # Create dependency container
        container = Container.create(settings)
        
        # Create message handler
        message_handler = MessageHandler(container)
        
        # Connect to RabbitMQ
        global consumer
        consumer = container.rabbitmq_consumer
        
        logger.info("Connecting to RabbitMQ...")
        consumer.connect()
        
        logger.info("Service started successfully")
        logger.info(f"Listening for messages on queue: {settings.rabbitmq_queue}")
        logger.info("Press Ctrl+C to stop")
        
        # Start consuming messages
        consumer.start_consuming(message_handler.handle_batch_processed)
        
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    main()
