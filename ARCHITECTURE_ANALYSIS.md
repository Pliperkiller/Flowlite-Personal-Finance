# ANÁLISIS ARQUITECTÓNICO COMPLETO - FLOWLITE PERSONAL FINANCE

## Tabla de Contenidos
1. Estructura General del Proyecto
2. Servicios Backend Implementados
3. Tecnologías Utilizadas
4. Patrones Arquitectónicos
5. Base de Datos y Schema
6. Comunicación entre Servicios
7. Componentes ML y Analytics
8. Frontend/Móvil

---

## 1. ESTRUCTURA GENERAL DEL PROYECTO

### Organización de Directorios

```
Flowlite-Personal-Finance/
├── build_app.sh                    # Script de inicio automático
├── destroy_app.sh                  # Script de detención
├── manage-flowlite.sh              # Gestor global de servicios
├── QUICK_START.md                  # Guía rápida
├── README.md                       # Documentación principal
│
├── InfrastructureService/          # Infraestructura compartida (Docker)
│   ├── docker-compose.yml          # Servicios: MySQL, Redis, RabbitMQ
│   ├── Dockerfile.init             # Inicialización automática DB
│   ├── alembic/                    # Migraciones de BD
│   ├── scripts/
│   │   ├── init_database.py        # Crea tablas
│   │   ├── seed_database.py        # Carga datos de prueba
│   │   └── check_infrastructure.py # Validación de servicios
│   └── requirements.txt
│
├── identifyservice/                # Autenticación (Java/Spring Boot)
│   ├── src/main/java/
│   │   ├── application/            # Servicios de aplicación
│   │   ├── domain/                 # Lógica de negocio
│   │   └── infrastructure/         # Adaptadores
│   ├── build.gradle                # Dependencias Maven
│   ├── start.sh                    # Script de inicio
│   └── START_GUIDE.md
│
├── uploadservice/                  # Procesamiento de archivos (Python/FastAPI)
│   ├── src/
│   │   ├── api/                    # Rutas REST
│   │   ├── application/            # Casos de uso
│   │   ├── domain/                 # Entidades y puertos
│   │   └── infrastructure/         # Implementaciones
│   ├── requirements.txt
│   ├── start.sh
│   └── README.md
│
├── InsightService/                 # Análisis con IA (Python/FastAPI)
│   ├── src/
│   │   ├── application/            # DTOs y casos de uso
│   │   ├── domain/                 # Entidades de negocio
│   │   └── infrastructure/         # BD, LLM, Mensajería
│   ├── main.py                     # Punto de entrada
│   ├── requirements.txt
│   └── README.md
│
├── dataservice/                    # Consulta de datos (Python/FastAPI)
│   ├── src/
│   │   ├── api/routes/             # Endpoints de datos
│   │   ├── application/            # Lógica de aplicación
│   │   └── infrastructure/         # Acceso a datos
│   ├── requirements.txt
│   └── START_GUIDE.md
│
├── database/                       # Gestión centralizada DB
│   ├── docker-compose.database.yml
│   ├── README.md
│   └── DATABASE_SHARING_GUIDE.md
│
├── mailhog/                        # SMTP Mock para desarrollo
│   ├── docker-compose.yml
│   └── README.md
│
└── redis/                          # Cache compartido
    ├── docker-compose.yml
    └── README.md
```

---

## 2. SERVICIOS BACKEND IMPLEMENTADOS

### 2.1 IdentityService (Autenticación)

**Ubicación:** `/identifyservice`

**Puerto:** 8000

**Tecnología:** Java 17 + Spring Boot 3.2.10

**Funcionalidades:**
- Registro y autenticación de usuarios
- Generación y validación de JWT tokens
- Integración OAuth2 (Google, GitHub, Microsoft, Facebook)
- Recuperación de contraseña
- Verificación de email
- Gestión de información de usuario (UserInfo)
- Token revocation con Redis
- Pre-registro de usuarios

**Estructura de Capas:**

```
IdentityService/
├── infrastructure/
│   ├── controllers/
│   │   ├── AuthController              # Endpoints de autenticación
│   │   ├── OAuth2Controller            # OAuth2 callback
│   │   ├── UserInfoController          # Gestión de datos de usuario
│   │   ├── PasswordRecoveryController  # Recuperación de contraseña
│   │   ├── VerificationController      # Verificación de email
│   │   └── PasswordRecoveryCodeController
│   │
│   ├── persistence/
│   │   ├── entities/
│   │   │   ├── UserEntity              # Usuario (credenciales)
│   │   │   └── UserInfoEntity          # Información adicional del usuario
│   │   │
│   │   ├── repositories/
│   │   │   ├── JpaUserRepository       # Acceso a usuarios
│   │   │   └── JpaUserInfoRepository   # Acceso a UserInfo
│   │   │
│   │   └── redis/
│   │       ├── RedisVerificationCodeRepository  # Códigos temporales
│   │       └── PendingUserRedisRepository      # Usuarios pre-registrados
│   │
│   └── config/
│       ├── JacksonConfig              # Serialización JSON
│       ├── EmailConfig                # Configuración de email
│       └── SecurityConfig             # JWT y OAuth2
│
├── application/
│   ├── services/
│   │   ├── RegisterUserService         # Registro de usuarios
│   │   ├── LoginUserService            # Autenticación
│   │   ├── PreregisterUserService      # Pre-registro
│   │   ├── LogoutUserService           # Revocación de token
│   │   ├── ValidateTokenService        # Validación JWT
│   │   ├── TokenRevocationService      # Blacklist con Redis
│   │   ├── PasswordRecoveryService     # Recuperación de password
│   │   ├── VerificationCodeService     # Códigos de verificación
│   │   ├── CompleteInfoUserService     # Completar datos de usuario
│   │   └── RegisterOAuth2UserService   # Registro OAuth2
│   │
│   ├── dto/
│   │   ├── PasswordRecoveryRequest
│   │   ├── UpdateUserInfoRequest
│   │   ├── ResetPasswordRequest
│   │   └── AuthResponse
│   │
│   └── ports/
│       ├── PasswordEncoder             # Interfaz de encriptación
│       ├── TokenProvider               # Generador de JWT
│       └── EmailService                # Envío de emails
│
└── domain/
    ├── repositories/
    │   ├── UserRepository
    │   ├── UserInfoRepository
    │   └── VerificationCodeRepository
    │
    └── models/
        ├── User
        ├── UserInfo
        └── VerificationCode
```

