# InfrastructureService - Flowlite Personal Finance

Este servicio centraliza toda la infraestructura compartida del proyecto Flowlite, incluyendo:
- Base de datos MySQL
- RabbitMQ (Message Broker)
- Redis (Cache y almacenamiento en memoria)
- Migraciones de base de datos (Alembic)

## 🚀 Quick Start (RECOMENDADO)

**Si es tu primera vez configurando el proyecto O si acabas de hacer git pull:**

```bash
cd infrastructureservice
./setup.sh
```

Este script automáticamente:
- ✓ Detecta y elimina imágenes Docker antiguas
- ✓ Reconstruye la imagen db-init con el código más reciente
- ✓ Inicializa la base de datos con las migraciones correctas
- ✓ Carga los datos de prueba (seed) con categorías ML
- ✓ Valida que todo esté configurado correctamente

### ⚠️ IMPORTANTE: Problema de Imágenes Antiguas

Docker cachea las imágenes construidas. Si tienes una imagen antigua del servicio `db-init`,
la base de datos puede cargarse con datos desactualizados (categorías antiguas en lugar de
categorías ML).

**Síntomas de este problema:**
- Las categorías tienen nombres como "Alimentación", "Servicios Públicos" (con espacios y tildes)
- En lugar de "Alimentacion_Restaurantes", "Servicios_Publicos" (con underscores)
- El clasificador ML no encuentra las categorías correctas

**Solución:** Usa `./setup.sh` que limpia automáticamente las imágenes antiguas.

**Alternativa manual:**
```bash
# 1. Detener servicios
docker-compose down

# 2. Eliminar imagen antigua
docker rmi $(docker images | grep infrastructureservice-db-init | awk '{print $3}')

# 3. Reconstruir sin caché
docker-compose build --no-cache db-init

# 4. Levantar servicios
docker-compose up -d
```

## 🔄 Control de Versiones del Seed

El proyecto utiliza un sistema de versionado para el seed de la base de datos que garantiza
que todos los desarrolladores usen la misma versión de datos de prueba.

### Ver la versión actual del seed:

```bash
# Ver la versión en docker-compose.yml
grep "SEED_VERSION:" docker-compose.yml

# Ver los logs del último seed ejecutado
docker logs flowlite-db-init | grep "Seed Version"
```

### Actualizar la versión del seed:

**Cuándo actualizar:** Cada vez que modifiques `scripts/seed_database.py` con cambios significativos
(nuevas categorías, cambios en estructura de datos, etc.).

**Cómo actualizar:**

1. Edita `docker-compose.yml` y cambia `SEED_VERSION`:
   ```yaml
   args:
     SEED_VERSION: "20251105-02"  # Incrementa la versión
   ```

2. Ejecuta el setup:
   ```bash
   ./setup.sh
   ```

El script `setup.sh` automáticamente detectará que cambió la versión y reconstruirá la imagen.

### Para Colaboradores:

Cuando hagas `git pull` y veas cambios en `seed_database.py` o `docker-compose.yml`:
```bash
./setup.sh  # Esto garantiza que uses la versión correcta
```

## Estructura

```
InfrastructureService/
├── docker-compose.yml          # Servicios de infraestructura (MySQL, RabbitMQ, Redis, DB-Init)
├── setup.sh                    # Script automatizado de setup (RECOMENDADO)
├── Dockerfile.init             # Dockerfile para el servicio de inicialización automática
├── .env.example                # Variables de entorno de ejemplo
├── .dockerignore               # Archivos a ignorar en la construcción de Docker
├── alembic.ini                 # Configuración de Alembic
├── models.py                   # Modelos compartidos de SQLAlchemy
├── requirements.txt            # Dependencias Python
├── alembic/
│   ├── env.py                  # Configuración del entorno de Alembic
│   ├── script.py.mako          # Template para nuevas migraciones
│   └── versions/
│       └── 001_initial_schema.py  # Migración inicial
├── scripts/
│   ├── init_database.py        # Script de inicialización de base de datos
│   ├── seed_database.py        # Script de población de datos de prueba
│   └── init_and_seed.sh        # Script que ejecuta init y seed automáticamente
└── README.md                   # Este archivo
```

