# 🚀 Guía de Inicio Rápido - InsightService

## Descripción

El InsightService es un **servicio híbrido** que combina:

1. **API HTTP (Puerto 8002)**:
   - Health checks y monitoreo
   - Verificación de estado de base de datos
   - Información del servicio

2. **Consumidor RabbitMQ**:
   - Escucha mensajes en una cola de RabbitMQ
   - Procesa eventos de transacciones
   - Genera insights usando un modelo LLM (Ollama)
   - Guarda los resultados en la base de datos

## Prerrequisitos

Antes de iniciar el InsightService, asegúrate de tener:

1. **Python 3.11+** instalado
2. **InfrastructureService** corriendo con:
   - MySQL en puerto 3306 (base de datos compartida)
   - RabbitMQ en puerto 5672
3. **Servidor Ollama** con modelo `llama3.1:8b` disponible

## Inicio Rápido

### 1. Verificar InfrastructureService

```bash
cd ../InfrastructureService
docker-compose ps

# Deberías ver:
# - flowlite-mysql (puerto 3306)
# - flowlite-rabbitmq (puertos 5672, 15672)
# - flowlite-redis (puerto 6379)
```

### 2. Verificar Ollama

```bash
# Si Ollama está en localhost
curl http://localhost:11434/api/tags

# Si Ollama está en servidor remoto
curl http://IP_SERVIDOR:11434/api/tags

# Debería listar los modelos disponibles, incluyendo llama3.1:8b
```

### 3. Iniciar InsightService

```bash
cd InsightService
./start.sh
```

El script automáticamente:
- ✅ Verifica el archivo `.env`
- ✅ Crea/activa el entorno virtual
- ✅ Instala las dependencias
- ✅ Verifica conexión a MySQL, RabbitMQ y Ollama
- ✅ Inicia el consumidor de mensajes

## Configuración

El archivo `.env` contiene todas las configuraciones necesarias:

```bash
# Base de datos MySQL compartida
DATABASE_URL=mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# RabbitMQ compartido con InfrastructureService
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE=batch_processed

# Servidor Ollama para generación de insights
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=120

# Logging
LOG_LEVEL=INFO

# API HTTP (Health Check y monitoreo)
API_HOST=0.0.0.0
API_PORT=8002
```

## Cómo Funciona

### Flujo de Procesamiento

1. **UploadService** procesa un archivo de transacciones
2. **UploadService** guarda las transacciones en la base de datos
3. **UploadService** envía un mensaje a RabbitMQ con el `batch_id`
4. **InsightService** (este servicio) recibe el mensaje
5. **InsightService** consulta las transacciones del lote
6. **InsightService** envía las transacciones al modelo LLM
7. **LLM** genera insights financieros personalizados
8. **InsightService** guarda los insights en la base de datos

### Formato del Mensaje RabbitMQ

```json
{
  "user_id": "uuid-del-usuario",
  "batch_id": "uuid-del-lote",
  "transaction_count": 25,
  "timestamp": "2024-10-28T12:00:00Z"
}
```

## Verificación

### Verificar API HTTP

```bash
# Health Check básico
curl http://localhost:8002/health

# Verificar conexión a base de datos
curl http://localhost:8002/health/db

# Health check completo (todos los componentes)
curl http://localhost:8002/health/full

# Información del servicio
curl http://localhost:8002/info

# Documentación interactiva
open http://localhost:8002/docs
```

### Ver logs del servicio

Los logs mostrarán:
- Inicio del servidor HTTP en puerto 8002
- Conexión a RabbitMQ
- Mensajes recibidos
- Consultas a la base de datos
- Generación de insights con el LLM
- Guardado de resultados

```bash
# Los logs aparecen en la consola donde ejecutaste ./start.sh
# Ejemplo de log:
INFO - Starting API server on 0.0.0.0:8002
INFO - Connecting to RabbitMQ...
INFO - Service started successfully
INFO - API available at: http://localhost:8002/health
INFO - Listening for messages on queue: batch_processed
INFO - Received message for batch: abc-123-def
INFO - Generating insights for 25 transactions...
INFO - Insight generated successfully
```

### Verificar RabbitMQ

```bash
# Acceder a RabbitMQ Management UI
open http://localhost:15672

# Credenciales: admin / admin
# Navegar a Queues > batch_processed
```

### Verificar que se guardaron los insights

```bash
# Conectarse a MySQL
mysql -u flowlite_user -p flowlite_db

# Ver insights generados
SELECT * FROM Insight ORDER BY created_at DESC LIMIT 5;
```

## Arquitectura

```
InsightService/
├── main.py                    # Punto de entrada
├── src/
│   ├── domain/                # Lógica de negocio
│   │   ├── entities/          # Insight, Transaction
│   │   └── services/          # InsightGenerator
│   ├── application/           # Casos de uso
│   │   └── generate_insights_use_case.py
│   ├── infrastructure/        # Implementaciones
│   │   ├── database/          # MySQL repositories
│   │   ├── llm/               # Cliente Ollama
│   │   ├── messaging/         # RabbitMQ consumer
│   │   └── config/            # Configuración
│   └── interfaces/            # Adaptadores
│       └── message_handler.py # Handler de mensajes
```

## Solución de Problemas

### Error: "Cannot connect to RabbitMQ"

```bash
# Verificar que RabbitMQ está corriendo
docker ps | grep rabbitmq

# Ver logs de RabbitMQ
cd ../InfrastructureService
docker-compose logs rabbitmq

# Reiniciar RabbitMQ
docker-compose restart rabbitmq
```

### Error: "Cannot connect to MySQL"

```bash
# Verificar que MySQL está corriendo
docker ps | grep mysql

# Probar conexión
mysql -h localhost -u flowlite_user -p

# Ver logs de MySQL
cd ../InfrastructureService
docker-compose logs mysql
```

