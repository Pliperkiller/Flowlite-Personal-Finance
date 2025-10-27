from dataclasses import dataclass
from contextlib import contextmanager
import logging

from src.infrastructure.config.settings import Settings
from src.infrastructure.config.database import DatabaseConfig
from src.infrastructure.database.repositories import (
    SQLAlchemyTransactionRepository,
    SQLAlchemyInsightRepository,
    SQLAlchemyBatchRepository
)
from src.infrastructure.llm.ollama_service import OllamaService
from src.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from src.application.services.transaction_aggregator import TransactionAggregator
from src.application.services.category_mapper import CategoryMapper
from src.application.use_cases.generate_insights_use_case import GenerateInsightsUseCase

logger = logging.getLogger(__name__)


@dataclass
class Container:
    """
    Dependency Injection Container
    
    Manages the lifecycle and dependencies of all application components
    following the Dependency Inversion Principle
    """
    
    settings: Settings
    db_config: DatabaseConfig
    
    # Repositories (created per request via session)
    # These are factory methods, not instances
    
    # Services
    transaction_aggregator: TransactionAggregator
    category_mapper: CategoryMapper
    llm_service: OllamaService
    
    # Infrastructure
    rabbitmq_consumer: RabbitMQConsumer
    
    @classmethod
    def create(cls, settings: Settings) -> 'Container':
        """
        Factory method to create and wire all dependencies
        
        Args:
            settings: Application settings
            
        Returns:
            Configured container with all dependencies
        """
        logger.info("Initializing dependency container...")
        
        # Database configuration
        db_config = DatabaseConfig(
            database_url=settings.database_url,
            echo=settings.database_echo
        )
        
        # Services
        transaction_aggregator = TransactionAggregator()
        category_mapper = CategoryMapper()
        
        # LLM Service
        llm_service = OllamaService(
            host=settings.ollama_host,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            timeout=settings.llm_timeout
        )
        
        # RabbitMQ Consumer
        rabbitmq_consumer = RabbitMQConsumer(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            username=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            queue_name=settings.rabbitmq_queue,
            prefetch_count=settings.rabbitmq_prefetch_count
        )
        
        logger.info("Dependency container initialized successfully")
        
        return cls(
            settings=settings,
            db_config=db_config,
            transaction_aggregator=transaction_aggregator,
            category_mapper=category_mapper,
            llm_service=llm_service,
            rabbitmq_consumer=rabbitmq_consumer
        )
    
    @contextmanager
    def get_use_case_with_session(self):
        """
        Context manager that provides a use case with a managed database session

        Usage:
            with container.get_use_case_with_session() as use_case:
                result = use_case.execute(...)

        Yields:
            Configured use case instance with managed session
        """
        with self.db_config.get_session() as session:
            # Create repositories with the session
            transaction_repo = SQLAlchemyTransactionRepository(session)
            insight_repo = SQLAlchemyInsightRepository(session)
            batch_repo = SQLAlchemyBatchRepository(session)

            # Create category mapper with repository for database lookups
            category_mapper = CategoryMapper(category_repository=insight_repo)

            # Create and yield use case
            use_case = GenerateInsightsUseCase(
                transaction_repository=transaction_repo,
                insight_repository=insight_repo,
                batch_repository=batch_repo,
                llm_service=self.llm_service,
                transaction_aggregator=self.transaction_aggregator,
                category_mapper=category_mapper
            )
            yield use_case