## Servicios Incluidos

### MySQL 8.0
- **Puerto**: 3306 (configurable)
- **Base de datos**: flowlite_db
- **Usuario**: flowlite_user
- **Volumen persistente**: mysql_data

### RabbitMQ 3.12
- **Puerto AMQP**: 5672 (configurable)
- **Puerto Management UI**: 15672 (configurable)
- **Usuario**: admin
- **Management UI**: http://localhost:15672

### Redis 7
- **Puerto**: 6379 (configurable)
- **Password**: flowlite_redis_pass_2024 (configurable)
- **Uso**: Cache de sesiones, rate limiting, datos temporales
- **Volumen persistente**: redis_data

### DB-Init (Inicialización Automática)
- **Descripción**: Servicio que inicializa automáticamente la base de datos
- **Funcionalidad**: Ejecuta migraciones y seed de datos al iniciar
- **Dependencia**: Espera a que MySQL esté saludable antes de ejecutarse
- **Ejecución**: Se ejecuta una sola vez automáticamente

## Instalación y Configuración

### 1. Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.11+ (para ejecutar migraciones)

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y ajusta los valores según tu entorno:

```bash
cp .env.example .env
```

Edita `.env` con tus configuraciones:

```bash
# MySQL Configuration
MYSQL_ROOT_PASSWORD=tu_password_seguro
MYSQL_DATABASE=flowlite_db
MYSQL_USER=flowlite_user
MYSQL_PASSWORD=tu_password_usuario
MYSQL_PORT=3306
MYSQL_HOST=localhost

# RabbitMQ Configuration
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=tu_password_rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=tu_password_redis
REDIS_DB=0
```

### 3. Levantar la Infraestructura

```bash
cd InfrastructureService
docker-compose up -d
```

Este comando iniciará todos los servicios de infraestructura:
1. **MySQL** - Se iniciará y esperará a estar "healthy"
2. **RabbitMQ** - Se iniciará en paralelo
3. **Redis** - Se iniciará en paralelo
4. **DB-Init** - Esperará a que MySQL esté healthy y luego ejecutará automáticamente:
   - Las migraciones de Alembic (`init_database.py`)
   - El seed de datos de prueba (`seed_database.py`)

Verificar que los servicios estén corriendo:

```bash
docker-compose ps
```

Deberías ver:
- flowlite-mysql (healthy)
- flowlite-rabbitmq (running)
- flowlite-redis (running)
- flowlite-db-init (exited with code 0) - Este servicio se ejecuta una sola vez y luego termina

Para ver los logs de la inicialización de la base de datos:

```bash
docker-compose logs db-init
```

**Nota**: Con esta configuración, **NO necesitas ejecutar manualmente** los scripts `init_database.py` y `seed_database.py`. El servicio `db-init` los ejecuta automáticamente.

### 4. Verificar Infraestructura (Recomendado)

Antes de inicializar la base de datos, verifica que todo esté funcionando:

```bash
python scripts/check_infrastructure.py
```

Este script verifica:
- ✓ Contenedores Docker están corriendo
- ✓ MySQL es accesible y tiene las tablas correctas
- ✓ RabbitMQ está funcionando (AMQP y Management API)
- ✓ Redis es accesible y responde correctamente
- ✓ Todas las conexiones son exitosas

Si todo está bien, verás:
```
✓ Toda la infraestructura está funcionando correctamente
```

### 5. Instalar Dependencias para Migraciones

```bash
pip install -r requirements.txt
```

### 6. Inicializar Base de Datos (Opcional - Ya se hace automáticamente)

⚠️ **NOTA IMPORTANTE**: Con la configuración actual del docker-compose, el servicio `db-init` ya ejecuta automáticamente los scripts de inicialización y seed cuando ejecutas `docker-compose up -d`. Esta sección es solo para referencia o si necesitas re-inicializar manualmente.

