from decimal import Decimal
from typing import Optional

from src.domain.entities import Transaction, Insight, TransactionBatch
from src.domain.value_objects import UserId, BatchId, Money, CategoryId
from src.infrastructure.database.models import (
    TransactionModel, 
    InsightModel, 
    TransactionBatchModel
)


class TransactionMapper:
    """Maps between Transaction entity and TransactionModel"""
    
    @staticmethod
    def to_entity(model: TransactionModel) -> Transaction:
        """Convert SQLAlchemy model to domain entity"""
        return Transaction(
            id_transaction=model.id_transaction,
            id_user=UserId(value=model.id_user),
            id_category=CategoryId(value=model.id_category),
            value=Money(amount=Decimal(str(model.value))),
            transaction_name=model.transaction_name,
            transaction_date=model.transaction_date,
            transaction_type=model.transaction_type,
            id_batch=BatchId(value=model.id_batch) if model.id_batch else None,
            id_bank=model.id_bank,
            category_description=model.category.description if model.category else None
        )
    
    @staticmethod
    def to_model(entity: Transaction) -> TransactionModel:
        """Convert domain entity to SQLAlchemy model"""
        return TransactionModel(
            id_transaction=entity.id_transaction,
            id_user=entity.id_user.value,
            id_category=entity.id_category.value,
            value=float(entity.value.amount),
            transaction_name=entity.transaction_name,
            transaction_date=entity.transaction_date,
            transaction_type=entity.transaction_type,
            id_batch=entity.id_batch.value if entity.id_batch else None,
            id_bank=entity.id_bank
        )


class InsightMapper:
    """Maps between Insight entity and InsightModel"""
    
    @staticmethod
    def to_entity(model: InsightModel) -> Insight:
        """Convert SQLAlchemy model to domain entity"""
        return Insight(
            id_insight=model.id_insight,
            id_user=UserId(value=model.id_user),
            id_category=CategoryId(value=model.id_category),
            title=model.title,
            text=model.text,
            relevance=model.relevance,
            created_at=model.created_at
        )
    
    @staticmethod
    def to_model(entity: Insight) -> InsightModel:
        """Convert domain entity to SQLAlchemy model"""
        return InsightModel(
            id_insight=entity.id_insight,
            id_user=entity.id_user.value,
            id_category=entity.id_category.value,
            title=entity.title,
            text=entity.text,
            relevance=entity.relevance,
            created_at=entity.created_at
        )


class TransactionBatchMapper:
    """Maps between TransactionBatch entity and TransactionBatchModel"""
    
    @staticmethod
    def to_entity(model: TransactionBatchModel) -> TransactionBatch:
        """Convert SQLAlchemy model to domain entity"""
        return TransactionBatch(
            id_batch=BatchId(value=model.id_batch),
            process_status=model.process_status,
            start_date=model.start_date,
            end_date=model.end_date,
            batch_size=model.batch_size
        )
    
    @staticmethod
    def to_model(entity: TransactionBatch) -> TransactionBatchModel:
        """Convert domain entity to SQLAlchemy model"""
        return TransactionBatchModel(
            id_batch=entity.id_batch.value,
            process_status=entity.process_status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            batch_size=entity.batch_size
        )