### Error: "Cannot connect to Ollama"

```bash
# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# Si usas servidor remoto, verificar firewall
ping IP_SERVIDOR

# Verificar que el modelo está instalado
ollama list | grep llama3.1
```

### Error: "Model not found"

```bash
# Instalar el modelo en el servidor Ollama
ollama pull llama3.1:8b

# Verificar instalación
ollama list
```

### No recibe mensajes

```bash
# Verificar que la cola existe
curl -u admin:admin http://localhost:15672/api/queues/%2F/batch_processed

# Enviar mensaje de prueba
cd scripts
python send_test_message.py <user_id> <batch_id>
```

## Pruebas

### Enviar mensaje de prueba

```bash
# Script para enviar mensaje de prueba a RabbitMQ
cd scripts
python send_test_message.py <user_id> <batch_id>

# Ejemplo:
python send_test_message.py "4b2e4192-0712-4f6e-8125-c480b15059ee" "abc-123-def"
```

### Verificar generación de insights

1. Sube un archivo de transacciones usando UploadService
2. El UploadService enviará un mensaje automáticamente
3. Observa los logs del InsightService para ver el procesamiento
4. Verifica que los insights se guardaron en la base de datos

## Detener el Servicio

### Opción 1: Usar el script kill.sh (Recomendado)

```bash
./kill.sh
```

### Opción 2: Manualmente

Presiona `Ctrl+C` en la terminal donde está corriendo el servicio.

El servicio cerrará la conexión a RabbitMQ gracefully.

## Base de Datos Compartida

Este servicio usa la base de datos `flowlite_db` compartida:

- **Tabla User**: Gestionada por IdentityService
- **Tabla Transaction**: Gestionada por UploadService
- **Tabla TransactionBatch**: Gestionada por UploadService
- **Tabla Insight**: Gestionada por InsightService

## Servicios del Ecosistema

```
┌─────────────────────┐
│ InfrastructureService│
│  (MySQL, RabbitMQ)  │
└──────────┬──────────┘
           │
           ├─────► IdentityService (puerto 8000)
           │        └─► Gestión de usuarios y autenticación
           │
           ├─────► UploadService (puerto 8001)
           │        └─► Procesa archivos, guarda transacciones
           │
           └─────► InsightService (NO tiene puerto)
                    └─► Genera insights con IA
```

## Monitoreo

### RabbitMQ Management

- **URL**: http://localhost:15672
- **Usuario**: admin
- **Password**: admin

Aquí puedes ver:
- Mensajes en la cola
- Consumidores conectados
- Rate de procesamiento
- Errores

### Logs

Los logs del servicio incluyen:
- Conexión a servicios externos
- Mensajes recibidos
- Tiempo de procesamiento
- Errores y stack traces

## Variables de Entorno Importantes

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a MySQL | `mysql+pymysql://flowlite_user:...` |
| `RABBITMQ_HOST` | Host de RabbitMQ | `localhost` |
| `RABBITMQ_QUEUE` | Cola a consumir | `batch_processed` |
| `OLLAMA_HOST` | URL del servidor Ollama | `http://localhost:11434` |
| `LLM_MODEL` | Modelo LLM a usar | `llama3.1:8b` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `API_HOST` | Host del servidor HTTP | `0.0.0.0` |
| `API_PORT` | Puerto del servidor HTTP | `8002` |

## Endpoints HTTP API

El InsightService expone una API REST en el puerto 8002 para monitoreo y health checks:

### GET /

Endpoint raíz del servicio

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2024-10-28T12:00:00.000Z",
  "service": "InsightService",
  "version": "1.0.0"
}
```

### GET /health

Health check básico del servicio

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-10-28T12:00:00.000Z",
  "service": "InsightService",
  "version": "1.0.0"
}
```

### GET /health/db

Verificación de conexión a la base de datos

**Response (Success - 200)**:
```json
{
  "status": "healthy",
  "database": "MySQL",
  "connected": true,
  "timestamp": "2024-10-28T12:00:00.000Z",
  "message": "Database connection successful"
}
```

**Response (Error - 503)**:
```json
{
  "status": "unhealthy",
  "database": "MySQL",
  "connected": false,
  "timestamp": "2024-10-28T12:00:00.000Z",
  "message": "Database connection failed: ..."
}
```

### GET /health/full

Health check completo de todos los componentes

**Response**:
```json
{
  "service": "InsightService",
  "status": "healthy",
  "timestamp": "2024-10-28T12:00:00.000Z",
  "components": {
    "database": {
      "status": "healthy",
      "type": "MySQL"
    },
    "rabbitmq": {
      "status": "configured",
      "queue": "batch_processed"
    },
    "llm": {
      "status": "configured",
      "host": "http://localhost:11434",
      "model": "llama3.1:8b"
    }
  }
}
```

### GET /info

Información detallada del servicio

**Response**:
```json
{
  "service": "InsightService",
  "version": "1.0.0",
  "description": "Financial Insights Service with AI-powered analysis",
  "config": {
    "database": "localhost:3306/flowlite_db",
    "rabbitmq": {
      "host": "localhost",
      "port": 5672,
      "queue": "batch_processed"
    },
    "llm": {
      "model": "llama3.1:8b",
      "temperature": 0.7
    },
    "api": {
      "host": "0.0.0.0",
      "port": 8002
    }
  },
  "timestamp": "2024-10-28T12:00:00.000Z"
}
```

### GET /docs

Documentación interactiva de la API (Swagger UI)

---

Para más información, consulta:
- **README.md**: Documentación completa del servicio
- **InfrastructureService**: Configuración de MySQL y RabbitMQ