Si por alguna razón necesitas ejecutar los scripts manualmente (por ejemplo, si el servicio db-init falló o si quieres re-poblar la base de datos):

**Opción A: Usando el script automático de inicialización**

```bash
python scripts/init_database.py
```

Este script:
- Verifica la conexión a MySQL
- Ejecuta todas las migraciones de Alembic
- Verifica que todas las tablas se crearon correctamente
- Muestra el estado de las migraciones

**Opción B: Ejecutar migraciones manualmente**

```bash
# Configurar la URL de la base de datos
export DATABASE_URL="mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db"

# Ejecutar migraciones
alembic upgrade head
```

Deberías ver la salida:

```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema for Flowlite database
```

### 7. Poblar Base de Datos con Datos de Prueba (Opcional - Ya se hace automáticamente)

⚠️ **NOTA IMPORTANTE**: El servicio `db-init` ya ejecuta automáticamente este script cuando ejecutas `docker-compose up -d`. Esta sección es solo para referencia.

Si necesitas re-poblar la base de datos manualmente:

```bash
# Limpiar y repoblar
python scripts/seed_database.py --clean
```

Este script crea:
- **Usuarios de prueba** para IdentityService (con credenciales de login)
- **Bancos y categorías** para UploadService
- **Transacciones de ejemplo** con diferentes fechas y tipos
- **Insights generados** para InsightService

Ver más detalles en: `scripts/README.md`

**Usuarios de prueba creados automáticamente:**
- Email: `juan.perez@example.com` / Password: `password123`
- Email: `maria.lopez@example.com` / Password: `password123`
- Email: `admin@flowlite.com` / Password: `admin123`

### 8. Verificar la Instalación Completa

Una vez inicializada y poblada la base de datos, verifica todo nuevamente:

```bash
python scripts/check_infrastructure.py --verbose
```

Esto mostrará:
- Estado de contenedores
- Conexiones a MySQL y RabbitMQ
- Conteo de registros en tablas clave
- Versiones de software

---

### 9. Verificación Manual (Opcional)

#### Verificar MySQL

```bash
# Conectarse a MySQL
docker exec -it flowlite-mysql mysql -u flowlite_user -p flowlite_db

# Dentro de MySQL, listar tablas
mysql> SHOW TABLES;
```

Deberías ver todas las tablas:
- Bank
- InsightCategory
- Insights
- Role
- Transaction
- TransactionBatch
- TransactionCategory
- User
- UserInfo
- alembic_version

#### Verificar RabbitMQ

1. Abre el Management UI: http://localhost:15672
2. Login con las credenciales de `.env` (default: admin/admin)
3. Verifica que el servidor esté corriendo correctamente

## Estructura de la Base de Datos

La base de datos `flowlite_db` contiene las siguientes tablas:

### Tablas de Usuario (IdentityService)
- **User**: Usuarios del sistema con credenciales de autenticación
- **Role**: Roles de usuarios (ADMIN, USER, PREMIUM_USER, etc.)
- **UserInfo**: Información adicional del usuario (nombre completo, dirección, teléfono, identificación)

### Tablas de Transacciones (UploadService)
- **Bank**: Bancos soportados (Bancolombia, Davivienda, etc.)
- **TransactionCategory**: Categorías de transacciones (Alimentación, Transporte, etc.)
- **TransactionBatch**: Lotes de procesamiento (pending, processing, completed, error)
- **Transaction**: Transacciones bancarias individuales

### Tablas de Insights (InsightService)
- **InsightCategory**: Categorías de insights (Ahorro, Presupuesto, Alertas, etc.)
- **Insights**: Insights generados automáticamente por IA

Todas las tablas usan UUID (CHAR(36)) como identificadores primarios.

### Diagrama de Relaciones

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id_user (PK)    │
│ username        │
│ email           │
│ password        │
│ role            │
│ active          │
└─────────┬───────┘
          │ 1:1
          │
┌─────────▼───────┐        ┌──────────────────┐
│    UserInfo     │        │       Role       │
├─────────────────┤        ├──────────────────┤
│ id_user (PK,FK) │        │ id_role (PK)     │
│ primerNombre    │        │ role_name        │
│ primerApellido  │        └──────────────────┘
│ telefono        │
│ direccion       │
│ numeroIdentif.  │
└─────────────────┘

