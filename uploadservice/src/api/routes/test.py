from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/test", tags=["test"])


class UserIdResponse(BaseModel):
    user_id: int
    message: str


@router.get("/user-id", response_model=UserIdResponse)
async def get_user_id_from_token(user_id: int = Depends(get_current_user_id)):
    """
    Test endpoint that returns the user_id extracted from the JWT token.
    For testing purposes only.

    Args:
        user_id: User ID extracted from the JWT token

    Returns:
        UserIdResponse: Contains the user ID and a confirmation message
    """
    return UserIdResponse(
        user_id=user_id,
        message=f"The token corresponds to user with ID {user_id}",
    )
