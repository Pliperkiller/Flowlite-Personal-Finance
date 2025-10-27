import logging
from uuid import UUID

from src.application.dtos import BatchProcessedMessage
from src.application.exceptions import (
    ApplicationError,
    TransactionNotFoundError,
    BatchNotFoundError,
    BatchNotProcessedError,
    LLMServiceError,
    InsightGenerationError
)
from src.domain.value_objects import UserId, BatchId
from src.infrastructure.di.container import Container

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Handles incoming messages from RabbitMQ
    
    This is the interface adapter that connects the messaging infrastructure
    to the application use cases
    """
    
    def __init__(self, container: Container):
        """
        Initialize message handler
        
        Args:
            container: Dependency injection container
        """
        self.container = container
    
    def handle_batch_processed(self, message: BatchProcessedMessage) -> None:
        """
        Handles a batch processed message
        
        Args:
            message: The batch processed message from RabbitMQ
            
        Raises:
            ApplicationError: If processing fails
        """
        logger.info(f"Processing batch_id={message.batch_id}, user_id={message.user_id}")
        
        try:
            # Convert to value objects
            user_id = UserId(value=message.user_id)
            batch_id = BatchId(value=message.batch_id)

            # Create use case with fresh session
            with self.container.get_use_case_with_session() as use_case:
                # Execute use case
                result = use_case.execute(user_id=user_id, batch_id=batch_id)

                logger.info(
                    f"✅ Successfully generated {result.insights_generated} insights "
                    f"for user={message.user_id}, batch={message.batch_id}"
                )

                # Log top insights
                for insight in result.insights[:3]:  # Log top 3
                    logger.info(
                        f"   - [{insight.relevance}/10] {insight.title}"
                    )
            
        except TransactionNotFoundError as e:
            logger.warning(f"No transactions found: {e}")
            # Not an error - just skip
            
        except (BatchNotFoundError, BatchNotProcessedError) as e:
            logger.error(f"Batch error: {e}")
            raise ApplicationError(f"Batch processing error: {str(e)}")
        
        except LLMServiceError as e:
            logger.error(f"LLM service error: {e}", exc_info=True)
            raise ApplicationError(f"LLM error: {str(e)}")
        
        except InsightGenerationError as e:
            logger.error(f"Insight generation error: {e}", exc_info=True)
            raise ApplicationError(f"Generation error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise ApplicationError(f"Unexpected error: {str(e)}")