┌────────────────────┐       ┌──────────────────────┐
│        Bank        │       │ TransactionCategory  │
├────────────────────┤       ├──────────────────────┤
│ id_bank (PK)       │       │ id_category (PK)     │
│ bank_name          │       │ description          │
└─────────┬──────────┘       └──────────┬───────────┘
          │                              │
          │                              │
┌─────────▼─────────────────────────────▼──────┐
│              Transaction                      │
├───────────────────────────────────────────────┤
│ id_transaction (PK)                           │
│ id_user (FK) ──────────────────┐              │
│ id_category (FK)                │              │
│ id_bank (FK)                    │              │
│ id_batch (FK)                   │              │
│ transaction_name                │              │
│ value                           │              │
│ transaction_date                │              │
│ transaction_type                │              │
└──────────────┬──────────────────┼──────────────┘
               │                  │
               │                  │
     ┌─────────▼────────┐         │
     │ TransactionBatch │         │
     ├──────────────────┤         │
     │ id_batch (PK)    │         │
     │ process_status   │         │
     │ start_date       │         │
     │ end_date         │         │
     │ batch_size       │         │
     └──────────────────┘         │
                                  │
┌─────────────────────────────────▼───────┐
│              Insights                   │
├─────────────────────────────────────────┤
│ id_insight (PK)                         │
│ id_user (FK) ───────────────┐           │
│ id_category (FK)             │           │
│ title                        │           │
│ text                         │           │
│ relevance                    │           │
│ created_at                   │           │
└──────────────────────────────┼───────────┘
                               │
                    ┌──────────▼──────────┐
                    │  InsightCategory    │
                    ├─────────────────────┤
                    │ id_category (PK)    │
                    │ description         │
                    └─────────────────────┘
```

## Uso en Servicios

### UploadService

El UploadService debe configurar las siguientes variables de entorno:

```bash
# Database
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin

# Redis (opcional para cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=flowlite_redis_pass_2024
REDIS_DB=0
```

**Nota**: El UploadService NO necesita ejecutar migraciones. Solo debe conectarse a la base de datos ya inicializada.

### InsightService

El InsightService debe configurar las siguientes variables de entorno:

```bash
# Database
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE=batch_processed

# Redis (opcional para cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=flowlite_redis_pass_2024
REDIS_DB=0
```

**Nota**: El InsightService NO necesita ejecutar migraciones. Solo debe conectarse a la base de datos ya inicializada.

## Gestión de Migraciones

### Crear una Nueva Migración

Si necesitas agregar o modificar tablas:

```bash
# Asegúrate de actualizar models.py primero
# Luego genera la migración automáticamente
alembic revision --autogenerate -m "descripcion de los cambios"

# Revisa el archivo generado en alembic/versions/
# Aplica la migración
alembic upgrade head
```

### Ver Historial de Migraciones

```bash
alembic history
```

### Revertir una Migración

```bash
# Revertir a la versión anterior
alembic downgrade -1

# Revertir a una versión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

## Comandos Útiles

### Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f mysql
docker-compose logs -f rabbitmq

# Reiniciar servicios
docker-compose restart

# Detener y eliminar volúmenes (PRECAUCIÓN: elimina datos)
docker-compose down -v
```

### MySQL

```bash
# Conectarse a MySQL
docker exec -it flowlite-mysql mysql -u flowlite_user -p flowlite_db

# Backup de la base de datos
docker exec flowlite-mysql mysqldump -u flowlite_user -pflowlite_password flowlite_db > backup.sql

# Restaurar backup
docker exec -i flowlite-mysql mysql -u flowlite_user -pflowlite_password flowlite_db < backup.sql
```

### RabbitMQ

```bash
# Ver estado de las colas
docker exec flowlite-rabbitmq rabbitmqctl list_queues

# Ver conexiones activas
docker exec flowlite-rabbitmq rabbitmqctl list_connections