**Dependencias Principales:**
```gradle
- Spring Boot Starter Data JPA
- Spring Boot Starter OAuth2 Client
- MySQL Connector (8.0.33)
- JJWT (JWT: 0.11.5)
- SpringDoc OpenAPI (Swagger)
- Spring Boot Data Redis
- Spring Mail
- Thymeleaf
- Hibernate Validator
- Jackson JSR310
- Spring Boot Actuator
```

**Configuración Base de Datos:**
```properties
spring.jpa.hibernate.ddl-auto=update        # Hibernate gestiona schema
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
```

**Endpoints Principales:**
```
POST   /auth/register                # Registro de usuario
POST   /auth/login                   # Login (retorna JWT)
POST   /auth/logout                  # Logout (revoca token)
GET    /auth/verify                  # Verifica email
POST   /auth/validate                # Valida token (para otros servicios)
POST   /auth/password-recovery       # Solicita recuperación de contraseña
POST   /auth/reset-password          # Reinicia password
PUT    /user/info                    # Actualiza información de usuario
GET    /user/me                      # Obtiene info del usuario actual
GET    /swagger-ui.html              # Documentación interactiva
```

---

### 2.2 UploadService (Procesamiento de Archivos)

**Ubicación:** `/uploadservice`

**Puerto:** 8001

**Tecnología:** Python 3.11 + FastAPI

**Funcionalidades:**
- Carga y procesamiento de archivos Excel
- Clasificación automática de transacciones con ML
- Gestión de lotes de procesamiento asíncrono
- Integración con RabbitMQ para eventos
- Soporte multi-banco (Bancolombia, extensible)
- Validación delegada de JWT via IdentityService

**Arquitectura: Hexagonal (Puertos y Adaptadores)**

```
uploadservice/src/
│
├── domain/                         # Lógica de negocio (independiente de tecnología)
│   ├── entities/
│   │   ├── bank.py                # Banco
│   │   ├── category.py            # Categoría de transacción
│   │   ├── transaction.py         # Transacción individual
│   │   ├── transaction_batch.py   # Lote de procesamiento
│   │   └── file_upload_history.py # Historial de cargas
│   │
│   └── ports/                      # Interfaces (contratos)
│       ├── classifier_port.py      # Clasificador abstracto
│       ├── excel_parser_port.py    # Parser de Excel abstracto
│       ├── message_broker_port.py  # Message broker abstracto
│       ├── repository_port.py      # Repositorio abstracto
│       └── file_upload_history_repository_port.py
│
├── application/                    # Casos de uso
│   ├── dto/
│   │   └── batch_status_dto.py    # DTOs de respuesta
│   │
│   └── use_cases/
│       ├── process_files_use_case.py           # UC: Procesar archivos
│       ├── process_files_use_case_updated.py   # UC: Versión mejorada
│       └── get_batch_status_use_case.py        # UC: Obtener estado
│
├── infrastructure/                 # Implementaciones concretas
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── file_upload_history_model.py
│   │   └── connection.py          # Conexión async a MySQL
│   │
│   ├── repositories/
│   │   ├── mysql_transaction_repository.py
│   │   ├── mysql_transaction_batch_repository.py
│   │   ├── mysql_bank_repository.py
│   │   ├── mysql_category_repository.py
│   │   ├── mysql_user_repository.py
│   │   └── mysql_file_upload_history_repository.py
│   │
│   ├── parsers/                   # Parsers para diferentes bancos
│   │   ├── parser_factory.py      # Factory pattern
│   │   └── bancolombia_parser.py  # Implementación Bancolombia
│   │
│   ├── classifier/                # ML classifier
│   │   ├── ml_classifier.py       # Implementación real (LogisticRegression)
│   │   ├── simple_classifier.py   # Implementación simple
│   │   └── utils.py               # Utilidades de clasificación
│   │
│   ├── messaging/
│   │   └── rabbitmq_producer.py   # Publicador de eventos
│   │
│   ├── clients/
│   │   └── identity_client.py     # Cliente HTTP para IdentityService
│   │
│   └── config/
│       └── settings.py            # Configuración
│
└── api/                            # Presentación (REST)
    ├── routes/
    │   ├── transactions.py        # GET/POST transacciones
    │   ├── health.py              # Health check
    │   └── test.py                # Endpoints de prueba
    │
    └── dependencies/
        ├── auth.py                # Validación de tokens
        ├── services.py            # Inyección de dependencias
        └── repositories.py
```

