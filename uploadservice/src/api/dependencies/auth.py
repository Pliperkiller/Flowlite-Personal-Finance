from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from ...infrastructure.clients import IdentityServiceClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_identity_client() -> IdentityServiceClient:
    """
    Dependency to get the IdentityService client.

    Returns:
        IdentityServiceClient: An instance of the IdentityService client
    """
    return IdentityServiceClient()


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    identity_client: IdentityServiceClient = Depends(get_identity_client),
) -> UUID:
    """
    Validates the JWT token using the IdentityService and extracts the user_id.

    Args:
        token: JWT token from the Authorization header
        identity_client: IdentityService client for token validation

    Returns:
        UUID: The user ID if the token is valid and active

    Raises:
        HTTPException: If the token is invalid, revoked, or user is not active
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = await identity_client.validate_token(token)
        if user_id is None:
            raise credentials_exception
        return user_id
    except Exception as e:
        # Log the error for debugging
        print(f"Error validating token with IdentityService: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
