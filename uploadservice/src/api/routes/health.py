from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ...infrastructure.database import get_database

router = APIRouter(prefix="/api/v1/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    database: str


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_database)):
    """
    Health check endpoint for the service and database.

    Returns:
        HealthResponse: Status of the service and database connection

    Raises:
        None: This endpoint should not raise exceptions
    """
    # Verify database connection
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
    )