**Dependencias Principales:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
aiomysql==0.2.0
pandas==2.2.0
openpyxl==3.1.2
scikit-learn==1.7.2           # ML classifier
scipy==1.12.0
aio-pika==9.3.1               # RabbitMQ async
httpx==0.26.0
```

**Endpoints Principales:**
```
GET    /api/v1/health                              # Health check
POST   /api/v1/transactions/upload?bank_code=      # Cargar archivo
GET    /api/v1/transactions/batch/{batch_id}       # Estado del lote
GET    /api/v1/test/user-id                        # Test (obtiene ID del token)
GET    /docs                                        # Swagger UI
```

**Procesamiento ML:**
- Modelo: LogisticRegression + TF-IDF Vectorizer
- Precisión: 99.7%
- Categorías: 12+ categorías (Alimentación_Restaurantes, Servicios_Publicos, etc.)
- Training: scikit-learn 1.7.2 (2025-11-04)

---

### 2.3 InsightService (Análisis con IA)

**Ubicación:** `/InsightService`

**Puerto:** 8002

**Tecnología:** Python 3.11 + FastAPI + LLM (Ollama)

**Funcionalidades:**
- Consumidor de eventos RabbitMQ (transacciones procesadas)
- Generación de insights automáticos usando LLM
- Persistencia de insights en base de datos
- API HTTP para health checks y monitoreo
- Clean Architecture + DDD

**Arquitectura: Clean Architecture + Domain-Driven Design**

```
InsightService/src/
│
├── domain/                         # Lógica de negocio pura
│   └── entities/
│       ├── Insight               # Entidad de dominio
│       └── InsightCategory       # Categoría de insight
│
├── application/                    # Casos de uso
│   ├── dtos.py                    # Data Transfer Objects
│   │   ├── BatchProcessedMessage  # Mensaje de RabbitMQ
│   │   ├── InsightDTO
│   │   └── GenerateInsightsResponse
│   │
│   ├── exceptions.py              # Excepciones de aplicación
│   │
│   ├── services/
│   │   ├── transaction_aggregator.py    # Agrega transacciones
│   │   └── category_mapper.py           # Mapea categorías
│   │
│   ├── interfaces/
│   │   └── llm_service.py         # Interfaz LLM
│   │
│   └── use_cases/
│       └── generate_insights_use_case.py  # Caso de uso principal
│
├── infrastructure/                 # Detalles técnicos
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM
│   │   ├── repositories.py        # Acceso a datos
│   │   └── mappers.py             # Entity <-> DTO conversion
│   │
│   ├── config/
│   │   ├── settings.py            # Configuración
│   │   ├── database.py            # Setup de BD
│   │   └── logging_config.py      # Logging
│   │
│   ├── llm/
│   │   └── ollama_service.py      # Cliente de Ollama
│   │
│   ├── messaging/
│   │   └── rabbitmq_consumer.py   # Consumidor de eventos
│   │
│   └── di/
│       └── container.py           # Inyección de dependencias
│
└── interfaces/                     # Adaptadores
    └── [HTTP REST API - FastAPI]
```

**Dependencias Principales:**
```txt
pika==1.3.2
sqlalchemy==2.0.23
aiomysql==0.2.0
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pydantic==2.5.0
```

**Endpoints HTTP:**
```
GET    /health                      # Health check básico
GET    /health/db                   # Verificar conexión BD
GET    /health/full                 # Health check completo
GET    /info                        # Info del servicio
GET    /docs                        # Documentación Swagger
```

**Integración LLM (Ollama):**
- Modelo: llama3.1:8b
- Host configurable (local o servidor remoto)
- Generación de insights personalizados basados en transacciones

**Flujo de Eventos:**
```
1. UploadService procesa archivo Excel
2. UploadService publica mensaje en RabbitMQ (batch_processed)
3. InsightService consume el mensaje
4. Agrega transacciones del usuario para ese lote
5. Mapea categorías de transacciones
6. Envía al LLM para generar insights
7. Persiste insights en base de datos
```

---

### 2.4 DataService (Consulta de Datos)

**Ubicación:** `/dataservice`

**Puerto:** 8003

**Tecnología:** Python 3.11 + FastAPI

**Funcionalidades:**
- Consulta de transacciones del usuario
- Obtención de dashboards y reportes
- Acceso a insights generados
- Catálogos (bancos, categorías)
- Validación delegada de JWT

**Estructura:**

```
dataservice/src/
│
├── api/
│   ├── dependencies/
│   │   └── auth.py                # Validación de tokens
│   │
│   └── routes/
│       ├── health.py              # Health check
│       ├── transactions.py        # Consulta de transacciones
│       ├── dashboard.py           # Datos para dashboard
│       ├── insights.py            # Acceso a insights
│       └── catalogs.py            # Bancos y categorías
│
├── application/
│   └── dto/
│       ├── transaction_dto.py
│       ├── user_dto.py
│       └── catalog_dto.py
│
└── infrastructure/
    └── database/
        └── [Acceso a datos compartidos]
```

**Endpoints Principales:**
```
GET    /health                      # Health check
GET    /api/v1/transactions         # Listar transacciones (con paginación)
GET    /api/v1/insights             # Listar insights del usuario
GET    /api/v1/dashboard            # Datos del dashboard
GET    /api/v1/catalogs/banks       # Bancos disponibles
GET    /api/v1/catalogs/categories  # Categorías de transacciones
```

---

## 3. TECNOLOGÍAS UTILIZADAS

### 3.1 Stack por Servicio

| Componente | Tecnología | Versión | Servicio(s) |
|---|---|---|---|
| **Lenguajes** | Java | 17 | IdentityService |
| | Python | 3.11+ | UploadService, InsightService, DataService |
| **Frameworks** | Spring Boot | 3.2.10 | IdentityService |
| | FastAPI | 0.109.0 | UploadService |
| | FastAPI | 0.104.1 | InsightService, DataService |
| **Servidores Web** | Gradle/Embedded | - | IdentityService |
| | Uvicorn | 0.27.0 | UploadService |
| | Uvicorn | 0.24.0 | InsightService, DataService |
| **ORM** | Spring Data JPA | Built-in | IdentityService |
| | SQLAlchemy | 2.0.25 | UploadService, InsightService, DataService |
| **Base de Datos** | MySQL | 8.0 | Compartida (InfrastructureService) |
| **Cache** | Redis | 7 | Compartida (IdentityService, otros) |
| **Message Broker** | RabbitMQ | 3.12 | UploadService → InsightService |
| **Migraciones** | Hibernate (auto) | Built-in | IdentityService |
| | Alembic | 1.13.0 | UploadService, InsightService |
| **Procesamiento Excel** | Pandas | 2.2.0 | UploadService |
| | OpenPyXL | 3.1.2 | UploadService |
| **ML/Classification** | scikit-learn | 1.7.2 | UploadService |
| | SciPy | 1.12.0 | UploadService |
| **LLM** | Ollama | N/A | InsightService |
| **Autenticación** | JWT (JJWT) | 0.11.5 | IdentityService |
| | OAuth2 | Built-in | IdentityService (Google, GitHub, MS, FB) |
| **Documentación API** | OpenAPI/Swagger | Built-in | Todos |
| **HTTP Client** | httpx | 0.26.0 | UploadService |
| | requests | 2.31.0 | InsightService |
| **Async** | aiomysql | 0.2.0 | UploadService, InsightService, DataService |
| | aio-pika | 9.3.1 | UploadService |
| | pika | 1.3.2 | InsightService |
| **Validación** | Pydantic | 2.5.0 | FastAPI services |
| | Hibernate Validator | 8.0.1 | IdentityService |
| **Contenedores** | Docker | Latest | InfrastructureService |
| | Docker Compose | Latest | Todo |

### 3.2 Dependencias de Infraestructura

```yaml
InfrastructureService (docker-compose.yml):
  - MySQL 8.0              (puerto 3306)
  - RabbitMQ 3.12         (puerto 5672, Management UI 15672)
  - Redis 7               (puerto 6379)
  - DB-Init (Python)      (servicio de inicialización automática)
