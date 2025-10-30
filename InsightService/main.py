#!/usr/bin/env python3
"""
Financial Insights Service - Main Entry Point

This service:
1. Exposes HTTP API for health checks and monitoring (FastAPI)
2. Consumes batch processed events from RabbitMQ
3. Generates financial insights using an LLM
4. Persists insights to the database
"""

import logging
import signal
import sys
import threading
from typing import Optional
import uvicorn

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging
from src.infrastructure.di.container import Container
from src.interfaces.message_handler import MessageHandler
from src.interfaces.api import create_app

logger = logging.getLogger(__name__)

# Global references for graceful shutdown
consumer: Optional[object] = None
api_server: Optional[object] = None
should_exit = threading.Event()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    should_exit.set()

    if consumer:
        try:
            consumer.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting consumer: {e}")

    sys.exit(0)


def start_api_server(app, settings):
    """Start FastAPI server in a separate thread"""
    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")

    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        access_log=True
    )

    server = uvicorn.Server(config)
    server.run()


def start_rabbitmq_consumer(container, message_handler):
    """Start RabbitMQ consumer"""
    global consumer
    consumer = container.rabbitmq_consumer

    logger.info("Connecting to RabbitMQ...")
    consumer.connect()

    logger.info(f"Listening for messages on queue: {container.settings.rabbitmq_queue}")

    # Start consuming messages (blocking)
    consumer.start_consuming(message_handler.handle_batch_processed)


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
        logger.info(f"API Server: http://{settings.api_host}:{settings.api_port}")
        logger.info("=" * 60)

        # Create dependency container
        container = Container.create(settings)

        # Create FastAPI app
        app = create_app(container)

        # Create message handler
        message_handler = MessageHandler(container)

        # Start API server in a separate thread
        api_thread = threading.Thread(
            target=start_api_server,
            args=(app, settings),
            daemon=True,
            name="APIServerThread"
        )
        api_thread.start()
        logger.info("API server thread started")

        # Give API server time to start
        import time
        time.sleep(2)

        logger.info("Service started successfully")
        logger.info(f"API available at: http://localhost:{settings.api_port}/health")
        logger.info(f"API docs at: http://localhost:{settings.api_port}/docs")
        logger.info("Press Ctrl+C to stop")

        # Start RabbitMQ consumer (blocking, runs in main thread)
        start_rabbitmq_consumer(container, message_handler)

    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        should_exit.set()
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    main()
