"""
Ejemplo de test del Upload Service sin IdentityService

Este test muestra cómo testear el Upload Service haciendo override
del dependency de autenticación para no requerir IdentityService.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from io import BytesIO
import pandas as pd

# Imports from the app
from src.main import app
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.services import get_message_broker
from src.api.dependencies.testing import (
    get_test_user_id,
    TEST_USER_1_UUID,
    create_test_user_override
)


@pytest.fixture
def client():
    """
    Test client with overridden dependencies.

    This fixture:
    1. Overrides authentication to use a test user UUID
    2. Overrides message broker to use a mock
    3. Provides a TestClient
    4. Cleans up after the test
    """
    # Override authentication dependency
    app.dependency_overrides[get_current_user_id] = get_test_user_id

    # Override message broker dependency
    mock_broker = AsyncMock()
    mock_broker.publish_batch_processed = AsyncMock()
    mock_broker.connect = AsyncMock()
    mock_broker.disconnect = AsyncMock()
    app.dependency_overrides[get_message_broker] = lambda: mock_broker

    # Create test client
    client = TestClient(app)

    yield client

    # Cleanup: remove all overrides
    app.dependency_overrides = {}


def create_test_excel() -> BytesIO:
    """
    Create a test Excel file in memory.

    Returns:
        BytesIO: Excel file as bytes
    """
    # Create test data
    df = pd.DataFrame({
        "Fecha": ["27/10/2025", "26/10/2025"],
        "Descripción": ["TEST TRANSACTION 1", "TEST TRANSACTION 2"],
        "Referencia": ["REF001", "REF002"],
        "Valor": [100.50, -50.25]
    })

    # Convert to Excel
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return output


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_upload_excel_file_success(client):
    """
    Test uploading an Excel file successfully.

    This test:
    1. Creates a test Excel file
    2. Uploads it to the API
    3. Verifies the response
    4. Does NOT require IdentityService or RabbitMQ
    """
    # Create test Excel file
    excel_file = create_test_excel()

    # Upload file
    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "BANCOLOMBIA"},
        files={"files": ("test_transactions.xlsx", excel_file, "application/vnd.ms-excel")}
    )

    # Verify response
    assert response.status_code == 202  # Accepted
    data = response.json()
    assert "batch_id" in data
    assert "message" in data

    # Verify batch_id is a valid UUID string
    import uuid
    try:
        uuid.UUID(data["batch_id"])
    except ValueError:
        pytest.fail("batch_id is not a valid UUID")


def test_upload_without_files(client):
    """Test upload endpoint without providing files"""
    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "BANCOLOMBIA"}
    )

    assert response.status_code == 400
    assert "Must provide at least one file" in response.json()["detail"]


def test_upload_invalid_file_type(client):
    """Test upload with non-Excel file"""
    # Create a text file
    text_file = BytesIO(b"This is not an Excel file")

    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "BANCOLOMBIA"},
        files={"files": ("test.txt", text_file, "text/plain")}
    )

    assert response.status_code == 400
    assert "not a valid Excel file" in response.json()["detail"]


def test_upload_invalid_bank_code(client):
    """Test upload with invalid bank code"""
    excel_file = create_test_excel()

    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "INVALID_BANK"},
        files={"files": ("test.xlsx", excel_file, "application/vnd.ms-excel")}
    )

    assert response.status_code == 400
    assert "not supported" in response.json()["detail"].lower()


def test_upload_with_different_user():
    """
    Test upload with a specific test user.

    This shows how to use a different test user UUID.
    """
    # Override with specific user
    from src.api.dependencies.testing import TEST_USER_2_UUID
    app.dependency_overrides[get_current_user_id] = create_test_user_override(TEST_USER_2_UUID)

    # Mock message broker
    mock_broker = AsyncMock()
    app.dependency_overrides[get_message_broker] = lambda: mock_broker

    client = TestClient(app)

    # Upload file
    excel_file = create_test_excel()
    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "BANCOLOMBIA"},
        files={"files": ("test.xlsx", excel_file, "application/vnd.ms-excel")}
    )

    assert response.status_code == 202

    # Cleanup
    app.dependency_overrides = {}


# Note: To run these tests, first initialize the database:
# python scripts/init_basic_data.py
#
# Then run:
# pytest tests/test_upload_example.py -v