```

### 3.3 Herramientas de Desarrollo

- **Gradle**: Build tool (IdentityService)
- **Pip**: Package manager (Python services)
- **Git**: Version control
- **Bash/Shell**: Scripts de automatización

---

## 4. PATRONES ARQUITECTÓNICOS IDENTIFICABLES

### 4.1 IdentityService

**Patrón Principal: Arquitectura en Capas (Layered Architecture)**

```
┌─────────────────────────────────────────┐
│         REST API / Controllers          │  (Presentation Layer)
├─────────────────────────────────────────┤
│      Application Services               │  (Application Layer)
│  (RegisterUserService, LoginUserService, etc)
├─────────────────────────────────────────┤
│         Domain Models                   │  (Domain Layer)
│    (User, UserInfo, VerificationCode)
├─────────────────────────────────────────┤
│    Infrastructure / Persistence         │  (Infrastructure Layer)
│  (Repositories, Redis, Email, JWT)
├─────────────────────────────────────────┤
│     MySQL + Redis + SMTP (MailHog)     │  (Data/External Layer)
└─────────────────────────────────────────┘
```

**Patrones de Diseño Implementados:**

1. **Repository Pattern**: JpaUserRepository, JpaUserInfoRepository para acceso a datos
2. **Strategy Pattern**: Diferentes estrategias de revocación de tokens (Redis)
3. **Factory Pattern**: Creación de diferentes tipos de respuestas
4. **Service Layer**: Separación clara entre controladores y lógica de negocio
5. **Port & Adapter**: PasswordEncoder, TokenProvider, EmailService como puertos
6. **DTO Pattern**: Separación entre entidades JPA y DTOs de respuesta
7. **Dependency Injection**: Spring IoC para inyección de dependencias

**Principios SOLID Aplicados:**
- **Single Responsibility**: Cada servicio tiene una responsabilidad
- **Open/Closed**: Extensible para nuevos tipos de autenticación
- **Liskov Substitution**: Diferentes implementaciones de ports
- **Interface Segregation**: Interfaces pequeñas y cohesivas
- **Dependency Inversion**: Depende de abstracciones, no implementaciones

---

### 4.2 UploadService

**Patrón Principal: Hexagonal Architecture (Puertos y Adaptadores)**

```
                    ┌──────────────────────┐
                    │   External System    │
                    │  (FastAPI REST API)  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  API Adapter Layer   │
                    │  (Routes, Dependencies)
                    └──────────┬───────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │         Application Layer                   │
        │  (Use Cases: Process Files, Get Batch)     │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │          CORE DOMAIN LAYER                  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Entities:                           │  │
        │  │  - Transaction                       │  │
        │  │  - TransactionBatch                  │  │
        │  │  - Bank                              │  │
        │  │  - Category                          │  │
        │  └──────────────────────────────────────┘  │
        │                                             │
        │  ┌──────────────────────────────────────┐  │
        │  │  PORTS (Abstracciones):              │  │
        │  │  - ClassifierPort                    │  │
        │  │  - ExcelParserPort                   │  │
        │  │  - MessageBrokerPort                 │  │
        │  │  - RepositoryPort                    │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │    INFRASTRUCTURE / ADAPTERS LAYER         │
        │  ┌──────────────────────────────────────┐  │
        │  │  Database Adapters:                  │  │
        │  │  - MySQLTransactionRepository        │  │
        │  │  - MySQLBankRepository               │  │
        │  │  - MySQLCategoryRepository           │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Parser Adapters:                    │  │
        │  │  - BancolombiaParser                 │  │
        │  │  - ParserFactory                     │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Classifier Adapters:                │  │
        │  │  - MLClassifier (LogisticRegression) │  │
        │  │  - SimpleClassifier                  │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Messaging Adapter:                  │  │
        │  │  - RabbitMQProducer                  │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  External Service Client:            │  │
        │  │  - IdentityClient (JWT validation)   │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  External Systems:   │
                    │  - MySQL             │
                    │  - RabbitMQ          │
                    │  - IdentityService   │
                    └──────────────────────┘
