# Testing Guide - Upload Service

Guía completa para testear el Upload Service sin depender del IdentityService.

## 📋 Tabla de Contenidos

1. [Configuración del Entorno de Testing](#configuración-del-entorno-de-testing)
2. [Testing sin IdentityService](#testing-sin-identityservice)
3. [Testing con Mock de RabbitMQ](#testing-con-mock-de-rabbitmq)
4. [Scripts Disponibles](#scripts-disponibles)
5. [Tests Automatizados](#tests-automatizados)

---

## Configuración del Entorno de Testing

### 1. Requisitos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Dependencias adicionales para testing
pip install pytest pytest-asyncio httpx
```

### 2. Base de Datos de Testing

```bash
# Usar la misma BD que InsightService
export DATABASE_URL="mysql+aiomysql://root:root@localhost:3306/flowlite_db"
```

### 3. Inicializar Datos Básicos

```bash
# Ejecutar el script de inicialización
python scripts/init_basic_data.py
```

---

## Testing sin Identifyservice

### Usando Dependency Override (Recomendado)

```python
from fastapi.testclient import TestClient
from src.main import app
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.testing import get_test_user_id, TEST_USER_1_UUID

# Override the dependency
app.dependency_overrides[get_current_user_id] = get_test_user_id

# Create test client
client = TestClient(app)

# Make requests without authentication
response = client.post(
    "/api/v1/transactions/upload",
    params={"bank_code": "BANCOLOMBIA"},
    files={"files": ("test.xlsx", open("test.xlsx", "rb"))}
)

# Clean up
app.dependency_overrides = {}
```

### Test User UUIDs Disponibles

```python
from src.api.dependencies.testing import (
    TEST_USER_1_UUID,  # 123e4567-e89b-12d3-a456-426614174001
    TEST_USER_2_UUID,  # 123e4567-e89b-12d3-a456-426614174002
    TEST_USER_3_UUID,  # 123e4567-e89b-12d3-a456-426614174003
)
```

---

## Testing con Mock de RabbitMQ

```python
from unittest.mock import AsyncMock
from src.domain.ports import MessageBrokerPort
from src.api.dependencies.services import get_message_broker

# Create mock
mock_broker = AsyncMock(spec=MessageBrokerPort)
mock_broker.publish_batch_processed = AsyncMock()

# Override dependency
app.dependency_overrides[get_message_broker] = lambda: mock_broker

# Test
response = client.post("/api/v1/transactions/upload", ...)

# Verify
mock_broker.publish_batch_processed.assert_called_once()
```

---

## Scripts Disponibles

### Inicializar Datos Básicos

```bash
python scripts/init_basic_data.py
```

Crea:
- ✅ Bancos (Bancolombia, Davivienda, etc.)
- ✅ Categorías de transacciones

---

## Tests Automatizados

### Ejemplo Completo

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.dependencies.auth import get_current_user_id
from src.api.dependencies.testing import get_test_user_id
from src.api.dependencies.services import get_message_broker
from unittest.mock import AsyncMock

@pytest.fixture
def client():
    # Override dependencies
    app.dependency_overrides[get_current_user_id] = get_test_user_id
    
    mock_broker = AsyncMock()
    app.dependency_overrides[get_message_broker] = lambda: mock_broker
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides = {}


def test_upload_excel_file(client):
    test_file = open("tests/fixtures/test.xlsx", "rb")
    
    response = client.post(
        "/api/v1/transactions/upload",
        params={"bank_code": "BANCOLOMBIA"},
        files={"files": ("test.xlsx", test_file)}
    )
    
    assert response.status_code == 202
    assert "batch_id" in response.json()
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Verbose
pytest -v
```

---

## Resumen Rápido

**Para testear sin IdentityService**:
```python
app.dependency_overrides[get_current_user_id] = get_test_user_id
```

**Para testear sin RabbitMQ**:
```python
app.dependency_overrides[get_message_broker] = lambda: AsyncMock()
```

**Para inicializar datos**:
```bash
python scripts/init_basic_data.py
```

**Para ejecutar tests**:
```bash
pytest
```
