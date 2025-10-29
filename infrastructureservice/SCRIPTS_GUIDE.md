# Guía de Scripts - InfrastructureService

## Resumen Rápido

Tres scripts principales para gestionar la infraestructura compartida de Flowlite:

1. **`check_infrastructure.py`** - ✨ Verifica que todo esté funcionando
2. **`init_database.py`** - Inicializa la estructura de la base de datos
3. **`seed_database.py`** - Puebla con datos de prueba

## Quick Start

```bash
# 1. Iniciar infraestructura
cd InfrastructureService
docker-compose up -d

# 2. Verificar que todo funcione
python scripts/check_infrastructure.py

# 3. Inicializar estructura
python scripts/init_database.py

# 4. Poblar datos de prueba
python scripts/seed_database.py

# 5. Verificar nuevamente con detalles
python scripts/check_infrastructure.py --verbose

# ¡Listo! Ahora puedes iniciar los servicios
```

## Comandos Útiles

### Setup Inicial
```bash
# Todo en uno - primera vez
docker-compose up -d && \
python scripts/check_infrastructure.py && \
python scripts/init_database.py && \
python scripts/seed_database.py
```

### Verificación Rápida
```bash
# Verificar todo
python scripts/check_infrastructure.py

# Solo MySQL
python scripts/check_infrastructure.py --service mysql

# Solo RabbitMQ
python scripts/check_infrastructure.py --service rabbitmq

# Con detalles (conteos, versiones, colas)
python scripts/check_infrastructure.py --verbose
```

### Desarrollo
```bash
# Repoblar datos (mantiene estructura)
python scripts/seed_database.py --clean

# Ver estado de base de datos
docker exec -it flowlite-mysql mysql -u flowlite_user -p flowlite_db -e "SHOW TABLES;"

# Ver usuarios de prueba
docker exec -it flowlite-mysql mysql -u flowlite_user -p flowlite_db -e "SELECT email, role FROM User;"
```

### Reset Completo
```bash
# Eliminar TODO (estructura + datos)
docker-compose down -v
docker-compose up -d
python scripts/init_database.py
python scripts/seed_database.py
```

## Datos de Prueba Creados

### Usuarios (IdentityService)

| Email | Password | Role | Descripción |
|-------|----------|------|-------------|
| `juan.perez@example.com` | `password123` | USER | Usuario normal con transacciones |
| `maria.lopez@example.com` | `password123` | PREMIUM_USER | Usuario premium con transacciones |
| `admin@flowlite.com` | `admin123` | ADMIN | Administrador del sistema |
| `pedro.gomez@example.com` | `password123` | USER | Usuario inactivo (para testing) |

**Nota:** Contraseñas en texto plano solo para testing. En producción usar hashes.

### Bancos (UploadService)

- Bancolombia
- Davivienda
- Banco de Bogotá
- BBVA Colombia
- Nequi

### Categorías de Transacciones (UploadService)

- Alimentación
- Transporte
- Vivienda
- Salud
- Entretenimiento
- Educación
- Servicios Públicos
- Compras
- Otros
- Ingresos

### Transacciones (UploadService)

**Juan Pérez (6 transacciones):**
- Ingreso: Nómina $3,500,000
- Gastos: Supermercado, Uber, Servicios, Netflix, Restaurante

**María López (4 transacciones):**
- Ingreso: Freelance $2,800,000
- Gastos: Arriendo, Curso online, Amazon

### Categorías de Insights (InsightService)

- Ahorro
- Presupuesto
- Análisis de Gastos
- Análisis de Ingresos
- Tendencias
- Alertas

### Insights Generados (InsightService)

- 3 insights para Juan Pérez (gastos alimentación, ahorro transporte, presupuesto)
- 2 insights para María López (gasto vivienda, inversión educación)

## Estructura de Tablas Creadas

```
✓ User              - Usuarios del sistema (IdentityService)
✓ Role              - Roles de usuario (IdentityService)
✓ UserInfo          - Info adicional usuarios (IdentityService)
✓ Bank              - Bancos soportados (UploadService)
✓ TransactionCategory - Categorías (UploadService)
✓ TransactionBatch  - Lotes procesamiento (UploadService)
✓ Transaction       - Transacciones (UploadService)
✓ InsightCategory   - Categorías insights (InsightService)
✓ Insights          - Insights generados (InsightService)
✓ alembic_version   - Control de migraciones
```

## Testing con Datos Poblados

### Test IdentityService

```bash
# Login con usuario de prueba
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.perez@example.com",
    "password": "password123"
  }'

# Debería retornar un JWT token
```

### Test UploadService

```bash
# 1. Obtener token de IdentityService (ver arriba)
# 2. Subir archivo de transacciones
curl -X POST "http://localhost:8001/api/v1/transactions/upload?bank_code=BANCOLOMBIA" \
  -H "Authorization: Bearer <token>" \
  -F "files=@transactions.xlsx"
```

### Test InsightService

El InsightService consume automáticamente de RabbitMQ cuando UploadService procesa un lote.

Ver logs:
```bash
cd InsightService
python main.py

# Debería mostrar:
# "Listening for messages on queue: batch_processed"
```