```

**Patrones de Diseño Implementados:**

1. **Hexagonal Architecture**: Core de negocio aislado
2. **Port & Adapter Pattern**: Todas las dependencias son puertos
3. **Dependency Injection**: Inyección de adaptadores en use cases
4. **Factory Pattern**: ParserFactory para crear parsers según banco
5. **Strategy Pattern**: Diferentes estrategias de clasificación
6. **Repository Pattern**: Acceso transparente a datos
7. **DTO Pattern**: Separación de datos externos vs internos
8. **Async/Await**: Procesamiento no bloqueante

**Ventajas de Hexagonal:**
- Fácil de testear (mock de puertos)
- Independiente de tecnología (cambiar MySQL → PostgreSQL)
- Lógica de negocio aislada y pura
- Extensible (agregar nuevos bancos, clasificadores)

---

### 4.3 InsightService

**Patrón Principal: Clean Architecture + Domain-Driven Design**

```
                    ┌──────────────────────┐
                    │  External Interfaces │
                    │  (HTTP API / RabbitMQ)
                    └──────────┬───────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │       INTERFACE ADAPTERS                    │
        │  ┌──────────────────────────────────────┐  │
        │  │  Controllers (API REST)              │  │
        │  │  - Health endpoints                  │  │
        │  │  - Info endpoint                     │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  RabbitMQ Consumer Adapter           │  │
        │  │  - BatchProcessedMessage parser      │  │
        │  │  - Message handler callback          │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │      APPLICATION LAYER (Use Cases)         │
        │  ┌──────────────────────────────────────┐  │
        │  │  GenerateInsightsUseCase             │  │
        │  │  - Orquesta la generación            │  │
        │  │  - Coordina servicios                │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Application Services:               │  │
        │  │  - TransactionAggregator             │  │
        │  │  - CategoryMapper                    │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  DTOs y Excepciones                  │  │
        │  │  - BatchProcessedMessage             │  │
        │  │  - InsightDTO                        │  │
        │  │  - ApplicationError                  │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │     DOMAIN LAYER (Entity Objects)          │
        │  ┌──────────────────────────────────────┐  │
        │  │  Domain Entities:                    │  │
        │  │  - Insight (Value Objects)           │  │
        │  │  - InsightCategory                   │  │
        │  │                                      │  │
        │  │  Business Logic Encapsulated         │  │
        │  │  in Entities & Value Objects         │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │    INFRASTRUCTURE LAYER (Implementation)    │
        │  ┌──────────────────────────────────────┐  │
        │  │  Database:                           │  │
        │  │  - SQLAlchemy ORM Models             │  │
        │  │  - Repositories                      │  │
        │  │  - Mappers (Entity ↔ DTO)            │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  External Services:                  │  │
        │  │  - OllamaService (LLM Client)        │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Configuration:                      │  │
        │  │  - Settings (env vars)               │  │
        │  │  - Database config                   │  │
        │  │  - Logging setup                     │  │
        │  └──────────────────────────────────────┘  │
        │  ┌──────────────────────────────────────┐  │
        │  │  Dependency Injection:               │  │
        │  │  - Service Container                 │  │
        │  └──────────────────────────────────────┘  │
        └──────────────────────┬──────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  External Systems:   │
                    │  - MySQL Database    │
                    │  - RabbitMQ Broker   │
                    │  - Ollama LLM        │
                    └──────────────────────┘
```

**Patrones de Diseño Implementados:**

1. **Clean Architecture**: Capas independientes y aisladas
2. **Domain-Driven Design**: Core de dominio bien definido
3. **Repository Pattern**: Abstracción de acceso a datos
4. **Service Locator/DI Container**: Inyección de dependencias
5. **Mapper Pattern**: Conversión Entity ↔ DTO
6. **Use Case Pattern**: Orquestación en use cases

---

### 4.4 Patrones de Comunicación entre Servicios

**1. Comunicación Síncrona (HTTP)**
```
UploadService → IdentityService: Validación de JWT
   POST /auth/validate
   Header: Authorization: Bearer <token>
   Response: { user_id: UUID }
```

**2. Comunicación Asíncrona (RabbitMQ)**
```
UploadService → RabbitMQ → InsightService
   Exchange: default
   Queue: batch_processed
   Message: {
       batch_id: UUID,
       status: "completed",
       userid: UUID
   }
```

**3. Acceso a Datos Compartidos**
```
Todos los servicios → MySQL (base de datos compartida)
   - Lectura/Escritura directa
   - Pool de conexiones async
```

---

## 5. BASE DE DATOS Y SCHEMA

### 5.1 Estrategia de Gestión de Schema

**Enfoque: Hibernate Auto-Update + Alembic**

```
IdentityService:
  └─ spring.jpa.hibernate.ddl-auto=update
     (Hibernate crea/actualiza tablas automáticamente)

UploadService, InsightService, DataService:
  └─ Alembic (migraciones versionadas)
     - alembic/versions/001_initial_schema.py
     - Migración inicial crea todas las tablas
