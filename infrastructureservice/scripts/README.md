# Scripts de InfrastructureService

Scripts para gestionar y verificar la infraestructura compartida de Flowlite.

## Scripts Disponibles

### 1. `check_infrastructure.py` - Verificación de Infraestructura ✨ NUEVO

Verifica que todos los servicios de infraestructura estén funcionando correctamente.

**Uso:**
```bash
cd InfrastructureService

# Verificación completa
python scripts/check_infrastructure.py

# Con información detallada
python scripts/check_infrastructure.py --verbose

# Solo MySQL
python scripts/check_infrastructure.py --service mysql

# Solo RabbitMQ
python scripts/check_infrastructure.py --service rabbitmq

# Solo Redis
python scripts/check_infrastructure.py --service redis
```

**¿Qué verifica?**

**Docker:**
- ✓ Docker está instalado
- ✓ Contenedor flowlite-mysql está corriendo
- ✓ Contenedor flowlite-rabbitmq está corriendo
- ✓ Contenedor flowlite-redis está corriendo

**MySQL:**
- ✓ Conexión exitosa
- ✓ Consultas funcionan
- ✓ Todas las tablas existen
- ✓ Migraciones aplicadas
- ✓ (Verbose) Conteo de registros por tabla

**RabbitMQ:**
- ✓ Conexión AMQP funciona
- ✓ Management API accesible
- ✓ Cola 'batch_processed' existe
- ✓ (Verbose) Versiones y colas configuradas

**Redis:**
- ✓ Conexión exitosa
- ✓ Comando PING responde
- ✓ Operaciones de lectura/escritura funcionan
- ✓ (Verbose) Versión del servidor e información detallada

**Salida Esperada:**
```
============================================================
VERIFICACIÓN DE INFRAESTRUCTURA - FLOWLITE
============================================================

✓ Variables de entorno cargadas desde .env

Verificando Contenedores Docker
------------------------------------------------------------
  Docker: Docker version 24.0.0
✓ Contenedor MySQL (flowlite-mysql) está corriendo
✓ Contenedor RabbitMQ (flowlite-rabbitmq) está corriendo
✓ Contenedor Redis (flowlite-redis) está corriendo

Verificando MySQL
------------------------------------------------------------
  Conectando a: flowlite_user@localhost:3306/flowlite_db
✓ Conexión a MySQL exitosa
✓ MySQL versión: 8.0.35
✓ Base de datos tiene 10 tablas
✓ Todas las tablas esperadas están presentes
✓ Migración actual: 001

Verificando RabbitMQ
------------------------------------------------------------
  Conectando AMQP a: localhost:5672
✓ Conexión AMQP a RabbitMQ exitosa
✓ Cola 'batch_processed' existe (0 mensajes)
  Verificando Management API: http://localhost:15672/api/overview
✓ Management API accesible
  Management UI: http://localhost:15672

Verificando Redis
------------------------------------------------------------
  Conectando a: localhost:6379
✓ Conexión a Redis exitosa
✓ Redis responde correctamente: PONG
✓ Redis versión: 7.0.0
✓ Operaciones de lectura/escritura funcionan

============================================================
RESUMEN DE VERIFICACIÓN
============================================================

DOCKER:
  ✓ Disponible

MYSQL:
  ✓ connection
  ✓ query
  ✓ tables
  ✓ migrations

RABBITMQ:
  ✓ amqp
  ✓ management
  ✓ queues

REDIS:
  ✓ connection
  ✓ ping
  ✓ info

Estado General:
  Checks pasados: 12/12 (100%)

✓ Toda la infraestructura está funcionando correctamente
```

**Prerequisitos:**
- Docker y docker-compose instalados
- Servicios iniciados: `docker-compose up -d`
- (Opcional) `pika`, `requests` y `redis` para verificaciones completas:
  ```bash
  pip install pika requests redis
  ```

---

### 2. `init_database.py` - Inicialización de Base de Datos

Inicializa la estructura completa de la base de datos ejecutando las migraciones de Alembic.

**Uso:**
```bash
cd InfrastructureService
python scripts/init_database.py
```

