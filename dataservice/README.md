# Flowlite Data Service

RESTful API service for retrieving user transactions, insights, and catalog data.

## Architecture

This service follows **Clean Hexagonal Architecture** with:
- **Domain Layer**: Entities, ports (interfaces)
- **Application Layer**: Use cases, DTOs
- **Infrastructure Layer**: Database repositories, external clients
- **API Layer**: FastAPI routes, dependencies

## Endpoints

### Protected Endpoints (Require Authentication)

#### GET `/transactions`
Get paginated transactions for authenticated user.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `pageSize` (int, optional): Items per page (default: 10)

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "name": "Transaction name",
      "value": 100.50,
      "date": "2024-01-15T10:30:00",
      "type": "expense",
      "category": "Alimentación",
      "bank": "Bancolombia"
    }
  ],
  "page": 1,
  "pageSize": 10,
  "totalPages": 5,
  "totalTransactions": 48
}
```

#### GET `/insights`
Get all insights/recommendations for authenticated user.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "recommendations": [
    {
      "id": "uuid",
      "type": "savings",
      "title": "Ahorro",
      "description": "Consider reducing expenses in restaurants",
      "relevance": 1
    }
  ]
}
```

### Public Endpoints (No Authentication)

#### GET `/banks`
Get all available banks.

**Response:**
```json
{
  "banks": [
    {
      "id": "uuid",
      "name": "Bancolombia"
    }
  ]
}
```

#### GET `/transaction-categories`
Get all transaction categories.

**Response:**
```json
{
  "categories": [
    {
      "id": "uuid",
      "description": "Alimentación"
    }
  ]
}
```

#### GET `/insight-categories`
Get all insight/recommendation categories.

**Response:**
```json
{
  "categories": [
    {
      "id": "uuid",
      "description": "savings"
    }
  ]
}
```

#### GET `/health`
Health check endpoint.

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database Configuration
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# IdentityService Configuration
IDENTITY_SERVICE_URL=http://localhost:8000
IDENTITY_SERVICE_TIMEOUT=5.0

# Server Configuration
HOST=0.0.0.0
PORT=8003
```

## Running the Service

### Development (Local)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the service
python main.py
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## Dependencies

- **InfrastructureService**: Shared database
- **IdentityService**: Token validation