# Ver exchanges
docker exec flowlite-rabbitmq rabbitmqctl list_exchanges
```

### Redis

```bash
# Conectarse a Redis CLI
docker exec -it flowlite-redis redis-cli -a flowlite_redis_pass_2024

# Dentro de Redis CLI, comandos útiles:
# PING - verificar conexión
# INFO - información del servidor
# KEYS * - listar todas las claves (usar con precaución en producción)
# GET clave - obtener valor de una clave
# FLUSHDB - limpiar base de datos actual (PRECAUCIÓN)
```

## Notas Importantes

### Drivers de MySQL

InfrastructureService usa **dos drivers de MySQL** dependiendo del contexto:

- **`pymysql`** (síncrono): Para scripts de Python (`init_database.py`, `seed_database.py`, `check_infrastructure.py`)
- **`aiomysql`** (asíncrono): Para servicios que usan async/await (UploadService, InsightService)

**Los scripts convierten automáticamente** `aiomysql` a `pymysql` si encuentran esa URL en `.env`, así que puedes usar una sola `DATABASE_URL` en tu `.env`:

```bash
# Esta URL funciona para ambos casos:
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# Los scripts la convierten automáticamente a:
# mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db
```

## Troubleshooting

### MySQL no inicia

1. Verificar logs: `docker-compose logs mysql`
2. Asegurarse de que el puerto 3306 no esté en uso
3. Verificar permisos del volumen

### RabbitMQ no es accesible

1. Verificar logs: `docker-compose logs rabbitmq`
2. Asegurarse de que los puertos 5672 y 15672 no estén en uso
3. Esperar unos segundos después de `docker-compose up` (RabbitMQ tarda en inicializar)

### Redis no es accesible

1. Verificar logs: `docker-compose logs redis`
2. Asegurarse de que el puerto 6379 no esté en uso
3. Verificar que el password en `.env` coincida con la configuración
4. Probar conexión: `docker exec -it flowlite-redis redis-cli -a flowlite_redis_pass_2024 PING`

### Migraciones fallan

1. Verificar que MySQL esté corriendo: `docker-compose ps`
2. Verificar que la URL de base de datos sea correcta
3. Verificar que el usuario tenga permisos: `GRANT ALL PRIVILEGES ON flowlite_db.* TO 'flowlite_user'@'%';`

### Error de conexión desde servicios

1. Si los servicios corren en Docker, usa `MYSQL_HOST=mysql` (nombre del servicio)
2. Si los servicios corren localmente, usa `MYSQL_HOST=localhost`
3. Verificar que las credenciales coincidan con `.env`

## Seguridad

En producción, asegúrate de:

1. Cambiar todas las contraseñas por defecto
2. Usar contraseñas fuertes
3. No exponer el puerto de MySQL (3306) públicamente
4. Configurar firewall para RabbitMQ
5. Usar SSL/TLS para conexiones de base de datos
6. Mantener los contenedores actualizados

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────┐
│              InfrastructureService                               │
│                                                                  │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐             │
│  │  MySQL   │      │ RabbitMQ │      │  Redis   │             │
│  │(flowlite_│      │ (Message │      │  (Cache) │             │
│  │   db)    │      │  Broker) │      │          │             │
│  │Port: 3306│      │Port: 5672│      │Port: 6379│             │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘             │
│       │                 │                  │                   │
└───────┼─────────────────┼──────────────────┼───────────────────┘
        │                 │                  │
        │                 │                  │
    ┌───▼────┐       ┌────▼────┐       ┌────▼────┐
    │ Upload │       │ Insight │       │Identity │
    │Service │──────►│ Service │       │ Service │
    │        │(msgs) │         │       │         │
    └────┬───┘       └────┬────┘       └────┬────┘
         │                │                  │
         │     MySQL (reads/writes)          │
         └────────────────┬──────────────────┘
                          │
                     Shared DB

    Redis: Cache compartido para todos los servicios
```

## Contacto y Soporte

Para reportar problemas o solicitar nuevas características, crea un issue en el repositorio del proyecto.
