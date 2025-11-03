from fastapi import APIRouter, Depends
from uuid import UUID

from ...application.dto import RecommendationDTO, InsightsResponse
from ...domain.ports import InsightRepositoryPort
from ..dependencies import get_current_user, get_insight_repository

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("", response_model=InsightsResponse)
async def get_insights(
    current_user: UUID = Depends(get_current_user),
    insight_repo: InsightRepositoryPort = Depends(get_insight_repository),
):
    """
    Get all insights/recommendations for the authenticated user.

    Requires authentication via Bearer token.
    """
    print(current_user)
    # Get insights from repository
    insights = await insight_repo.get_insights_by_user(user_id=current_user)

    # Convert to DTOs
    recommendation_dtos = [
        RecommendationDTO(
            id=str(i.id_insight),
            type=i.category_type or "general",
            title=i.title,
            description=i.text,
            relevance=i.relevance,
        )
        for i in insights
    ]

    return InsightsResponse(recommendations=recommendation_dtos)
