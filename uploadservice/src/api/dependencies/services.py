import os
import logging
from ...infrastructure.classifier import SimpleClassifier, MLClassifier
from ...infrastructure.messaging import RabbitMQProducer
from ...domain.ports import ClassifierPort, MessageBrokerPort

logger = logging.getLogger(__name__)


def get_classifier() -> ClassifierPort:
    """
    Dependency for getting the transaction classifier.

    Uses MLClassifier by default (ML-based classification with 99.7% accuracy).
    Can be switched to SimpleClassifier via USE_SIMPLE_CLASSIFIER env var for testing.

    Environment Variables:
        USE_SIMPLE_CLASSIFIER: Set to "true" to use SimpleClassifier instead of MLClassifier
        ML_MODELS_PATH: Path to ML model files (default: uploadservice/models/)

    Returns:
        ClassifierPort: Classifier instance for categorizing transactions
    """
    use_simple = os.getenv("USE_SIMPLE_CLASSIFIER", "false").lower() == "true"

    if use_simple:
        logger.info("Using SimpleClassifier (returns 'Other' for all transactions)")
        return SimpleClassifier()
    else:
        logger.info("Using MLClassifier (ML-based classification)")
        return MLClassifier()


def get_message_broker() -> MessageBrokerPort:
    """
    Dependency for getting the message broker.

    Returns:
        MessageBrokerPort: RabbitMQ producer instance
    """
    return RabbitMQProducer(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        username=os.getenv("RABBITMQ_USERNAME", "guest"),
        password=os.getenv("RABBITMQ_PASSWORD", "guest"),
        queue_name=os.getenv("RABBITMQ_QUEUE_NAME", "batch_processed"),
    )
