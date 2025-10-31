from typing import List, Callable
import asyncio
import logging
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
from ...domain.ports import (
    TransactionRepositoryPort,
    BankRepositoryPort,
    CategoryRepositoryPort,
    TransactionBatchRepositoryPort,
    ExcelParserPort,
    ClassifierPort,
    MessageBrokerPort,
)
from ...domain.entities import Transaction, TransactionBatch


class ProcessFilesUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepositoryPort,
        bank_repo: BankRepositoryPort,
        category_repo: CategoryRepositoryPort,
        batch_repo: TransactionBatchRepositoryPort,
        classifier: ClassifierPort,
        message_broker: MessageBrokerPort,
        session_factory: sessionmaker = None,
    ):
        self.transaction_repo = transaction_repo
        self.bank_repo = bank_repo
        self.category_repo = category_repo
        self.batch_repo = batch_repo
        self.classifier = classifier
        self.message_broker = message_broker
        self.session_factory = session_factory

    async def execute(
        self,
        files_content: List[bytes],
        parser: ExcelParserPort,
        user_id: UUID,
    ) -> UUID:
        """
        Process Excel files and return the batch ID
        """
        # 1. Get the bank by name (bank_code is now bank_name)
        bank_name = parser.get_bank_code()  # This should return bank name
        bank = await self.bank_repo.get_by_name(bank_name)
        if not bank:
            raise ValueError(f"Bank with name {bank_name} not found")

        # 2. Parse all files
        all_raw_transactions = []
        for file_content in files_content:
            raw_transactions = parser.parse(file_content)
            all_raw_transactions.extend(raw_transactions)

        # 3. Create the batch
        batch = TransactionBatch(
            id_batch=None,
            process_status="pending",
            start_date=datetime.now(),
            end_date=None,
            batch_size=len(all_raw_transactions),
        )
        batch = await self.batch_repo.save(batch)

        # 4. Process in background (in a real application you would use Celery or similar)
        asyncio.create_task(
            self._process_transactions_async(
                all_raw_transactions, batch, user_id, bank.id_bank
            )
        )

        return batch.id_batch

    async def _process_transactions_async(
        self, raw_transactions, batch: TransactionBatch, user_id: UUID, bank_id: str
    ):
        """Process transactions in batches of 500"""
        # Create a new session for this background task
        async with self.session_factory() as session:
            try:
                # Import repositories
                from ...infrastructure.repositories import (
                    MySQLTransactionRepository,
                    MySQLCategoryRepository,
                    MySQLTransactionBatchRepository,
                )

                # Create repository instances with the new session
                transaction_repo = MySQLTransactionRepository(session)
                category_repo = MySQLCategoryRepository(session)
                batch_repo = MySQLTransactionBatchRepository(session)

                batch.process_status = "processing"
                await batch_repo.update(batch)
                await session.commit()

                BATCH_SIZE = 500
                for i in range(0, len(raw_transactions), BATCH_SIZE):
                    chunk = raw_transactions[i : i + BATCH_SIZE]

                    # Classify and create transactions
                    transactions = []
                    for raw_tx in chunk:
                        # Classify
                        category_description = await self.classifier.classify(
                            raw_tx.description
                        )

                        # Get or create category
                        category = await category_repo.get_by_description(
                            category_description
                        )
                        if not category:
                            from ...domain.entities import Category

                            category = await category_repo.save(
                                Category(id_category=None, description=category_description)
                            )
                            await session.commit()

                        # Determine transaction type (income or expense based on amount sign)
                        transaction_type = "income" if raw_tx.amount > 0 else "expense"

                        # Create transaction
                        transaction = Transaction(
                            id_transaction=None,
                            id_user=user_id,
                            id_bank=bank_id,
                            id_category=category.id_category,
                            id_batch=batch.id_batch,
                            transaction_date=raw_tx.date,
                            transaction_name=raw_tx.description,
                            value=abs(raw_tx.amount),  # Store as positive value
                            transaction_type=transaction_type,
                        )
                        transactions.append(transaction)

                    # Save batch
                    await transaction_repo.save_batch(transactions)
                    await session.commit()

                # Mark as completed
                batch.process_status = "completed"
                batch.end_date = datetime.now()
                await batch_repo.update(batch)
                await session.commit()

                # Publish message to RabbitMQ after successful completion
                try:
                    await self.message_broker.publish_batch_processed(
                        batch_id=batch.id_batch,
                        user_id=user_id,
                        status="completed",  # Status expected by InsightService
                    )
                except Exception as mq_error:
                    # Log error but don't fail the batch processing
                    # The batch is already completed and saved
                    logger.error(
                        f"Failed to publish batch processed event to RabbitMQ: {mq_error}",
                        exc_info=True,
                    )

            except Exception as e:
                await session.rollback()
                # Create a new session to update error status
                async with self.session_factory() as error_session:
                    error_batch_repo = MySQLTransactionBatchRepository(error_session)
                    batch.process_status = "error"
                    batch.end_date = datetime.now()
                    await error_batch_repo.update(batch)
                    await error_session.commit()

                # Optionally publish error event to RabbitMQ
                try:
                    await self.message_broker.publish_batch_processed(
                        batch_id=batch.id_batch,
                        user_id=user_id,
                        status="Error",
                    )
                except Exception as mq_error:
                    logger.error(
                        f"Failed to publish batch error event to RabbitMQ: {mq_error}",
                        exc_info=True,
                    )

                raise e
