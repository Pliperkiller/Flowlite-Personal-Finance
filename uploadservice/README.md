# Upload Service - Flowlite Personal Finance

FastAPI service to process and classify bank transactions from Excel files using hexagonal architecture.

## Features

- Processing of Excel files with bank transactions
- **ML-based transaction classification with 99.7% accuracy** (Logistic Regression + TF-IDF)
- Automatic categorization into 12+ categories (Alimentación, Transporte, etc.)
- Asynchronous batch processing
- **Delegated JWT authentication via IdentityService**
- **Event-driven architecture with RabbitMQ**
- **UUID-based identifiers for all entities**
- Hexagonal architecture for high maintainability and scalability
- Extensible support for multiple banks
- **Shared database with InsightService**

## Architecture

The project follows hexagonal architecture principles (ports and adapters):

```
src/
├── domain/              # Domain layer (business logic)
│   ├── entities/        # Domain entities
│   └── ports/           # Interfaces (ports)
├── application/         # Application layer (use cases)
│   ├── use_cases/       # Use cases
│   └── dto/             # Data Transfer Objects
├── infrastructure/      # Infrastructure layer (adapters)
│   ├── database/        # Models and DB connection
│   ├── repositories/    # Repository implementations
│   ├── parsers/         # Excel file parsers
│   └── classifier/      # Transaction classifier
└── api/                 # Presentation layer (REST API)
    ├── routes/          # Endpoints
    └── dependencies/    # FastAPI dependencies
```

## Database Models

- **users**: System users (includes test users for testing)
- **banks**: Bank information
- **categories**: Transaction categories
- **transaction_batches**: Processing batches
- **transactions**: Individual normalized transactions

## Requirements

- Python 3.9+
- **InfrastructureService** running (MySQL and RabbitMQ)
- **IdentityService** running (for authentication on port 8000)

## Installation

### 1. Start InfrastructureService

**FIRST**, start the shared infrastructure:

```bash
cd InfrastructureService

# Start MySQL and RabbitMQ
docker-compose up -d

# Verify services are running
docker-compose ps

# Run migrations (only the first time)
export DATABASE_URL="mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db"
alembic upgrade head
```

See `InfrastructureService/README.md` for more details.

### 2. Start IdentityService (required for authentication)

```bash
cd identifyservice
./start.sh
```

### 3. Install UploadService

```bash
cd uploadservice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings
```

**Important**: The database schema is managed by **InfrastructureService**.
Do NOT run migrations from this service.

## Running

Make sure **InfrastructureService** and **IdentityService** are running first.

```bash
cd uploadservice
source venv/bin/activate

# Start the service
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

**Note**: The service runs on port **8001** to avoid conflicts with IdentityService (port 8000)

The API will be available at `http://localhost:8001`

Interactive documentation: `http://localhost:8001/docs`

## Authentication

**Important**: This service does NOT manage users or generate JWT tokens.

Authentication is delegated to the **IdentityService**:

1. Users register/login via IdentityService
2. IdentityService returns a JWT token
3. Upload Service validates the token by calling IdentityService's `/auth/validate` endpoint
4. If valid, Upload Service extracts the `userId` (UUID) from the response

To get a JWT token, use the IdentityService:

```bash
# Login via IdentityService
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

The response will include a JWT token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Endpoints

### 1. Health Check
```http
GET /api/v1/health
```
Checks the service and database status.

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

### 2. Upload Transaction Files
```http
POST /api/v1/transactions/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Parameters:**
- `bank_code`: Bank code (e.g., BANCOLOMBIA)
- `files`: List of Excel files

**Response:**
```json
{
  "batch_id": 1,
  "message": "Processing started. Use batch_id 1 to check status."
}
```

**Example with curl:**
```bash
curl -X POST "http://localhost:8001/api/v1/transactions/upload?bank_code=BANCOLOMBIA" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "files=@MovimientosTusCuentasBancolombia07Oct2025.xlsx"
```

### 3. Check Batch Status
```http
GET /api/v1/transactions/batch/{batch_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "batch_id": 1,
  "status": "processing",
  "total_records": 190,
  "processed_records": 95,
  "processed_percentage": 50.0,
  "created_at": "2025-10-10T10:00:00",
  "updated_at": "2025-10-10T10:05:00"
}
```

### 4. Get User ID from Token (Testing)
```http
GET /api/v1/test/user-id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": 123,
  "message": "The token corresponds to user with ID 123"
}
```

## Excel File Format

### Bancolombia
The file must have the following columns:
- **Fecha** (Date): Transaction date
- **Descripción** (Description): Transaction description
- **Referencia** (Reference): Optional reference
- **Valor** (Value): Transaction amount

Example:
| Fecha      | Descripción           | Referencia | Valor      |
|------------|-----------------------|------------|------------|
| 2025-10-05 | TRANSF PEDRO PEREZ |            | 23.0    |
| 2025-09-26 | PAGO DE NOMI   | 1004057  | 123.0  |

## Add Support for New Banks

To add support for a new bank:

1. Create a new parser in `src/infrastructure/parsers/`:

