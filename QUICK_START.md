# 🚀 Flowlite - Personal Finance Platform

Sistema de gestión de finanzas personales con análisis automático mediante IA.

## Arquitectura de Microservicios

```
┌─────────────────────────────────────────────────────────┐
│                  FLOWLITE ECOSYSTEM                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  InfrastructureService (Docker)                        │
│  ├─ MySQL (3306)        - Base de datos compartida    │
│  ├─ Redis (6379)        - Cache y blacklist tokens    │
│  └─ RabbitMQ (5672)     - Mensajería asíncrona        │
│                                                         │
│  IdentityService (Java/Spring Boot - Puerto 8000)     │
│  ├─ Autenticación y gestión de usuarios               │
│  ├─ JWT token generation/validation                   │
│  └─ OAuth2 (Google, GitHub, Microsoft, Facebook)     │
│                                                         │
│  UploadService (Python/FastAPI - Puerto 8001)         │
│  ├─ Procesamiento de archivos Excel                   │
│  ├─ Clasificación automática de transacciones         │
│  └─ Publicación de eventos a RabbitMQ                 │
│                                                         │
│  InsightService (Python - Puerto 8002)                │
│  ├─ API HTTP para health checks y monitoreo           │
│  ├─ Consumo de eventos de transacciones (RabbitMQ)    │
│  ├─ Generación de insights usando LLM (Ollama)        │
│  └─ Persistencia de análisis en base de datos         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerrequisitos

### Software Requerido

- **Docker & Docker Compose** (para InfrastructureService)
- **Java 17+** (para IdentityService)
- **Python 3.11+** (para UploadService e InsightService)
- **Ollama** con modelo `llama3.1:8b` (para InsightService)

### Verificar Instalaciones

```bash
# Docker
docker --version
docker-compose --version

# Java
java -version

# Python
python3 --version

# Ollama (si está instalado localmente)
ollama list
```

## 🚀 Inicio Rápido

### Opción 1: Iniciar Todos los Servicios

```bash
./build_app.sh
```

Este script iniciará automáticamente todos los servicios en el orden correcto:
1. InfrastructureService (MySQL, Redis, RabbitMQ)
2. IdentityService (puerto 8000)
3. InsightService (consumidor RabbitMQ)
4. UploadService (puerto 8001)

### Opción 2: Iniciar Servicios Individualmente

```bash
# 1. Infrastructure (SIEMPRE PRIMERO)
cd InfrastructureService
docker-compose up -d

# 2. Identity Service
cd identifyservice
./start.sh

# 3. Insight Service
cd InsightService
./start.sh

# 4. Upload Service
cd uploadservice
./start.sh
```

## 🛑 Detener Todos los Servicios

```bash
./destroy_app.sh
```

Este script detendrá todos los servicios y contenedores Docker de manera ordenada.

## 📊 Verificar que Todo Funciona (Manual)

### 1. InfrastructureService

```bash
# Ver contenedores corriendo
docker ps

# Deberías ver:
# - flowlite-mysql
# - flowlite-redis
# - flowlite-rabbitmq

# Acceder a RabbitMQ Management UI
open http://localhost:15672
# Usuario: admin / Password: admin
```

### 2. IdentityService

```bash
# Health check
curl http://localhost:8000/actuator/health

# Swagger UI
open http://localhost:8000/swagger-ui.html
```

### 3. InsightService

```bash
# Health check
curl http://localhost:8002/health

# Database check
curl http://localhost:8002/health/db

# API Docs
open http://localhost:8002/docs
```

### 4. UploadService

```bash
# Health check
curl http://localhost:8001/health

# API Docs
open http://localhost:8001/docs
```

## 📖 Guías Detalladas

Cada servicio tiene su propia guía de inicio rápido:

- **IdentityService**: `identifyservice/START_GUIDE.md`
- **UploadService**: `uploadservice/START_GUIDE.md`
- **InsightService**: `InsightService/START_GUIDE.md`
- **InfrastructureService**: `InfrastructureService/README.md`

## 🔑 Flujo de Uso Completo

### 1. Registrar Usuario

```bash
curl -X POST "http://<server route>:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. Obtener Token

```bash
curl -X POST "http://<server route>:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

Guarda el `token` de la respuesta.

### 3. Subir Archivo de Transacciones

```bash
curl -X POST "http://<server route>:8001/api/v1/transactions/upload?bank_code=BANCOLOMBIA" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -F "files=@/ruta/a/tu/archivo.xlsx"
```

Respuesta:
```json
{
  "batch_id": "abc-123-def-456",
  "status": "PENDING",
  "message": "Archivo recibido y procesándose"
}
```

### 4. Consultar Estado del Lote

```bash
curl -X GET "http://<server route>:8001/api/v1/transactions/batch/abc-123-def-456" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

