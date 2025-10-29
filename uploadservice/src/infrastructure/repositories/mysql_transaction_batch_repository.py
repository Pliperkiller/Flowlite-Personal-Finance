from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import TransactionBatchRepositoryPort
from ...domain.entities import TransactionBatch
from ..database.models import TransactionBatchModel


class MySQLTransactionBatchRepository(TransactionBatchRepositoryPort):
    """MySQL implementation of the Transaction Batch repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, batch: TransactionBatch) -> TransactionBatch:
        """Save a transaction batch to the database"""
        model = self._to_model(batch)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, id_batch: UUID) -> Optional[TransactionBatch]:
        """Get a transaction batch by its ID"""
        result = await self.session.execute(
            select(TransactionBatchModel).where(TransactionBatchModel.id_batch == str(id_batch))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, batch: TransactionBatch) -> TransactionBatch:
        """Update a transaction batch in the database"""
        result = await self.session.execute(
            select(TransactionBatchModel).where(TransactionBatchModel.id_batch == str(batch.id_batch))
        )
        model = result.scalar_one_or_none()
        if model:
            model.process_status = batch.process_status
            model.end_date = batch.end_date
            model.batch_size = batch.batch_size
            await self.session.flush()
            await self.session.refresh(model)
            return self._to_entity(model)
        return batch

    def _to_model(self, entity: TransactionBatch) -> TransactionBatchModel:
        """Convert domain entity to database model"""
        return TransactionBatchModel(
            id_batch=str(entity.id_batch) if entity.id_batch else None,
            process_status=entity.process_status,
            start_date=entity.start_date,
            end_date=entity.end_date,
            batch_size=entity.batch_size,
        )

    def _to_entity(self, model: TransactionBatchModel) -> TransactionBatch:
        """Convert database model to domain entity"""
        return TransactionBatch(
            id_batch=UUID(model.id_batch) if model.id_batch else None,
            process_status=model.process_status,
            start_date=model.start_date,
            end_date=model.end_date,
            batch_size=model.batch_size,
        )