```python
# src/infrastructure/parsers/new_bank_parser.py
from typing import List
import pandas as pd
from io import BytesIO
from decimal import Decimal
from ...domain.ports.excel_parser_port import ExcelParserPort, RawTransaction


class NewBankParser(ExcelParserPort):
    BANK_CODE = "NEW_BANK"

    def parse(self, file_content: bytes) -> List[RawTransaction]:
        df = pd.read_excel(BytesIO(file_content))

        # Adapt according to new bank format
        transactions = []
        for _, row in df.iterrows():
            transaction = RawTransaction(
                date=pd.to_datetime(row["Date"]),
                description=str(row["Description"]),
                reference=str(row["Ref"]) if pd.notna(row["Ref"]) else None,
                amount=Decimal(str(row["Amount"])),
            )
            transactions.append(transaction)

        return transactions

    def get_bank_code(self) -> str:
        return self.BANK_CODE
```

2. Register the parser in `ParserFactory`:

```python
# src/infrastructure/parsers/parser_factory.py
from .new_bank_parser import NewBankParser

class ParserFactory:
    _parsers = {
        "BANCOLOMBIA": BancolombiaParser,
        "NEW_BANK": NewBankParser,  # Add here
    }
```

3. Add the bank to the database:

```python
bank = BankModel(name="New Bank", code="NEW_BANK")
```

## JWT Configuration

The service expects JWT tokens with the following format:

```json
{
  "sub": 123,  // user_id
  "exp": 1234567890,
  // other claims...
}
```

Configure `JWT_SECRET_KEY` and `JWT_ALGORITHM` in `.env` to match the authentication service.

## Environment Variables

**Important**: Database and RabbitMQ credentials must match those in **InfrastructureService**.

```bash
# Database (must match InfrastructureService configuration)
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# IdentityService
IDENTITY_SERVICE_URL=http://localhost:8000
IDENTITY_SERVICE_TIMEOUT=5.0

# RabbitMQ (must match InfrastructureService configuration)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE_NAME=batch_processed

# Server
HOST=0.0.0.0
PORT=8001
```

## RabbitMQ Integration

When a batch is successfully processed, the Upload Service publishes a message to RabbitMQ:

```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Processed",
  "userid": "123e4567-e89b-12d3-a456-426614174000"
}
```

This message is consumed by the **InsightService**, which automatically generates insights for the user.

### Message Flow

```
Upload Service → RabbitMQ (batch_processed queue) → InsightService
```

1. User uploads Excel files
2. Upload Service processes transactions
3. Upload Service publishes "Processed" message
4. InsightService consumes message
5. InsightService generates insights automatically

For more details, see [RABBITMQ_INTEGRATION.md](./RABBITMQ_INTEGRATION.md)

## Asynchronous Processing

Transactions are processed in batches of 500 records asynchronously. The user immediately receives a `batch_id` that can be used to check progress.

Batch states:
- `pending`: Batch created, waiting for processing
- `processing`: Processing in progress
- `completed`: Processing completed successfully
- `error`: Error during processing

## Transaction Classifier

Currently, the classifier returns the "Other" category for all transactions. To integrate an ML model:

1. Implement `ClassifierPort` in `src/infrastructure/classifier/`:

```python
class MLClassifier(ClassifierPort):
    def __init__(self, model_path: str):
        # Load model
        self.model = load_model(model_path)

    async def classify(self, description: str) -> str:
        # Use model to classify
        category = self.model.predict(description)
        return category
```

2. Update the dependency in `src/api/dependencies/services.py`:

```python
def get_classifier() -> ClassifierPort:
    return MLClassifier(model_path="path/to/model")
```

## Development

### Run tests
```bash
pytest tests/
```

### Linting
```bash
black src/
flake8 src/
```

## Important Notes

- Users can only upload files from the same bank per request
- Files are processed in batches of 500 transactions
- Transactions are normalized with bank, category, and user IDs
- The users table is automatically created by the initialization script

## Complete Testing Example

### 1. Start InfrastructureService
```bash
cd InfrastructureService
docker-compose up -d

# Run migrations (first time only)
export DATABASE_URL="mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db"
alembic upgrade head
```

### 2. Initialize test data
```bash
cd uploadservice
python scripts/init_basic_data.py
```

### 3. Start the upload service
```bash
cd uploadservice
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### 4. Test health check
```bash
curl -X GET "http://localhost:8001/api/v1/health"
```

You should see:
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

### 5. Upload transaction file (without authentication for testing)

See [TESTING.md](./TESTING.md) for detailed instructions on testing without IdentityService.

**With IdentityService** (production mode):
```bash
# First, get a token from IdentityService
# Then upload files
curl -X POST "http://localhost:8001/api/v1/transactions/upload?bank_code=BANCOLOMBIA" \
  -H "Authorization: Bearer <your-token>" \
  -F "files=@MovimientosTusCuentasBancolombia07Oct2025.xlsx"
```

Expected response:
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Processing started. Use batch_id to check status."
}
```

### 6. Check processing status
```bash
curl -X GET "http://localhost:8001/api/v1/transactions/batch/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer <your-token>"
```

Expected response:
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_records": 190,
  "processed_records": 190,
  "processed_percentage": 100.0,
  "created_at": "2025-10-10T10:00:00",
  "updated_at": "2025-10-10T10:05:00"
}
```

## License

MIT
