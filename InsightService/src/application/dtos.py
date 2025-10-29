from dataclasses import dataclass
from uuid import UUID
from typing import List


@dataclass
class BatchProcessedMessage:
    """DTO for incoming RabbitMQ message"""
    batch_id: str
    status: str
    user_id: str

    def is_processed(self) -> bool:
        """Check if the batch status is 'completed'"""
        return self.status == "completed"


@dataclass
class InsightDTO:
    """DTO for insight response"""
    id_insight: UUID
    id_user: UUID
    id_category: UUID
    title: str
    text: str
    relevance: int
    
    @classmethod
    def from_entity(cls, insight):
        """Create DTO from Insight entity"""
        from src.domain.entities import Insight
        
        return cls(
            id_insight=insight.id_insight,
            id_user=insight.id_user.value,
            id_category=insight.id_category.value,
            title=insight.title,
            text=insight.text,
            relevance=insight.relevance
        )


@dataclass
class GenerateInsightsResponse:
    """Response DTO for insight generation use case"""
    user_id: str
    batch_id: str
    insights_generated: int
    insights: List[InsightDTO]