```

### 5.2 Estructura de Tablas

**Diagrama de Relaciones:**

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (IdentityService)                │
├─────────────────────────────────────────────────────────────┤
│
│  ┌──────────────┐              ┌──────────────────┐
│  │    User      │         1:1  │   UserInfo       │
│  ├──────────────┤◄─────────────┤──────────────────┤
│  │ id_user (PK) │              │ id_user (PK, FK) │
│  │ username     │              │ first_name       │
│  │ email        │              │ last_name        │
│  │ password     │              │ phone            │
│  │ role         │              │ address          │
│  │ active       │              │ id_number        │
│  │ created_at   │              │ updated_at       │
│  └──────────────┘              └──────────────────┘
│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              TRANSACCIONES (UploadService)                   │
├─────────────────────────────────────────────────────────────┤
│
│  ┌──────────────┐    ┌──────────────────┐
│  │    Bank      │    │ TransactionCategory
│  ├──────────────┤    ├──────────────────┤
│  │ id_bank (PK) │    │ id_category (PK) │
│  │ bank_name    │    │ description      │
│  │ code         │    │ ml_category      │
│  └──────┬───────┘    └──────┬───────────┘
│         │                    │
│         │        ┌───────────┴────────┐
│         │        │                    │
│  ┌──────▼────────▼────────────────────┴────┐
│  │        Transaction                      │
│  ├──────────────────────────────────────────┤
│  │ id_transaction (PK)                      │
│  │ id_user (FK → User)                      │
│  │ id_batch (FK → TransactionBatch)         │
│  │ id_bank (FK)                             │
│  │ id_category (FK)                         │
│  │ transaction_name                         │
│  │ value (Decimal)                          │
│  │ transaction_date                         │
│  │ transaction_type                         │
│  │ created_at                               │
│  └──────┬───────────────────────────────────┘
│         │
│         │ 1:N
│         │
│  ┌──────▼──────────────┐
│  │ TransactionBatch    │
│  ├─────────────────────┤
│  │ id_batch (PK)       │
│  │ id_user (FK)        │
│  │ process_status      │ ← pending, processing, completed, error
│  │ total_records       │
│  │ processed_records   │
│  │ created_at          │
│  │ updated_at          │
│  └─────────────────────┘
│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              INSIGHTS (InsightService)                       │
├─────────────────────────────────────────────────────────────┤
│
│  ┌────────────────────┐
│  │ InsightCategory    │
│  ├────────────────────┤
│  │ id_category (PK)   │
│  │ description        │ ← Ahorro, Presupuesto, Alertas
│  └──────────┬─────────┘
│             │ 1:N
│             │
│         ┌───▼──────────────────────┐
│         │      Insights            │
│         ├──────────────────────────┤
│         │ id_insight (PK)          │
│         │ id_user (FK)             │
│         │ id_category (FK)         │
│         │ title                    │
│         │ text (Generado por IA)   │
│         │ relevance (0-100)        │
│         │ created_at               │
│         └──────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Tipos de Datos

```sql
-- IDs primarios (UUIDs)
id_user        CHAR(36) PRIMARY KEY COMMENT 'UUID as string'
id_insight     CHAR(36) PRIMARY KEY COMMENT 'UUID as string'
id_transaction CHAR(36) PRIMARY KEY COMMENT 'UUID as string'

-- Datos de transacciones
value          DECIMAL(15, 2) COMMENT 'Monto de transacción'
transaction_date DATE COMMENT 'Fecha de la transacción'
process_status ENUM('pending', 'processing', 'completed', 'error')

-- Información de usuario
first_name     VARCHAR(50)
last_name      VARCHAR(50)
email          VARCHAR(100) UNIQUE
phone          VARCHAR(20)
address        VARCHAR(255)
id_number      VARCHAR(50)

-- Timestamps
created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 5.4 Índices Principales

```sql
-- Búsqueda rápida de transacciones por usuario
CREATE INDEX idx_transaction_user ON Transaction(id_user);

-- Búsqueda por batch
CREATE INDEX idx_transaction_batch ON Transaction(id_batch);

-- Búsqueda rápida de insights por usuario
CREATE INDEX idx_insight_user ON Insights(id_user);

-- Búsqueda de batch por usuario
CREATE INDEX idx_batch_user ON TransactionBatch(id_user);
```

---

## 6. CONFIGURACIÓN DE COMUNICACIÓN ENTRE SERVICIOS

### 6.1 Flujo Completo de Datos

```
                                 USUARIO FINAL
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
          ┌──────────────────┐  ┌──────────────────┐  
          │   Navegador      │  │  Mobile App      │  
          │   (Frontend)     │  │  (Futuro)        │
          └────────┬─────────┘  └────────┬─────────┘  
                   │                     │
        ───────────┴─────────────────────┴───────────
                        │
        ┌───────────────▼────────────────┐
        │  IdentityService (Puerto 8000) │
        │  ┌─────────────────────────────┤
        │  │ POST /auth/register         │
        │  │ POST /auth/login            │
        │  │ POST /auth/validate         │──┐
        │  │ POST /auth/logout           │  │
        │  │ PUT  /user/info             │  │
        │  │ GET  /user/me               │  │
        │  └─────────────────────────────┤  │
        │  (Genera JWT Tokens)           │  │
        └───────────┬─────────────────────┘  │
                    │                        │ Token validation
                    │ JWT Token              │ via HTTP
                    │                        │
        ┌───────────▼───────────────────────┴─────────────┐
        │                                                 │
        │  ┌──────────────────────┐  ┌────────────────┐  │
        │  │ UploadService        │  │ DataService    │  │
        │  │ (Puerto 8001)        │  │ (Puerto 8003)  │  │
        │  ├──────────────────────┤  ├────────────────┤  │
        │  │ POST /upload         │  │ GET /transactions
        │  │ GET /batch/{id}      │  │ GET /dashboard │  │
        │  │ GET /health          │  │ GET /insights  │  │
        │  └──────────┬───────────┘  └────────────────┘  │
        │             │                      ▲            │
        │             │ Procesa Excel         │ Lee datos  │
        │             │ Clasifica transacciones
        │             │                      │            │
        │             │      ┌────────────────┘            │
        │             │      │                             │
        │  ┌──────────▼──────▼──────────────────────────┐ │
        │  │  MySQL Database (Puerto 3306)              │ │
        │  │  Base de datos compartida: flowlite_db     │ │
        │  │  ┌──────────────────────────────────────┐  │ │
        │  │  │ Tablas:                              │  │ │
        │  │  │ - User                               │  │ │
        │  │  │ - UserInfo                           │  │ │
        │  │  │ - Transaction                        │  │ │
        │  │  │ - TransactionBatch                   │  │ │
        │  │  │ - Bank                               │  │ │
        │  │  │ - TransactionCategory                │  │ │
        │  │  │ - Insights                           │  │ │
        │  │  │ - InsightCategory                    │  │ │
        │  │  └──────────────────────────────────────┘  │ │
        │  └──────────────────────────────────────────┘ │
        │                    ▲                           │
        └────────────────────┼───────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
        ┌───────────▼────────┐  ┌─────▼──────────────┐
        │ RabbitMQ           │  │ Redis              │
        │ (Puerto 5672)      │  │ (Puerto 6379)      │
        │ Message Broker     │  │ Cache              │
        ├────────────────────┤  ├────────────────────┤
        │ Exchange: default  │  │ Token blacklist    │
        │ Queue: batch_      │  │ Session cache      │
        │   processed        │  │ Rate limiting      │
        └────────┬───────────┘  └────────────────────┘
                 │
                 │ Mensaje: {
                 │   batch_id: UUID,
                 │   status: "completed",
                 │   userid: UUID
                 │ }
                 │
        ┌────────▼──────────────────┐
        │ InsightService             │
        │ (Puerto 8002)              │
        ├────────────────────────────┤
        │ Consumidor RabbitMQ        │
        │ ┌────────────────────────┐ │
        │ │ Aggregates transactions
        │ │ Calls Ollama LLM       │ │
        │ │ Generates insights     │ │
        │ │ Saves to database      │ │
        │ └────────────────────────┘ │
        └────────────────────────────┘
                 │
                 │ LLM API Call
                 │
        ┌────────▼──────────────────┐
        │ Ollama (Puerto 11434)      │
        │ LLM: llama3.1:8b           │
        │ (Local or Remote)          │
        └────────────────────────────┘
```

