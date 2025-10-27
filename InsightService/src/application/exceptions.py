class ApplicationError(Exception):
    """Base exception for application layer errors"""
    pass


class TransactionNotFoundError(ApplicationError):
    """Raised when no transactions are found for a user"""
    pass


class BatchNotFoundError(ApplicationError):
    """Raised when a batch is not found"""
    pass


class BatchNotProcessedError(ApplicationError):
    """Raised when attempting to generate insights for an unprocessed batch"""
    pass


class LLMServiceError(ApplicationError):
    """Raised when the LLM service encounters an error"""
    pass


class InsightGenerationError(ApplicationError):
    """Raised when insight generation fails"""
    pass
