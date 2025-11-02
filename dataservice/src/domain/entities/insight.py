from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Insight:
    """
    Domain entity representing an insight/recommendation.
    """
    id_insight: UUID
    id_user: UUID | str  # Can be UUID or user code string
    id_category: UUID | str  # Can be UUID or category code string
    title: str
    text: str
    relevance: int
    created_at: datetime
    category_type: str | None = None  # savings, budget, etc.
