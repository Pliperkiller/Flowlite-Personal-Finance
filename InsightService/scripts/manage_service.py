#!/usr/bin/env python3
"""
Service management script for development
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import subprocess
import logging

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging

logger = logging.getLogger(__name__)


def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        settings = get_settings()
        response = requests.get(f"{settings.ollama_host}/api/tags", timeout=2)
        if response.status_code == 200:
            logger.info("Ollama is running")
            return True
    except:
        pass
    
    logger.error("Ollama is not running")
    logger.info("   Start it with: ollama serve")
    return False


def check_rabbitmq():
    """Check if RabbitMQ is accessible"""
    try:
        import pika
        settings = get_settings()
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            connection_attempts=1,
            socket_timeout=2
        )
        connection = pika.BlockingConnection(parameters)
        connection.close()
        logger.info("RabbitMQ is accessible")
        return True
    except:
        pass
    
    logger.error("RabbitMQ is not accessible")
    logger.info(f"   Check connection to {settings.rabbitmq_host}:{settings.rabbitmq_port}")
    return False


def check_database():
    """Check if database is accessible"""
    try:
        from sqlalchemy import text
        from src.infrastructure.config.database import DatabaseConfig
        settings = get_settings()
        db_config = DatabaseConfig(database_url=settings.database_url)
        with db_config.get_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("Database is accessible")
        return True
    except Exception as e:
        logger.error(f"Database is not accessible: {e}")
        return False


def check_dependencies():
    """Check all service dependencies"""
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("Checking service dependencies")
    logger.info("=" * 60)
    
    checks = {
        "Database": check_database(),
        "RabbitMQ": check_rabbitmq(),
        "Ollama": check_ollama()
    }
    
    logger.info("=" * 60)
    
    all_ok = all(checks.values())
    
    if all_ok:
        logger.info("All dependencies are ready!")
        logger.info("\n Start the service with: python main.py")
    else:
        logger.error("Some dependencies are not ready")
        logger.error("   Fix the issues above before starting the service")
    
    logger.info("=" * 60)
    
    return all_ok


def show_status():
    """Show service status"""
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("Service Status")
    logger.info("=" * 60)
    
    check_dependencies()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage_service.py <command>")
        print("\nCommands:")
        print("  check    - Check all dependencies")
        print("  status   - Show service status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        success = check_dependencies()
        sys.exit(0 if success else 1)
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
