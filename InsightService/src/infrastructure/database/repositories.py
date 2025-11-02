from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
import logging

from src.domain.repositories import (
    TransactionRepository,
    InsightRepository,
    BatchRepository
)
from src.domain.entities import Transaction, Insight, TransactionBatch
from src.domain.value_objects import UserId, BatchId, CategoryId
from src.infrastructure.database.models import (
    TransactionModel,
    InsightModel,
    TransactionBatchModel,
    InsightCategoryModel
)
from src.infrastructure.database.mappers import (
    TransactionMapper,
    InsightMapper,
    TransactionBatchMapper
)

logger = logging.getLogger(__name__)


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def find_by_user_and_batch(
        self, 
        user_id: UserId, 
        batch_id: BatchId
    ) -> List[Transaction]:
        """Gets all transactions for a user in a specific batch"""
        logger.info(f"Fetching transactions for user={user_id}, batch={batch_id}")
        
        models = (
            self._session.query(TransactionModel)
            .options(joinedload(TransactionModel.category))
            .filter(
                TransactionModel.id_user == user_id.value,
                TransactionModel.id_batch == batch_id.value
            )
            .all()
        )
        
        entities = [TransactionMapper.to_entity(model) for model in models]
        logger.info(f"Found {len(entities)} transactions")
        
        return entities
    
    def find_by_user(
        self, 
        user_id: UserId, 
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Gets transactions for a user (optionally limited)"""
        logger.info(f"Fetching transactions for user={user_id}, limit={limit}")
        
        query = (
            self._session.query(TransactionModel)
            .options(joinedload(TransactionModel.category))
            .filter(TransactionModel.id_user == user_id.value)
            .order_by(TransactionModel.transaction_date.desc())
        )
        
        if limit:
            query = query.limit(limit)
        
        models = query.all()
        entities = [TransactionMapper.to_entity(model) for model in models]
        
        logger.info(f"Found {len(entities)} transactions")
        return entities


class SQLAlchemyInsightRepository(InsightRepository):
    """SQLAlchemy implementation of InsightRepository"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, insight: Insight) -> Insight:
        """Persists a new insight"""
        logger.info(f"Saving insight id={insight.id_insight}")
        
        model = InsightMapper.to_model(insight)
        self._session.add(model)
        self._session.flush()  # Get the ID without committing
        
        return InsightMapper.to_entity(model)
    
    def save_batch(self, insights: List[Insight]) -> List[Insight]:
        """Persists multiple insights efficiently"""
        logger.info(f"Saving {len(insights)} insights in batch")

        models = [InsightMapper.to_model(insight) for insight in insights]
        self._session.bulk_save_objects(models, return_defaults=True)
        self._session.flush()

        # Return the entities (in a real scenario, you might want to query them back)
        return insights

    def delete_by_user(self, user_id: UserId) -> int:
        """Deletes all insights for a user"""
        logger.info(f"Deleting all insights for user={user_id}")

        deleted_count = (
            self._session.query(InsightModel)
            .filter(InsightModel.id_user == user_id.value)
            .delete()
        )
        self._session.flush()

        logger.info(f"Deleted {deleted_count} insights for user={user_id}")
        return deleted_count
    
    def find_by_user(self, user_id: UserId) -> List[Insight]:
        """Gets all insights for a user"""
        logger.info(f"Fetching insights for user={user_id}")

        models = (
            self._session.query(InsightModel)
            .filter(InsightModel.id_user == user_id.value)
            .order_by(InsightModel.relevance.desc(), InsightModel.created_at.desc())
            .all()
        )

        entities = [InsightMapper.to_entity(model) for model in models]
        logger.info(f"Found {len(entities)} insights")

        return entities

    def get_category_id_by_description(self, description: str) -> Optional[CategoryId]:
        """Gets category ID by description"""
        logger.info(f"Fetching category ID for description={description}")

        model = (
            self._session.query(InsightCategoryModel)
            .filter(InsightCategoryModel.description == description)
            .first()
        )

        if not model:
            logger.warning(f"Category with description '{description}' not found")
            return None

        return CategoryId(value=model.id_category)


class SQLAlchemyBatchRepository(BatchRepository):
    """SQLAlchemy implementation of BatchRepository"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def find_by_id(self, batch_id: BatchId) -> Optional[TransactionBatch]:
        """Finds a batch by its ID"""
        logger.info(f"Fetching batch id={batch_id}")
        
        model = (
            self._session.query(TransactionBatchModel)
            .filter(TransactionBatchModel.id_batch == batch_id.value)
            .first()
        )
        
        if not model:
            logger.warning(f"Batch {batch_id} not found")
            return None
        
        return TransactionBatchMapper.to_entity(model)
