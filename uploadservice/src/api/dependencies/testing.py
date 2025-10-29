"""
Testing dependencies - Override para testing sin IdentityService
"""
from uuid import UUID
from typing import Optional


# Test user UUIDs - usa estos IDs en tus tests
TEST_USER_1_UUID = UUID("123e4567-e89b-12d3-a456-426614174001")
TEST_USER_2_UUID = UUID("123e4567-e89b-12d3-a456-426614174002")
TEST_USER_3_UUID = UUID("123e4567-e89b-12d3-a456-426614174003")


async def get_test_user_id(test_user_uuid: Optional[UUID] = None) -> UUID:
    """
    Override de get_current_user_id para testing.

    Retorna un UUID de usuario de prueba sin llamar al IdentityService.

    Args:
        test_user_uuid: UUID opcional del usuario de prueba.
                       Si no se provee, usa TEST_USER_1_UUID por defecto.

    Returns:
        UUID del usuario de prueba

    Uso:
        from fastapi.testclient import TestClient
        from src.main import app
        from src.api.dependencies.auth import get_current_user_id
        from src.api.dependencies.testing import get_test_user_id, TEST_USER_1_UUID

        # Override dependency
        app.dependency_overrides[get_current_user_id] = get_test_user_id

        # Use TestClient
        client = TestClient(app)
        response = client.post("/api/v1/transactions/upload", ...)

        # Reset override when done
        app.dependency_overrides = {}
    """
    return test_user_uuid or TEST_USER_1_UUID


def create_test_user_override(user_uuid: UUID):
    """
    Factory para crear un override con un UUID específico.

    Args:
        user_uuid: UUID del usuario de prueba

    Returns:
        Función async que retorna el UUID especificado

    Uso:
        from src.api.dependencies.testing import create_test_user_override, TEST_USER_2_UUID

        # Override con usuario específico
        app.dependency_overrides[get_current_user_id] = create_test_user_override(TEST_USER_2_UUID)
    """
    async def _override() -> UUID:
        return user_uuid
    return _override
