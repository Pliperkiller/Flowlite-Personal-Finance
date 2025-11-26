# Flowlite Personal Finance - Configuración Docker

**Autores:** Carlos Felipe Caro Arroyave & Joiver Andrés Gómez Coronado

Este directorio contiene toda la configuración Docker necesaria para ejecutar la plataforma Flowlite Personal Finance en contenedores.

## Estructura del Directorio

```
Docker/
├── docker-compose.yml          # Orquestación de todos los servicios
├── README.md                   # Este archivo
├── IdentifyService/            # Servicio de autenticación
│   ├── Dockerfile
│   └── .env.example
├── UploadService/              # Servicio de carga de transacciones
│   ├── Dockerfile
│   └── .env.example
├── InsightService/             # Servicio de insights con IA
│   ├── Dockerfile
│   └── .env.example
└── DataService/                # Servicio de consultas de datos
    ├── Dockerfile
    └── .env.example
```

---

## Servicios

### 1. IdentifyService

**Descripción:** Microservicio de autenticación y autorización usando JWT y OAuth2.

**Tecnología:** Java 17 + Spring Boot

**Puerto:** 8080

**Características:**
- Registro de usuarios (directo, pre-registro con verificación, OAuth2)
- Login con JWT
- Recuperación de contraseña
- Gestión de información de usuario (KYC)
- Integración con Google OAuth2
- Revocación de tokens con Redis

**Dependencias:**
- MySQL (base de datos)
- Redis (cache y blacklist de tokens)
- MailHog (envío de emails en desarrollo)

**Archivos:**
- `Dockerfile`: Construcción multi-stage (builder + runtime) con Java 17
- `.env.example`: Variables de entorno (JWT secret, database, Redis, OAuth2)

**Health Check:** `http://localhost:8080/actuator/health`

**Swagger UI:** `http://localhost:8080/swagger-ui/index.html`

---

### 2. UploadService

**Descripción:** Microservicio para carga de archivos Excel bancarios, parsing y clasificación automática de transacciones.

**Tecnología:** Python 3.11 + FastAPI

**Puerto:** 8001

**Características:**
- Parsing de archivos Excel bancarios (Bancolombia, extensible a otros bancos)
- Clasificación automática con Machine Learning (sklearn)
- Detección de duplicados mediante hash SHA256
- Procesamiento por lotes (batches)
- Publicación de eventos a RabbitMQ

**Dependencias:**
- MySQL (base de datos)
- RabbitMQ (mensajería asíncrona)
- IdentifyService (validación de tokens)

**Archivos:**
- `Dockerfile`: Python slim con dependencias ML (pandas, sklearn)
- `.env.example`: Variables de entorno (database, RabbitMQ, ML models)

**Health Check:** `http://localhost:8001/health`

**API Docs:** `http://localhost:8001/docs`

---

### 3. InsightService

**Descripción:** Microservicio que genera recomendaciones financieras personalizadas usando LLM (Ollama).

**Tecnología:** Python 3.11 + FastAPI + Ollama

**Puerto:** 8002

**Características:**
- Análisis temporal de transacciones
- Generación de insights con LLM (Llama 3.1)
- Consumo de eventos RabbitMQ (batch_processed)
- Categorización de recomendaciones (savings, spending, investment, debt, budget)
- API REST para consultar insights

**Dependencias:**
- MySQL (base de datos)
- RabbitMQ (consumo de eventos)
- Ollama (servicio LLM)

**Archivos:**
- `Dockerfile`: Python slim con cliente Ollama
- `.env.example`: Variables de entorno (database, RabbitMQ, Ollama config)

**Health Check:** `http://localhost:8002/health`

**API Docs:** `http://localhost:8002/docs`

---

### 4. DataService

**Descripción:** Microservicio de consultas y vistas de datos financieros (Dashboard, Transacciones, Insights, Catálogos).

**Tecnología:** Python 3.11 + FastAPI

**Puerto:** 8003

**Características:**
- Dashboard consolidado (balance, últimas transacciones, top insights)
- Consulta paginada de transacciones
- Consulta de insights por usuario
- Catálogos (bancos, categorías)
- Integración con IdentifyService para autenticación

**Dependencias:**
- MySQL (base de datos)
- IdentifyService (validación de tokens)

**Archivos:**
- `Dockerfile`: Python slim con FastAPI
- `.env.example`: Variables de entorno (database, IdentifyService URL)

**Health Check:** `http://localhost:8003/health`

**API Docs:** `http://localhost:8003/docs`

---

## Infraestructura

### MySQL
- **Imagen:** mysql:8.0
- **Puerto:** 3306
- **Database:** flowlite_db
- **Usuario:** flowlite_user
- **Password:** flowlite_password
- **Volumen:** mysql-data (persistencia)

### Redis
- **Imagen:** redis:7-alpine
- **Puerto:** 6379
- **Password:** flowlite_redis_pass_2024
- **Uso:** Cache y blacklist de tokens JWT
- **Volumen:** redis-data (persistencia)

