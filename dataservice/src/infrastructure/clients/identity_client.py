import httpx
import os
from typing import Optional
from uuid import UUID


class IdentityServiceClient:
    """
    Client to communicate with the IdentityService to validate tokens
    and retrieve user information.
    """

    def __init__(self):
        self.base_url = os.getenv("IDENTITY_SERVICE_URL", "http://localhost:8000")
        self.timeout = float(os.getenv("IDENTITY_SERVICE_TIMEOUT", "5.0"))

    async def validate_token(self, token: str) -> Optional[UUID]:
        """
        Validate a JWT token using the IdentityService /auth/validate endpoint.

        Args:
            token: The JWT token to validate

        Returns:
            UUID: The user ID if the token is valid and active
            None: If the token is invalid, revoked, or the user is not active

        Raises:
            httpx.HTTPError: If there's a connection error with IdentityService
        """
        url = f"{self.base_url}/auth/validate"
        params = {"token": token}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()

                    # Check if token is valid and active
                    if data.get("valid") and not data.get("revoked") and data.get("status") == "active":
                        user_id_str = data.get("userId")
                        if user_id_str:
                            try:
                                user_uuid = UUID(user_id_str)
                                return user_uuid
                            except (ValueError, TypeError) as e:
                                raise ValueError(f"Invalid UUID format: {user_id_str}") from e

                return None

        except httpx.HTTPError as e:
            print(f"Error connecting to IdentityService: {e}")
            raise