### 6.2 Variables de Entorno por Servicio

**IdentityService (.env):**
```bash
SERVER_PORT=8000
SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/flowlite_db
SPRING_DATASOURCE_USERNAME=flowlite_user
SPRING_DATASOURCE_PASSWORD=flowlite_password
SPRING_DATA_REDIS_HOST=localhost
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=flowlite_redis_pass_2024
JWT_SECRET=mi_clave_super_secreta_de_32_caracteres_minimo_123456789
MAIL_HOST=localhost
MAIL_PORT=1025
```

**UploadService (.env):**
```bash
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db
IDENTITY_SERVICE_URL=http://localhost:8000
IDENTITY_SERVICE_TIMEOUT=5.0
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE_NAME=batch_processed
HOST=0.0.0.0
PORT=8001
```

**InsightService (.env):**
```bash
DATABASE_URL=mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE=batch_processed
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.7
LLM_TIMEOUT=120
API_HOST=0.0.0.0
API_PORT=8002
LOG_LEVEL=INFO
```

**DataService (.env):**
```bash
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db
IDENTITY_SERVICE_URL=http://localhost:8000
IDENTITY_SERVICE_TIMEOUT=5.0
HOST=0.0.0.0
PORT=8003
DEFAULT_PAGE_SIZE=15
```

---

## 7. COMPONENTES ML Y ANALYTICS

### 7.1 Clasificador de Transacciones (UploadService)

**Ubicación:** `uploadservice/src/infrastructure/classifier/`

**Tecnología:** scikit-learn 1.7.2

**Modelo:** Logistic Regression + TF-IDF Vectorizer

**Precisión:** 99.7%

**Características:**
```python
class MLClassifier(ClassifierPort):
    """Clasificador ML con modelo entrenado"""
    
    - Carga modelo pickle preentrenado
    - Usa TF-IDF para vectorización
    - Logistic Regression para clasificación
    - 12+ categorías disponibles
    
    Categorías:
    - Alimentacion_Restaurantes
    - Transporte
    - Servicios_Publicos
    - Educacion_Colegio
    - Educacion_Universidad
    - Salud
    - Seguros
    - Telecomunicaciones
    - Entretenimiento
    - Viajes_Alojamiento
    - Compras_Generales
    - Otros
```

**Implementación Alternativa:**
```python
class SimpleClassifier(ClassifierPort):
    """Clasificador simple que retorna 'Otros'"""
    - Útil para testing y desarrollo
    - Sin dependencias de modelos
```

**Flujo de Clasificación:**
```
1. Usuario sube archivo Excel
2. UploadService parsea transacciones
3. Para cada transacción:
   - Extrae descripción
   - Vectoriza con TF-IDF
   - Pasa a LogisticRegression
   - Obtiene predicción de categoría
4. Guarda categoría en base de datos
5. Publica evento a RabbitMQ
```

### 7.2 Generador de Insights (InsightService)

**Ubicación:** `InsightService/src/infrastructure/llm/`

**Tecnología:** Ollama + llama3.1:8b (LLM)

**Características:**
```python
class OllamaService:
    """Cliente para generar insights con LLM remoto"""
    
    - Se conecta a servidor Ollama (local o remoto)
    - Modelo: llama3.1:8b
    - Temperatura configurable (0.7 por defecto)
    - Timeout configurable (120s)
    - Generación de insights personalizados
```

**Prompt Engineering:**
```
El servicio recibe:
- Transacciones del usuario (últimas 30 días)
- Categorías mapeadas
- Contexto de gastos

El LLM genera insights sobre:
- Patrones de gasto
- Recomendaciones de ahorro
- Alertas de anomalías
- Presupuesto sugerido
```

**Ejemplo de Insight Generado:**
```
{
    "id_insight": "550e8400-e29b-41d4-a716-446655440000",
    "id_user": "123e4567-e89b-12d3-a456-426614174000",
    "id_category": "ahorro-001",
    "title": "Oportunidad de ahorro detectada",
    "text": "Nuestro análisis de IA detectó que gastas 450USD en restaurantes mensualmente...",
    "relevance": 85,
    "created_at": "2025-11-25T10:30:00"
}
```

### 7.3 Analytics y Reportes (DataService)

**Ubicación:** `dataservice/src/api/routes/`