### RabbitMQ
- **Imagen:** rabbitmq:3.12-management-alpine
- **Puerto AMQP:** 5672
- **Puerto Management UI:** 15672
- **Usuario:** flowlite
- **Password:** flowlite_rabbitmq_pass
- **Uso:** Event-driven communication (batch_processed events)
- **Management UI:** `http://localhost:15672`
- **Volumen:** rabbitmq-data (persistencia)

### Ollama
- **Imagen:** ollama/ollama:latest
- **Puerto:** 11434
- **Modelo:** llama3.1:8b
- **Uso:** Generación de insights financieros con LLM
- **Volumen:** ollama-data (persistencia de modelos)

**Nota:** Después de iniciar Ollama, ejecutar:
```bash
docker exec -it flowlite-ollama ollama pull llama3.1:8b
```

### MailHog
- **Imagen:** mailhog/mailhog:latest
- **Puerto SMTP:** 1025
- **Puerto Web UI:** 8025
- **Uso:** Captura de emails en desarrollo (no envía realmente)
- **Web UI:** `http://localhost:8025`

---

## Inicio Rápido

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- 8 GB RAM mínimo (16 GB recomendado para Ollama)

### Pasos

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd Flowlite-Personal-Finance/Docker
```

2. **Configurar variables de entorno:**

Para cada servicio, copiar `.env.example` a `.env` y ajustar si es necesario:

```bash
# IdentifyService
cp IdentifyService/.env.example IdentifyService/.env

# UploadService
cp UploadService/.env.example UploadService/.env

# InsightService
cp InsightService/.env.example InsightService/.env

# DataService
cp DataService/.env.example DataService/.env
```

3. **Iniciar toda la plataforma:**

```bash
docker-compose up -d
```

Este comando:
- Descarga todas las imágenes necesarias
- Construye los Dockerfiles de los microservicios
- Inicia la infraestructura (MySQL, Redis, RabbitMQ, Ollama, MailHog)
- Inicia los 4 microservicios

4. **Descargar el modelo LLM (primera vez):**

```bash
docker exec -it flowlite-ollama ollama pull llama3.1:8b
```

Esto puede tardar varios minutos dependiendo de la conexión.

5. **Verificar que todos los servicios estén saludables:**

```bash
docker-compose ps
```

Todos los servicios deben mostrar estado `healthy`.

---

## Comandos Útiles

### Ver logs de un servicio específico:
```bash
docker-compose logs -f identifyservice
docker-compose logs -f uploadservice
docker-compose logs -f insightservice
docker-compose logs -f dataservice
```

### Ver logs de toda la infraestructura:
```bash
docker-compose logs -f mysql redis rabbitmq ollama
```

### Detener todos los servicios:
```bash
docker-compose down
```

### Detener y eliminar volúmenes (reset completo):
```bash
docker-compose down -v
```

### Reiniciar un servicio específico:
```bash
docker-compose restart uploadservice
```

### Reconstruir un servicio (después de cambios de código):
```bash
docker-compose up -d --build uploadservice
```

### Acceder a un contenedor (shell):
```bash
docker exec -it flowlite-identifyservice bash
docker exec -it flowlite-uploadservice bash
```

### Ver estado de salud de servicios:
```bash
curl http://localhost:8080/actuator/health  # IdentifyService
curl http://localhost:8001/health           # UploadService
curl http://localhost:8002/health           # InsightService
curl http://localhost:8003/health           # DataService
```

---

## Arquitectura de Red

Todos los servicios se ejecutan en la red `flowlite-network` (bridge), permitiendo comunicación interna por nombre de servicio:

```
identifyservice   → mysql, redis, mailhog
uploadservice     → mysql, rabbitmq, identifyservice
insightservice    → mysql, rabbitmq, ollama
dataservice       → mysql, identifyservice
```

### Mapa de Puertos

| Servicio | Puerto Host | Puerto Container | Propósito |
|----------|-------------|------------------|-----------|
| IdentifyService | 8080 | 8080 | API REST |
| UploadService | 8001 | 8001 | API REST |
| InsightService | 8002 | 8002 | API REST |
| DataService | 8003 | 8003 | API REST |
| MySQL | 3306 | 3306 | Database |
| Redis | 6379 | 6379 | Cache |
| RabbitMQ (AMQP) | 5672 | 5672 | Message Broker |
| RabbitMQ (UI) | 15672 | 15672 | Management UI |
| Ollama | 11434 | 11434 | LLM API |
| MailHog (SMTP) | 1025 | 1025 | Email Capture |
| MailHog (UI) | 8025 | 8025 | Email Web UI |

---

### Bounded Contexts en Contenedores

| Bounded Context | Container | Responsabilidad |
|----------------|-----------|-----------------|
| Identity & Access Management | identifyservice | Autenticación, autorización |
| Transaction Upload & Classification | uploadservice | Carga, parsing, clasificación |
| Financial Insights Generation | insightservice | Análisis, recomendaciones IA |
| Financial Data Management | dataservice | Consultas, vistas consolidadas |

