from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from ...domain.ports import InsightRepositoryPort
from ...domain.entities import Insight as InsightEntity
from ..database.models import Insights, InsightCategory


class InsightRepository(InsightRepositoryPort):
    """
    Repository for insight operations using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_insights_by_user(self, user_id: UUID) -> List[InsightEntity]:
        """
        Get all insights for a user, ordered by relevance (higher values = more relevant).
        """
        query = (
            select(Insights)
            .options(joinedload(Insights.category))
            .where(Insights.id_user == str(user_id))
            .order_by(Insights.relevance.desc())  # Higher relevance number = higher priority
        )

        result = await self.session.execute(query)
        insights = result.scalars().unique().all()

        # Convert to domain entities
        insight_entities = []
        for i in insights:
            try:
                # Parse id_user - could be either a UUID string or a user code string
                id_user_value = None
                if i.id_user:
                    user_str = str(i.id_user).strip()
                    try:
                        id_user_value = UUID(user_str)
                    except ValueError:
                        # It's a user code like "user-001-juan-perez", keep as string
                        id_user_value = user_str

                # Parse id_category - could be either a UUID string or a category code string
                id_category_value = None
                if i.id_category:
                    category_str = str(i.id_category).strip()
                    try:
                        id_category_value = UUID(category_str)
                    except ValueError:
                        # It's a category code like "ins-cat-001-ahorro", keep as string
                        id_category_value = category_str

                insight_entities.append(
                    InsightEntity(
                        id_insight=UUID(str(i.id_insight).strip()),
                        id_user=id_user_value,
                        id_category=id_category_value,
                        title=i.title,
                        text=i.text,
                        relevance=i.relevance,
                        created_at=i.created_at,
                        category_type=i.category.description if i.category else None,
                    )
                )
            except (ValueError, AttributeError) as e:
                # Skip insights with invalid data
                print(f"Warning: Skipping insight with invalid data: {i.id_insight} - {e}")
                continue

        return insight_entities
