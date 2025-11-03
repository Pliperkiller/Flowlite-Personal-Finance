from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from ...infrastructure.clients import IdentityServiceClient

# Middleware de seguridad estándar para encabezado "Authorization: Bearer <token>"
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """
    Dependency to validate the authorization token and get the current user.

    This uses the standard FastAPI HTTPBearer security scheme, which:
      - Automatically adds the 'Authorize' button in Swagger UI.
      - Expects a header 'Authorization: Bearer <token>'.

    Returns:
        UUID: The validated user ID.

    Raises:
        HTTPException: If the token is invalid or cannot be validated.
    """

    token = credentials.credentials  # Extract token from the header

    # Validate token with the IdentityService
    identity_client = IdentityServiceClient()

    try:
        user_id = await identity_client.validate_token(token)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return user_id

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating token: {str(e)}",
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to validate token. Identity service unavailable.",
        )
