from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import BankRepositoryPort
from ...domain.entities import Bank
from ..database.models import BankModel


class MySQLBankRepository(BankRepositoryPort):
    """MySQL implementation of the Bank repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, bank_name: str) -> Optional[Bank]:
        """Get a bank by its name"""
        result = await self.session.execute(
            select(BankModel).where(BankModel.bank_name == bank_name)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, bank: Bank) -> Bank:
        """Save a bank to the database"""
        model = self._to_model(bank)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, id_bank: str) -> Optional[Bank]:
        """Get a bank by its ID"""
        result = await self.session.execute(
            select(BankModel).where(BankModel.id_bank == id_bank)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Bank) -> BankModel:
        """Convert domain entity to database model"""
        return BankModel(
            id_bank=entity.id_bank,
            bank_name=entity.bank_name,
        )

    def _to_entity(self, model: BankModel) -> Bank:
        """Convert database model to domain entity"""
        return Bank(
            id_bank=model.id_bank,
            bank_name=model.bank_name,
        )