### 5. Los Insights se Generan Automáticamente

El InsightService detectará el evento y generará análisis usando IA. Los insights se guardan en la base de datos.

## 📁 Estructura del Proyecto

```
Flowlite-Personal-Finance/
├── build_app.sh                # 🚀 Iniciar todos los servicios
├── destroy_app.sh              # 🛑 Detener todos los servicios
├── dashboard.html              # 🎛️ Dashboard de monitoreo
├── QUICK_START.md              # 📖 Esta guía
├── logs/                       # 📝 Logs de los servicios
│   ├── identifyservice.log
│   ├── uploadservice.log
│   └── insightservice.log
│
├── InfrastructureService/      # 🏗️ Infraestructura compartida
│   ├── docker-compose.yml
│   └── README.md
│
├── identifyservice/            # 🔐 Autenticación
│   ├── start.sh
│   ├── START_GUIDE.md
│   └── src/
│
├── uploadservice/              # 📤 Carga de archivos
│   ├── start.sh
│   ├── START_GUIDE.md
│   └── src/
│
└── InsightService/             # 🤖 Análisis con IA
    ├── start.sh
    ├── START_GUIDE.md
    └── src/
```

## 📝 Logs

Los logs de cada servicio se guardan en el directorio `logs/`:

```bash
# Ver logs en tiempo real
tail -f logs/identifyservice.log
tail -f logs/uploadservice.log
tail -f logs/insightservice.log

# Ver logs de infraestructura
cd InfrastructureService
docker-compose logs -f mysql
docker-compose logs -f rabbitmq
```

## 🔧 Configuración

Cada servicio tiene su archivo `.env` con configuraciones específicas:

- **identifyservice/.env**: Puerto, JWT secret, database, OAuth2
- **uploadservice/.env**: Puerto, database, RabbitMQ, IdentityService URL
- **InsightService/.env**: Database, RabbitMQ, Ollama host

## 🐛 Solución de Problemas

### Puertos en Uso

Si algún puerto está ocupado:

```bash
# Ver qué proceso usa el puerto 8000
lsof -i :8000

# Matar el proceso
lsof -ti:8000 | xargs kill -9
```

### Servicios No Inician

```bash
# Ver logs para diagnosticar
tail -f logs/identifyservice.log
tail -f logs/uploadservice.log
tail -f logs/insightservice.log

# Verificar que Infrastructure esté corriendo
docker ps
```

### Base de Datos

```bash
# Conectarse a MySQL
mysql -h localhost -u flowlite_user -p flowlite_db
# Password: flowlite_password

# Ver tablas
SHOW TABLES;
```

### RabbitMQ

```bash
# Acceder a Management UI
open http://localhost:15672
# Usuario: admin / Password: admin

# Ver colas y mensajes
```

## 🔒 Seguridad

**IMPORTANTE**:
- Cambiar todas las contraseñas en producción
- No commitear archivos `.env` al repositorio
- Usar secrets managers en producción
- Configurar HTTPS/TLS

## 🎯 Endpoints Principales

### IdentityService (8000)

```
POST   /api/auth/register          # Registrar usuario
POST   /api/auth/login             # Login
POST   /api/auth/logout            # Logout
GET    /api/auth/verify            # Verificar email
GET    /swagger-ui.html            # Documentación API
```

### InsightService (8002)

```
GET    /health                     # Health check
GET    /health/db                  # Database check
GET    /health/full                # Full health check
GET    /info                       # Service information
GET    /docs                       # Documentación API
```

### UploadService (8001)

```
POST   /api/v1/transactions/upload # Subir archivo
GET    /api/v1/transactions/batch/{id} # Estado del lote
GET    /health                     # Health check
GET    /docs                       # Documentación API
```

## 📚 Tecnologías Utilizadas

- **Backend Services**:
  - Java 17 + Spring Boot (IdentityService)
  - Python 3.11 + FastAPI (UploadService)
  - Python 3.11 + FastAPI  (InsightService)

- **Base de Datos**: MySQL 8.0

- **Cache**: Redis

- **Mensajería**: RabbitMQ

- **IA**: Ollama (LLM llama3.1:8b)

- **Contenedores**: Docker + Docker Compose
