from typing import Optional
from uuid import UUID
from ...domain.ports import TransactionBatchRepositoryPort
from ..dto import BatchStatusDTO


class GetBatchStatusUseCase:
    def __init__(self, batch_repo: TransactionBatchRepositoryPort):
        self.batch_repo = batch_repo

    async def execute(self, batch_id: UUID) -> Optional[BatchStatusDTO]:
        """Get the status of a transaction batch"""
        batch = await self.batch_repo.get_by_id(batch_id)
        if not batch:
            return None

        return BatchStatusDTO(
            id_batch=batch.id_batch,
            process_status=batch.process_status,
            start_date=batch.start_date,
            end_date=batch.end_date,
            batch_size=batch.batch_size,
            processed_percentage=batch.processed_percentage,
        )
