from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...domain.ports import BankRepositoryPort
from ...domain.entities import Bank as BankEntity
from ..database.models import Bank


class BankRepository(BankRepositoryPort):
    """
    Repository for bank operations using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_banks(self) -> List[BankEntity]:
        """
        Get all available banks.
        """
        query = select(Bank).order_by(Bank.bank_name)
        result = await self.session.execute(query)
        banks = result.scalars().all()

        # Convert to domain entities
        bank_entities = []
        for b in banks:
            bank_entities.append(
                BankEntity(
                    id_bank=str(b.id_bank).strip(),
                    bank_name=b.bank_name,
                )
            )

        return bank_entities
