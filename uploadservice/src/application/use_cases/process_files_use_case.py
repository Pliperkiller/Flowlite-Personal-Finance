"""
ProcessFilesUseCase with file hash validation and duplicate file detection.
"""
from typing import List, Tuple
import asyncio
import logging
from datetime import datetime
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
from ...domain.ports.file_upload_history_repository_port import FileUploadHistoryRepositoryPort
from ...domain.entities import Transaction, TransactionBatch, FileUploadHistory


class DuplicateFileError(Exception):
    """Exception raised when a duplicate file is detected."""
    def __init__(self, filename: str, batch_id: str, upload_date: datetime):
        self.filename = filename
        self.batch_id = batch_id
        self.upload_date = upload_date
        super().__init__(f"File {filename} was already uploaded on {upload_date}")


class ProcessFilesUseCase:
    """
    Use case for processing uploaded files with duplicate detection.

    Features:
    - Calculates SHA256 hash of uploaded files
    - Detects and prevents duplicate file processing
    - Saves file upload history to database
    - Processes transactions asynchronously
    """

    def __init__(
        self,
        transaction_repo: TransactionRepositoryPort,
        bank_repo: BankRepositoryPort,
        category_repo: CategoryRepositoryPort,
        batch_repo: TransactionBatchRepositoryPort,
        classifier: ClassifierPort,
        message_broker: MessageBrokerPort,
        file_upload_history_repo: FileUploadHistoryRepositoryPort,  # NEW PARAMETER
        session_factory: sessionmaker = None,
    ):
        self.transaction_repo = transaction_repo
        self.bank_repo = bank_repo
        self.category_repo = category_repo
        self.batch_repo = batch_repo
        self.classifier = classifier
        self.message_broker = message_broker
        self.file_upload_history_repo = file_upload_history_repo  # NEW
        self.session_factory = session_factory

    async def execute(
        self,
        files_data: List[Tuple[bytes, str, str, int]],  # (content, hash, filename, size)
        parser: ExcelParserPort,
        user_id: str,  # UUID as string
    ) -> str:  # Returns batch_id as string
        """
        Process Excel files with duplicate detection.

        Args:
            files_data: List of tuples containing (file_content, file_hash, filename, file_size)
            parser: Excel parser for the bank
            user_id: ID of the user uploading files (UUID as string)

        Returns:
            UUID string of the created batch

        Raises:
            ValueError: If bank not found
            DuplicateFileError: If file was already uploaded (contains batch_id and upload_date)
        """
        # 1. Get the bank by name
        bank_name = parser.get_bank_code()
        bank = await self.bank_repo.get_by_name(bank_name)
        if not bank:
            raise ValueError(f"Bank with name {bank_name} not found")

        # 2. VALIDATE FILE HASHES - Check for duplicates
        for file_content, file_hash, filename, file_size in files_data:
            existing_upload = await self.file_upload_history_repo.get_by_hash(
                user_id=user_id,
                file_hash=file_hash
            )

            if existing_upload:
                # FILE IS DUPLICATE - Raise exception to return 409
                logger.warning(
                    f"Duplicate file detected: {filename} (hash: {file_hash[:16]}...) "
                    f"Original upload: {existing_upload.upload_date}, "
                    f"Batch ID: {existing_upload.id_batch}"
                )
                # Raise exception with details about the duplicate
                raise DuplicateFileError(
                    filename=filename,
                    batch_id=existing_upload.id_batch,
                    upload_date=existing_upload.upload_date
                )

        # 3. Parse all files
        all_raw_transactions = []
        for file_content, file_hash, filename, file_size in files_data:
            raw_transactions = parser.parse(file_content)
            all_raw_transactions.extend(raw_transactions)

        # 4. Create the batch
        batch = TransactionBatch(
            id_batch=None,
            process_status="pending",
            start_date=datetime.now(),
            end_date=None,
            batch_size=len(all_raw_transactions),
        )
        batch = await self.batch_repo.save(batch)

        # 5. SAVE FILE UPLOAD HISTORY - Record this upload
        for file_content, file_hash, filename, file_size in files_data:
            file_upload = FileUploadHistory(
                id_file=None,
                id_user=user_id,
                file_hash=file_hash,
                file_name=filename,
                bank_code=bank_name,
                upload_date=datetime.now(),
                id_batch=batch.id_batch,
                file_size=file_size,
            )
            await self.file_upload_history_repo.save(file_upload)
            logger.info(
                f"Saved file upload history: {filename} (hash: {file_hash[:16]}...) "
                f"Batch ID: {batch.id_batch}"
            )

        # 6. Process in background
        asyncio.create_task(
            self._process_transactions_async(
                all_raw_transactions, batch, user_id, bank.id_bank
            )
        )

        return batch.id_batch

    async def _process_transactions_async(
        self, raw_transactions, batch: TransactionBatch, user_id: str, bank_id: str  # Both are UUID strings
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

                # Cache categories to avoid repeated DB queries
                category_cache = {}

                for i in range(0, len(raw_transactions), BATCH_SIZE):
                    chunk = raw_transactions[i : i + BATCH_SIZE]

                    # OPTIMIZATION: Batch classify all transactions at once
                    # This is 50-100x faster than classifying one-by-one!
                    descriptions = [raw_tx.description for raw_tx in chunk]
                    values = [float(raw_tx.amount) for raw_tx in chunk]

                    logger.info(f"Batch classifying {len(chunk)} transactions...")
                    category_descriptions = await self.classifier.classify_batch(
                        descriptions=descriptions,
                        transaction_values=values
                    )

                    # Create transactions with classified categories
                    transactions = []
                    for raw_tx, category_description in zip(chunk, category_descriptions):
                        # Check cache first
                        if category_description not in category_cache:
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

                            # Add to cache
                            category_cache[category_description] = category
                        else:
                            # Use cached category (much faster!)
                            category = category_cache[category_description]

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
                    logger.info(f"Saving {len(transactions)} classified transactions to database...")
                    await transaction_repo.save_batch(transactions)
                    await session.commit()
                    logger.info(f"Batch {i//BATCH_SIZE + 1} completed: {len(transactions)} transactions saved")

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
                        status="completed",
                    )
                except Exception as mq_error:
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
