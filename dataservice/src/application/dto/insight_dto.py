from pydantic import BaseModel


class RecommendationDTO(BaseModel):
    """
    DTO for insight/recommendation data.
    """
    id: str
    type: str  # savings, budget, etc.
    title: str
    description: str
    relevance: int

    class Config:
        from_attributes = True


class InsightsResponse(BaseModel):
    """
    Response for insights endpoint.
    """
    recommendations: list[RecommendationDTO]

    class Config:
        from_attributes = True
