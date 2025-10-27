#!/usr/bin/env python3
"""
Test script to verify all components are working
"""

import logging
from decimal import Decimal

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging
from src.infrastructure.di.container import Container
from src.domain.llm_models import TransactionSummary

logger = logging.getLogger(__name__)


def test_llm_service():
    """Test the LLM service with sample data"""
    
    # Setup
    settings = get_settings()
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("Testing Financial Insights Service Components")
    logger.info("=" * 60)
    
    # Create container
    container = Container.create(settings)
    
    # Create sample transaction summaries
    sample_transactions = [
        TransactionSummary(
            category="Restaurantes",
            total_amount=Decimal("1500000"),
            transaction_count=12,
            transaction_type="expense"
        ),
        TransactionSummary(
            category="Transporte",
            total_amount=Decimal("800000"),
            transaction_count=20,
            transaction_type="expense"
        ),
        TransactionSummary(
            category="Entretenimiento",
            total_amount=Decimal("600000"),
            transaction_count=8,
            transaction_type="expense"
        ),
        TransactionSummary(
            category="Salario",
            total_amount=Decimal("5000000"),
            transaction_count=1,
            transaction_type="income"
        )
    ]
    
    logger.info("Sample transaction data:")
    for trans in sample_transactions:
        logger.info(f"   - {trans.category}: ${trans.total_amount:,.0f} COP ({trans.transaction_count} txns)")
    
    logger.info("")
    logger.info("Calling LLM service...")
    
    try:
        # Test LLM service
        recommendations = container.llm_service.generate_recommendations(sample_transactions)
        
        logger.info(f"Generated {len(recommendations)} recommendations:")
        logger.info("")
        
        for idx, rec in enumerate(recommendations, 1):
            logger.info(f"{idx}. [{rec.relevance}/10] {rec.title}")
            logger.info(f"   Category: {rec.category}")
            logger.info(f"   Comment: {rec.comment}")
            logger.info("")
        
        logger.info("=" * 60)
        logger.info("All tests passed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    
    return True


if __name__ == "__main__":
    success = test_llm_service()
    exit(0 if success else 1)