## Verificación de Datos

### Ver usuarios en base de datos

```bash
docker exec -it flowlite-mysql mysql -u flowlite_user -p -e "
USE flowlite_db;
SELECT
    u.email,
    u.role,
    u.active,
    ui.primerNombre,
    ui.primerApellido
FROM User u
LEFT JOIN UserInfo ui ON u.id_user = ui.id_user;
"
```

### Ver transacciones por usuario

```bash
docker exec -it flowlite-mysql mysql -u flowlite_user -p -e "
USE flowlite_db;
SELECT
    u.email,
    COUNT(t.id_transaction) as total_transactions,
    SUM(CASE WHEN t.transaction_type = 'income' THEN t.value ELSE 0 END) as total_income,
    SUM(CASE WHEN t.transaction_type = 'expense' THEN t.value ELSE 0 END) as total_expenses
FROM User u
LEFT JOIN Transaction t ON u.id_user = t.id_user
GROUP BY u.id_user, u.email;
"
```

### Ver insights generados

```bash
docker exec -it flowlite-mysql mysql -u flowlite_user -p -e "
USE flowlite_db;
SELECT
    u.email,
    i.title,
    ic.description as category,
    i.relevance,
    i.created_at
FROM Insights i
JOIN User u ON i.id_user = u.id_user
JOIN InsightCategory ic ON i.id_category = ic.id_category
ORDER BY i.created_at DESC;
"
```

## Solución de Problemas

### "Can't connect to MySQL server"

```bash
# Verificar que MySQL esté corriendo
docker-compose ps

# Iniciar si no está corriendo
docker-compose up -d

# Ver logs
docker-compose logs mysql
```

### "Access denied for user"

Verificar credenciales en `.env`:
```bash
cat .env | grep MYSQL
```

Deben ser:
- MYSQL_USER=flowlite_user
- MYSQL_PASSWORD=flowlite_password
- MYSQL_DATABASE=flowlite_db

### "Table already exists"

```bash
# Opción 1: Limpiar datos (mantiene estructura)
python scripts/seed_database.py --clean

# Opción 2: Reset completo
docker-compose down -v
docker-compose up -d
python scripts/init_database.py
python scripts/seed_database.py
```

### "Module not found"

```bash
# Instalar dependencias
cd InfrastructureService
pip install -r requirements.txt
```

## Workflow Recomendado

### Desarrollo Diario

```bash
# Mañana - Iniciar todo
cd InfrastructureService
docker-compose up -d

# Si necesitas datos frescos
python scripts/seed_database.py --clean

# Iniciar servicios
cd ../identifyservice && uvicorn src.main:app --port 8000 &
cd ../uploadservice && uvicorn src.main:app --port 8001 &
cd ../InsightService && python main.py &
```

### Testing Específico

```bash
# Testing de IdentityService
python scripts/seed_database.py --clean  # Datos frescos
# Hacer pruebas de login/registro

# Testing de UploadService
python scripts/seed_database.py --clean  # Datos frescos
# Subir archivos Excel

# Testing de InsightService
# Los insights se generarán automáticamente después de subir transacciones
```

### Antes de Commit

```bash
# Verificar que scripts funcionen
docker-compose down -v
docker-compose up -d
python scripts/init_database.py
python scripts/seed_database.py

# Si todo funciona, hacer commit
```

## Personalización

### Modificar Usuarios de Prueba

Editar `scripts/seed_database.py`:

```python
users_data = [
    {
        "id_user": "user-custom-id",
        "username": "nuevo.usuario",
        "email": "nuevo@example.com",
        "password": "password123",
        "role": "USER",
        "active": True
    }
]
```

### Agregar Más Transacciones

Editar `scripts/seed_database.py` en la función `seed_transactions()`:

```python
transactions_custom = [
    {
        "id_user": "user-001-juan-perez",
        "id_category": "cat-001-alimentacion",
        "id_bank": "bank-001-bancolombia",
        "transaction_name": "NUEVA TRANSACCIÓN",
        "value": Decimal("-50000.00"),
        "transaction_date": datetime.now(),
        "transaction_type": "expense"
    }
]
```

### Agregar Nuevos Bancos

Editar `scripts/seed_database.py` en la función `seed_banks()`:

```python
banks_data = [
    {"id_bank": "bank-006-nuevo", "bank_name": "Banco Nuevo"},
]
```

## Logs y Debugging

### Ver progreso de scripts

Los scripts usan logging detallado:

```bash
python scripts/init_database.py
# Mostrará cada paso: conexión, migraciones, verificación

python scripts/seed_database.py
# Mostrará cada entidad creada con contadores
```

### Activar modo debug

Para ver queries SQL:

```python
# En seed_database.py, cambiar:
engine = create_engine(database_url, echo=True)  # echo=True muestra SQL
```

## Referencias

- Documentación completa: `scripts/README.md`
- Modelos de datos: `models.py`
- Migraciones: `alembic/versions/`
- Configuración: `.env.example`

## Soporte

Si tienes problemas:

1. Verificar que Docker esté corriendo
2. Verificar configuración en `.env`
3. Ver logs: `docker-compose logs`
4. Consultar `scripts/README.md` para más detalles