**¿Qué hace?**
- Verifica la conexión a MySQL
- Ejecuta todas las migraciones de Alembic
- Crea todas las tablas necesarias:
  - `User` - Usuarios del sistema
  - `Role` - Roles de usuario
  - `UserInfo` - Información adicional de usuarios
  - `Bank` - Bancos soportados
  - `TransactionCategory` - Categorías de transacciones
  - `TransactionBatch` - Lotes de procesamiento
  - `Transaction` - Transacciones individuales
  - `InsightCategory` - Categorías de insights
  - `Insights` - Insights generados
- Verifica que todas las tablas se crearon correctamente

**Prerequisitos:**
- MySQL debe estar corriendo: `docker-compose up -d`
- Variables de entorno configuradas en `.env`

**Salida Esperada:**
```
============================================================
INICIALIZACIÓN DE BASE DE DATOS - FLOWLITE
============================================================
✓ Conexión a base de datos exitosa
✓ Migraciones ejecutadas exitosamente

Tablas encontradas: 10
  ✓ User
  ✓ Role
  ✓ UserInfo
  ✓ Bank
  ✓ TransactionCategory
  ✓ TransactionBatch
  ✓ Transaction
  ✓ InsightCategory
  ✓ Insights
  ✓ alembic_version

✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE
```

---

### 2. `seed_database.py` - Población de Datos de Prueba

Puebla la base de datos con datos de prueba para los tres servicios.

**Uso Básico:**
```bash
cd InfrastructureService
python scripts/seed_database.py
```

**Uso Avanzado:**
```bash
# Limpiar datos existentes antes de poblar
python scripts/seed_database.py --clean
```

**⚠️ ADVERTENCIA:** La opción `--clean` eliminará TODOS los datos existentes.

**¿Qué datos crea?**

#### IdentityService
- **3 Roles:**
  - ADMIN
  - USER
  - PREMIUM_USER

- **4 Usuarios de prueba:**
  1. **Juan Pérez** (USER activo)
     - Email: `juan.perez@example.com`
     - Password: `password123`
     - Con transacciones e insights

  2. **María López** (PREMIUM_USER activo)
     - Email: `maria.lopez@example.com`
     - Password: `password123`
     - Con transacciones e insights

  3. **Admin** (ADMIN activo)
     - Email: `admin@flowlite.com`
     - Password: `admin123`

  4. **Pedro Gómez** (USER inactivo)
     - Email: `pedro.gomez@example.com`
     - Para testing de usuarios inactivos

- **Información de Usuario (UserInfo):**
  - Nombres completos
  - Teléfonos
  - Direcciones
  - Ciudades y departamentos
  - Números de identificación

#### UploadService
- **5 Bancos:**
  - Bancolombia
  - Davivienda
  - Banco de Bogotá
  - BBVA Colombia
  - Nequi

- **10 Categorías de Transacciones:**
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

- **3 Lotes de Transacciones:**
  - 2 completados (con diferentes fechas)
  - 1 en procesamiento

- **10 Transacciones de ejemplo:**
  - 6 transacciones para Juan Pérez
  - 4 transacciones para María López
  - Incluyen gastos e ingresos
  - Fechas variadas (último mes)

#### InsightService
- **6 Categorías de Insights:**
  - Ahorro
  - Presupuesto
  - Análisis de Gastos
  - Análisis de Ingresos
  - Tendencias
  - Alertas

- **5 Insights generados:**
  - 3 insights para Juan Pérez
  - 2 insights para María López
  - Diferentes niveles de relevancia
  - Recomendaciones personalizadas

**Salida Esperada:**
```
============================================================
POBLACIÓN DE BASE DE DATOS - FLOWLITE
============================================================

📋 Poblando Roles...
  + ADMIN
  + USER
  + PREMIUM_USER
✓ 3 roles creados

👥 Poblando Usuarios...
  ✓ juan.perez@example.com (USER)
  ✓ maria.lopez@example.com (PREMIUM_USER)
  ✓ admin@flowlite.com (ADMIN)
  ✗ pedro.gomez@example.com (USER)
✓ 4 usuarios creados

[... más salida ...]

============================================================
📊 RESUMEN DE DATOS CREADOS
============================================================
  Roles: 3
  Usuarios: 4
  Información de Usuarios: 3
  Bancos: 5
  Categorías de Transacciones: 10
  Lotes de Transacciones: 3
  Transacciones: 10
  Categorías de Insights: 6
  Insights: 5

✅ BASE DE DATOS POBLADA EXITOSAMENTE
```

