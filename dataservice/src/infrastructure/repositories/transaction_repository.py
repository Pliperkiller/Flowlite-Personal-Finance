from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List, Tuple

from ...domain.ports import TransactionRepositoryPort
from ...domain.entities import Transaction as TransactionEntity
from ..database.models import Transaction, TransactionCategory, Bank


class TransactionRepository(TransactionRepositoryPort):
    """
    Repository for transaction operations using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_transactions_by_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[TransactionEntity], int]:
        """
        Get paginated transactions for a user.
        """
        # Calculate offset
        offset = (page - 1) * page_size

        # Query for transactions with joins
        query = (
            select(Transaction)
            .options(joinedload(Transaction.category), joinedload(Transaction.bank))
            .where(Transaction.id_user == str(user_id))
            .order_by(Transaction.transaction_date.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.session.execute(query)
        transactions = result.scalars().unique().all()

        # Count total transactions
        count_query = select(func.count()).select_from(Transaction).where(Transaction.id_user == str(user_id))
        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar()

        # Convert to domain entities
        transaction_entities = []
        for t in transactions:
            try:
                # Parse id_bank - could be either a UUID string or a bank code string
                id_bank_value = None
                if t.id_bank:
                    bank_str = str(t.id_bank).strip()
                    # Try to parse as UUID, if it fails, keep as string
                    try:
                        id_bank_value = UUID(bank_str)
                    except ValueError:
                        # It's a bank code like "bank-001-bancolombia", keep as string
                        id_bank_value = bank_str

                # Parse id_batch - should be UUID or None
                id_batch_value = None
                if t.id_batch:
                    try:
                        id_batch_value = UUID(str(t.id_batch).strip())
                    except ValueError:
                        # If not a valid UUID, keep as string
                        id_batch_value = str(t.id_batch).strip()

                transaction_entities.append(
                    TransactionEntity(
                        id_transaction=UUID(str(t.id_transaction).strip()),
                        id_user=UUID(str(t.id_user).strip()),
                        id_category=str(t.id_category).strip(),  # Category ID is a string, not UUID
                        id_bank=id_bank_value,
                        id_batch=id_batch_value,
                        transaction_name=t.transaction_name,
                        value=t.value,
                        transaction_date=t.transaction_date,
                        transaction_type=t.transaction_type,
                        category_description=t.category.description if t.category else None,
                        bank_name=t.bank.bank_name if t.bank else None,
                    )
                )
            except (ValueError, AttributeError) as e:
                # Skip transactions with invalid UUIDs
                print(f"Warning: Skipping transaction with invalid UUID: {t.id_transaction} - {e}")
                continue

        return transaction_entities, total_count
