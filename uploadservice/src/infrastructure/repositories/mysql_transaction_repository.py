from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import TransactionRepositoryPort
from ...domain.entities import Transaction
from ..database.models import TransactionModel


class MySQLTransactionRepository(TransactionRepositoryPort):
    """MySQL implementation of the Transaction repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """Save a batch of transactions to the database"""
        models = [self._to_model(tx) for tx in transactions]
        self.session.add_all(models)
        await self.session.flush()
        # Refresh to load generated IDs
        for model in models:
            await self.session.refresh(model)
        return [self._to_entity(model) for model in models]

    async def get_by_id(self, id_transaction: UUID) -> Optional[Transaction]:
        """Get a transaction by its ID"""
        result = await self.session.execute(
            select(TransactionModel).where(TransactionModel.id_transaction == str(id_transaction))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Transaction) -> TransactionModel:
        """Convert domain entity to database model"""
        return TransactionModel(
            id_transaction=str(entity.id_transaction) if entity.id_transaction else None,
            id_user=str(entity.id_user),
            id_bank=entity.id_bank,  # Bank ID is already a string
            id_category=entity.id_category,  # Category ID is already a string
            id_batch=str(entity.id_batch) if entity.id_batch else None,
            transaction_date=entity.transaction_date,
            transaction_name=entity.transaction_name,
            value=entity.value,
            transaction_type=entity.transaction_type,
        )

    def _to_entity(self, model: TransactionModel) -> Transaction:
        """Convert database model to domain entity"""
        return Transaction(
            id_transaction=UUID(model.id_transaction) if model.id_transaction else None,
            id_user=UUID(model.id_user),
            id_category=model.id_category,  # Category ID is a string, not UUID
            id_bank=model.id_bank,
            id_batch=UUID(model.id_batch) if model.id_batch else None,
            transaction_date=model.transaction_date,
            transaction_name=model.transaction_name,
            value=model.value,
            transaction_type=model.transaction_type,
        )