---

## Flujo de Trabajo Completo

### Primera Vez (Setup Inicial)

```bash
# 1. Iniciar infraestructura
cd InfrastructureService
docker-compose up -d

# 2. Verificar que todo esté funcionando
python scripts/check_infrastructure.py

# 3. Inicializar estructura de base de datos
python scripts/init_database.py

# 4. Poblar con datos de prueba
python scripts/seed_database.py

# 5. Verificar nuevamente (ahora con datos)
python scripts/check_infrastructure.py --verbose
```

### Testing y Desarrollo

```bash
# Repoblar datos (mantiene estructura, reemplaza datos)
python scripts/seed_database.py --clean

# Solo estructura (sin datos)
python scripts/init_database.py
```

### Resetear Todo

```bash
# Opción 1: Eliminar volúmenes de Docker (más drástico)
cd InfrastructureService
docker-compose down -v
docker-compose up -d
python scripts/init_database.py
python scripts/seed_database.py

# Opción 2: Solo limpiar datos (mantiene estructura)
python scripts/seed_database.py --clean
```

---

## Troubleshooting

### Error: "Can't connect to MySQL server"

**Problema:** MySQL no está corriendo o no es accesible.

**Solución:**
```bash
# Verificar estado de MySQL
docker-compose ps

# Si no está corriendo, iniciarlo
docker-compose up -d

# Ver logs si hay problemas
docker-compose logs mysql
```

### Error: "Access denied for user"

**Problema:** Credenciales incorrectas en `.env`

**Solución:**
```bash
# Verificar que .env tenga las credenciales correctas
cat .env

# Deben coincidir con docker-compose.yml
# Por defecto:
# MYSQL_USER=flowlite_user
# MYSQL_PASSWORD=flowlite_password
# MYSQL_DATABASE=flowlite_db
```

### Error: "alembic: command not found"

**Problema:** Dependencias no instaladas.

**Solución:**
```bash
cd InfrastructureService
pip install -r requirements.txt
```

### Error: "Table 'X' already exists"

**Problema:** Base de datos ya tiene datos.

**Solución:**
```bash
# Opción 1: Limpiar y repoblar
python scripts/seed_database.py --clean

# Opción 2: Resetear completamente
docker-compose down -v
docker-compose up -d
python scripts/init_database.py
python scripts/seed_database.py
```

---

## Notas Importantes

### Seguridad

⚠️ **Los datos de prueba NO son seguros para producción:**

- Las contraseñas están en texto plano (`password123`, `admin123`)
- Los IDs son predecibles para facilitar testing
- No hay validación de emails

**En producción:**
- Usar contraseñas hasheadas (bcrypt, argon2)
- Generar IDs aleatorios
- Validar todos los datos de entrada
- No usar estos scripts

### Performance

Los scripts están optimizados para datos de prueba pequeños:
- Seed completo toma ~2-3 segundos
- No usar para datasets grandes
- Para producción, usar herramientas especializadas

### Customización

Puedes modificar los datos de prueba editando:
- `seed_database.py` - Cambiar usuarios, transacciones, etc.
- `models.py` - Cambiar estructura de tablas
- Después de cambiar modelos, crear nueva migración:
  ```bash
  alembic revision --autogenerate -m "descripción"
  alembic upgrade head
  ```

---

## Dependencias

Scripts de base de datos (init_database.py, seed_database.py):
- `sqlalchemy` - ORM
- `pymysql` - Driver MySQL
- `python-dotenv` - Variables de entorno
- `alembic` - Migraciones (solo init_database.py)

Script de verificación (check_infrastructure.py):
- `python-dotenv` - Variables de entorno
- `pika` - Cliente RabbitMQ (opcional)
- `requests` - Cliente HTTP (opcional)
- `redis` - Cliente Redis (opcional)

Instalación:
```bash
# Dependencias básicas
pip install -r requirements.txt

# Dependencias opcionales para check_infrastructure.py
pip install pika requests redis
```

---

## Soporte

Si encuentras problemas:
1. Verifica que MySQL esté corriendo
2. Revisa los logs: `docker-compose logs mysql`
3. Confirma que `.env` esté configurado
4. Asegúrate de tener las dependencias instaladas

Para más ayuda, consulta:
- `InfrastructureService/README.md`
- `InfrastructureService/.env.example`
