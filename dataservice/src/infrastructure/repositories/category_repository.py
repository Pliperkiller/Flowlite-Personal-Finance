from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...domain.ports import CategoryRepositoryPort
from ...domain.entities import TransactionCategory as TransactionCategoryEntity
from ...domain.entities import InsightCategory as InsightCategoryEntity
from ..database.models import TransactionCategory, InsightCategory


class CategoryRepository(CategoryRepositoryPort):
    """
    Repository for category operations using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_transaction_categories(self) -> List[TransactionCategoryEntity]:
        """
        Get all available transaction categories.
        """
        query = select(TransactionCategory).order_by(TransactionCategory.description)
        result = await self.session.execute(query)
        categories = result.scalars().all()

        # Convert to domain entities
        category_entities = []
        for c in categories:
            category_entities.append(
                TransactionCategoryEntity(
                    id_category=str(c.id_category).strip(),
                    description=c.description,
                )
            )

        return category_entities

    async def get_all_insight_categories(self) -> List[InsightCategoryEntity]:
        """
        Get all available insight categories.
        """
        query = select(InsightCategory).order_by(InsightCategory.description)
        result = await self.session.execute(query)
        categories = result.scalars().all()

        # Convert to domain entities
        category_entities = []
        for c in categories:
            category_entities.append(
                InsightCategoryEntity(
                    id_category=str(c.id_category).strip(),
                    description=c.description,
                )
            )

        return category_entities
