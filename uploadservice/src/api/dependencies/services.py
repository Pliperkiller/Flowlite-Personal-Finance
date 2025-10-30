import os
from ...infrastructure.classifier import SimpleClassifier
from ...infrastructure.messaging import RabbitMQProducer
from ...domain.ports import ClassifierPort, MessageBrokerPort


def get_classifier() -> ClassifierPort:
    """
    Dependency for getting the transaction classifier.

    Returns:
        ClassifierPort: Classifier instance for categorizing transactions
    """
    return SimpleClassifier()


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
