# Scripts - Upload Service

## Scripts Disponibles

### `init_basic_data.py`

Inicializa datos básicos en la base de datos compartida (flowlite_db).

**Qué crea**:
- ✅ Bancos (Bancolombia, Davivienda, Banco de Bogotá)
- ✅ Categorías de transacciones (Alimentación, Transporte, Servicios, etc.)

**Qué NO crea**:
- ❌ Usuarios (los gestiona el IdentityService)
- ❌ Tokens JWT (los genera el IdentityService)

**Uso**:
```bash
python scripts/init_basic_data.py
```

**Requisitos**:
- MySQL corriendo
- Base de datos `flowlite_db` creada
- Variable de entorno `DATABASE_URL` configurada (o usa el default)

**Output esperado**:
```
✅ DATOS BÁSICOS CREADOS EXITOSAMENTE

📊 Bancos creados:
1. Bancolombia
   ID: 550e8400-e29b-41d4-a716-446655440000
2. Davivienda
   ID: 123e4567-e89b-12d3-a456-426614174000
...

📁 Categorías creadas:
1. Otros
   ID: abc12345-...
2. Alimentación
   ID: def67890-...
...
```

---

## Scripts Eliminados

Los siguientes scripts fueron **eliminados** porque ya no son compatibles con la nueva arquitectura:

### ❌ `init_db.py`
**Problema**: Intentaba crear usuarios localmente en el Upload Service.

**Por qué se eliminó**: Los usuarios ahora son gestionados exclusivamente por el IdentityService. El Upload Service solo valida tokens y obtiene el userId.

**Alternativa**: Usar el IdentityService para crear usuarios:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### ❌ `generate_test_tokens.py`
**Problema**: Generaba tokens JWT localmente usando una secret key.

**Por qué se eliminó**: El Upload Service ya NO valida tokens JWT localmente. Delega la validación al IdentityService mediante el endpoint `/auth/validate`.

**Alternativa 1**: Obtener token del IdentityService:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Alternativa 2**: Para testing sin IdentityService, usar dependency override:
```python
from src.api.dependencies.testing import get_test_user_id
app.dependency_overrides[get_current_user_id] = get_test_user_id
```

Ver [TESTING.md](../TESTING.md) para más detalles.

---

## Flujo de Setup Completo

### 1. Iniciar Servicios Requeridos

```bash
# RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# MySQL
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=flowlite_db \
  mysql:8
```

### 2. Ejecutar Migraciones (desde InsightService)

```bash
cd ../InsightService
alembic upgrade head
```

Esto crea las tablas: `Bank`, `TransactionCategory`, `TransactionBatch`, `Transaction`, `User`, etc.

### 3. Inicializar Datos Básicos

```bash
cd ../uploadservice
python scripts/init_basic_data.py
```

### 4. Iniciar IdentityService

```bash
cd ../IdentityService
uvicorn src.main:app --port 8000
```

### 5. Iniciar Upload Service

```bash
cd ../uploadservice
uvicorn src.main:app --port 8001
```

### 6. Crear Usuario de Prueba

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 7. Obtener Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 8. Usar el Token en Upload Service

```bash
curl -X POST "http://localhost:8001/api/v1/transactions/upload" \
  -H "Authorization: Bearer {token}" \
  -F "bank_code=BANCOLOMBIA" \
  -F "files=@test.xlsx"
```

---

## Testing sin IdentityService

Si quieres testear sin levantar el IdentityService, usa el módulo de testing:

```python
from src.api.dependencies.testing import get_test_user_id
from src.api.dependencies.auth import get_current_user_id

# Override dependency
app.dependency_overrides[get_current_user_id] = get_test_user_id

# Ahora puedes hacer requests sin token real
```

Ver documentación completa en [TESTING.md](../TESTING.md)

---

## Notas Importantes

1. **Base de Datos Compartida**: El Upload Service y el InsightService comparten la misma base de datos (`flowlite_db`)

2. **Gestión de Usuarios**: Los usuarios se crean en el IdentityService, NO en este servicio

3. **Validación de Tokens**: El Upload Service consulta al IdentityService para validar tokens

4. **UUIDs**: Todos los IDs son UUID (no integers)

5. **RabbitMQ**: El servicio publica eventos cuando completa batches

---

## Troubleshooting

### Error: "Bank with name X not found"

**Causa**: No se ejecutó el script de inicialización

**Solución**:
```bash
python scripts/init_basic_data.py
```

### Error: "No module named 'src'"

**Causa**: El script no encuentra el módulo src

**Solución**:
```bash
# Ejecutar desde el directorio raíz del proyecto
cd uploadservice
python scripts/init_basic_data.py
```

### Error: "Connection refused to MySQL"

**Causa**: MySQL no está corriendo

**Solución**:
```bash
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=flowlite_db \
  mysql:8
```

### Error: "Table doesn't exist"

**Causa**: No se ejecutaron las migraciones

**Solución**:
```bash
cd ../InsightService
alembic upgrade head
```