**Funcionalidades:**
- Dashboard de resumen de gastos
- Análisis por categoría
- Evolución histórica
- Comparativas mes a mes
- KPIs de ahorro

**Endpoints:**
```
GET /api/v1/dashboard
    - Total gastado (mes, año)
    - Gasto por categoría
    - Top 5 gastos
    - Tendencias

GET /api/v1/transactions?page=1&per_page=15
    - Listado paginado
    - Filtros por categoría, fecha
    - Búsqueda por descripción

GET /api/v1/insights
    - Insights generados
    - Ordenados por relevancia
    - Filtrados por categoría
```

---

## 8. FRONTEND/MÓVIL

### 8.1 Estado Actual

**No hay frontend/aplicación móvil implementada aún.**

El proyecto está orientado a proporcionar una API REST robusta que pueda ser consumida por:
- Aplicación web (React, Vue, Angular)
- Aplicación móvil (React Native, Flutter, Kotlin)
- Cliente de escritorio
- Integraciones de terceros

### 8.2 Requisitos para Frontend (Basado en API)

**Autenticación:**
```javascript
// 1. Registrar usuario
POST /auth/register
{
    email: "user@example.com",
    username: "username",
    password: "Password123!"
}
→ Response: { access_token: "jwt-token", token_type: "bearer" }

// 2. Login
POST /auth/login
{
    email: "user@example.com",
    password: "Password123!"
}
→ Response: { access_token: "jwt-token" }

// 3. Obtener perfil del usuario
GET /user/me
Headers: Authorization: Bearer jwt-token
→ Response: { id, username, email, firstName, lastName, ... }

// 4. Actualizar perfil
PUT /user/info
Headers: Authorization: Bearer jwt-token
Body: { firstName, lastName, phone, address, idNumber }
```

**Carga de Archivos:**
```javascript
// 1. Subir archivo de transacciones
POST /api/v1/transactions/upload?bank_code=BANCOLOMBIA
Headers: Authorization: Bearer jwt-token
Body: FormData { files: [File] }
→ Response: { batch_id: "uuid", message: "Processing started" }

// 2. Verificar estado del procesamiento
GET /api/v1/transactions/batch/batch-id
Headers: Authorization: Bearer jwt-token
→ Response: { 
    batch_id: "uuid",
    status: "completed",
    total_records: 190,
    processed_records: 190,
    processed_percentage: 100
}
```

**Consulta de Datos:**
```javascript
// 1. Listar transacciones
GET /api/v1/transactions?page=1&per_page=15
Headers: Authorization: Bearer jwt-token
→ Response: {
    items: [
        {
            id: "uuid",
            description: "MERCADO CARREFOUR",
            amount: -45.50,
            category: "Alimentacion_Restaurantes",
            date: "2025-11-20",
            bank: "BANCOLOMBIA"
        }
    ],
    total: 190,
    page: 1,
    per_page: 15
}

// 2. Dashboard
GET /api/v1/dashboard
Headers: Authorization: Bearer jwt-token
→ Response: {
    total_spent: { month: 1250.50, year: 15000.00 },
    by_category: [
        { category: "Alimentacion_Restaurantes", amount: 450.00, percentage: 36 },
        { category: "Transporte", amount: 250.00, percentage: 20 },
        ...
    ],
    top_transactions: [...],
    insights: [...]
}

// 3. Insights
GET /api/v1/insights
Headers: Authorization: Bearer jwt-token
→ Response: {
    items: [
        {
            id: "uuid",
            title: "Oportunidad de ahorro",
            text: "Nuestro análisis...",
            category: "ahorro",
            relevance: 85,
            created_at: "2025-11-25T10:30:00"
        }
    ]
}
```

### 8.3 Documentación API Interactiva

Disponible en cada servicio:
```
IdentityService:     http://localhost:8000/swagger-ui.html
UploadService:       http://localhost:8001/docs
InsightService:      http://localhost:8002/docs
DataService:         http://localhost:8003/docs
```

---

## RESUMEN TÉCNICO

### Stack Tecnológico
- **Backend:** Java (Spring Boot), Python (FastAPI)
- **Base de Datos:** MySQL 8.0 (compartida)
- **Cache:** Redis 7
- **Message Broker:** RabbitMQ 3.12
- **LLM:** Ollama (llama3.1:8b)
- **ML/ML:** scikit-learn (LogisticRegression)
- **Contenedores:** Docker + Docker Compose
- **Migraciones:** Hibernate (Java), Alembic (Python)

### Patrones Arquitectónicos
- **IdentityService:** Layered Architecture
- **UploadService:** Hexagonal Architecture
- **InsightService:** Clean Architecture + DDD
- **DataService:** Layered Architecture

### Principios SOLID
✅ Single Responsibility
✅ Open/Closed
✅ Liskov Substitution
✅ Interface Segregation
✅ Dependency Inversion

### Características de Calidad
✅ Separación clara de capas
✅ Inyección de dependencias
✅ Patrón Repository para acceso a datos
✅ DTOs para transferencia de datos
✅ Validación en múltiples niveles
✅ Manejo de errores robusto
✅ Documentación API automática
✅ Health checks integrados
✅ Logging centralizado
✅ Configuración por variables de entorno

### Escalabilidad
- Comunicación asíncrona vía RabbitMQ
- Procesamiento de lotes (batch processing)
- Cache con Redis
- Pool de conexiones a BD
- Servicios independientes y desplegables

### Seguridad
- JWT tokens con expiración
- OAuth2 integrado (Google, GitHub, MS, FB)
- Validación delegada de tokens
- Blacklist de tokens revocados en Redis
- Hash de contraseñas con BCrypt
- HTTPS ready (ngrok compatible)
- MailHog para testing de emails

---

**Generado:** 25 de Noviembre, 2025
**Proyecto:** Flowlite Personal Finance Platform
**Versión:** 1.0.0
