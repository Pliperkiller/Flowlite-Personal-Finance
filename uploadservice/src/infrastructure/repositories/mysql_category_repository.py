from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import CategoryRepositoryPort
from ...domain.entities import Category
from ..database.models import CategoryModel


class MySQLCategoryRepository(CategoryRepositoryPort):
    """MySQL implementation of the Category repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_description(self, description: str) -> Optional[Category]:
        """Get a category by its description"""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.description == description)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, category: Category) -> Category:
        """Save a category to the database"""
        model = self._to_model(category)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, id_category: UUID) -> Optional[Category]:
        """Get a category by its ID"""
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id_category == str(id_category))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Category) -> CategoryModel:
        """Convert domain entity to database model"""
        return CategoryModel(
            id_category=str(entity.id_category) if entity.id_category else None,
            description=entity.description,
        )

    def _to_entity(self, model: CategoryModel) -> Category:
        """Convert database model to domain entity"""
        return Category(
            id_category=UUID(model.id_category) if model.id_category else None,
            description=model.description,
        )
