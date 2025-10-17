from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/api/v1/test", tags=["test"])


class UserIdResponse(BaseModel):
    user_id: int
    message: str


@router.get("/user-id", response_model=UserIdResponse)
async def get_user_id_from_token(usuario_id: int = Depends(get_current_user_id)):
    """
    Endpoint de prueba que retorna el user_id extraído del JWT
    Solo para propósitos de testing
    """
    return UserIdResponse(
        user_id=usuario_id,
        message=f"El token corresponde al usuario con ID {usuario_id}",
    )
