# Vistas Arquitectónicas - Flowlite Personal Finance

## Índice

1. [Vista de Contexto](#1-vista-de-contexto)
2. [Vista de Contenedores (C4)](#2-vista-de-contenedores-c4)
3. [Vista de Componentes](#3-vista-de-componentes)
4. [Vista de Módulos](#4-vista-de-módulos)
5. [Vista de Componentes y Conectores](#5-vista-de-componentes-y-conectores)
6. [Vista de Deployment](#6-vista-de-deployment)
7. [Vista de Datos](#7-vista-de-datos)
8. [Vista de Seguridad](#8-vista-de-seguridad)

---

## 1. Vista de Contexto

**Propósito:** Muestra el sistema como una caja negra y su relación con usuarios externos y sistemas externos.

```mermaid
graph TB
    subgraph "Usuarios"
        User[Usuario Móvil<br/>Gestiona finanzas personales]
        Admin[‍Administrador<br/>Gestiona modelos ML]
    end

    subgraph "Sistema Flowlite"
        System[Flowlite<br/>Personal Finance<br/>System]
    end

    subgraph "Sistemas Externos"
        Gmail[Gmail SMTP<br/>Servicio de Email]
        Google[Google OAuth<br/>Autenticación]
        GitHub[GitHub OAuth<br/>Autenticación]
        Microsoft[Microsoft OAuth<br/>Autenticación]
        Ollama[Ollama LLM<br/>Generación de Insights]
    end

    subgraph "Fuentes de Datos"
        Bank[Archivos Excel<br/>Transacciones Bancarias]
    end

    User -->|Registra, autentica, carga datos| System
    User -->|Consulta dashboard e insights| System
    Admin -->|Gestiona modelos ML| System

    System -->|Envía emails de verificación| Gmail
    System -->|Autentica usuarios| Google
    System -->|Autentica usuarios| GitHub
    System -->|Autentica usuarios| Microsoft
    System -->|Genera insights con IA| Ollama

    User -->|Exporta desde banco| Bank
    Bank -->|Carga en sistema| System

    style System fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    style User fill:#2196F3,stroke:#1565C0,color:#fff
    style Admin fill:#FF9800,stroke:#E65100,color:#fff
```

**Descripción:**
- **Usuarios Móviles:** Personas que gestionan sus finanzas personales
- **Administradores:** Personal técnico que gestiona modelos ML y configuraciones
- **Sistema Flowlite:** Sistema completo de finanzas personales
- **Sistemas Externos:** Servicios de terceros para autenticación, email y LLM

---

## 2. Vista de Contenedores (C4)

**Propósito:** Descompone el sistema en contenedores (aplicaciones, servicios, bases de datos).

```mermaid
graph TB
    subgraph "Dispositivo Móvil"
        Mobile["App Móvil Flutter<br/>- UI/UX<br/>- Gestión de estado (BLoC)<br/>- Cache local (Hive)<br/>- JWT storage"]
    end

    subgraph "Backend Services"
        IS["IdentityService<br/>Java Spring Boot 3.2.10<br/>- Autenticación JWT<br/>- OAuth2<br/>- Gestión usuarios<br/>Puerto: 8000"]

        US["UploadService<br/>Python FastAPI<br/>- Carga archivos Excel<br/>- Parseo transacciones<br/>- Clasificación ML<br/>Puerto: 8001"]

        InsS["InsightService<br/>Python FastAPI<br/>- Generación insights<br/>- Integración LLM<br/>- Análisis con IA<br/>Puerto: 8002"]

        DS["DataService<br/>Python FastAPI<br/>- Consultas de datos<br/>- Dashboard<br/>- Reportes<br/>Puerto: 8003"]
    end

    subgraph "Infraestructura"
        DB[("MySQL 8.0<br/>Base de Datos<br/>- Usuarios<br/>- Transacciones<br/>- Insights<br/>Puerto: 3306")]

        Redis[("Redis 7<br/>Cache + Tokens<br/>- Token revocation<br/>- Cache de sesión<br/>Puerto: 6379")]

        MQ["RabbitMQ 3.12<br/>Message Broker<br/>- Cola batch.processed<br/>Puerto: 5672"]

        Ollama["Ollama LLM<br/>llama3.1:8b<br/>- Generación texto<br/>Puerto: 11434"]
    end

    subgraph "Observabilidad"
        Prometheus["Prometheus<br/>Métricas<br/>Puerto: 9090"]
        Grafana["Grafana<br/>Dashboards<br/>Puerto: 3000"]
        Jaeger["Jaeger<br/>Distributed Tracing<br/>Puerto: 16686"]
    end

    Mobile -->|"1. JWT Auth<br/>POST /auth/login"| IS
    Mobile -->|"2. Upload Excel<br/>POST /transactions/upload"| US
    Mobile -->|"3. Query Data<br/>GET /dashboard"| DS
    Mobile -->|"4. Get Insights<br/>GET /insights"| DS

    US -->|"Validate JWT<br/>GET /auth/validate"| IS
    DS -->|"Validate JWT<br/>GET /auth/validate"| IS

    US -->|"Publish:<br/>batch.processed"| MQ
    MQ -->|"Consume:<br/>batch.processed"| InsS

    InsS -->|"Generate text<br/>POST /api/generate"| Ollama

    IS -->|"CRUD<br/>Users, UserInfo"| DB
    US -->|"CRUD<br/>Transactions, Batches"| DB
    InsS -->|"CRUD<br/>Insights"| DB
    DS -->|"Query<br/>Read-only"| DB

    IS -->|"Token revocation<br/>Session cache"| Redis

    IS -->|"Expose /actuator/prometheus"| Prometheus
    US -->|"Expose /metrics"| Prometheus
    InsS -->|"Expose /metrics"| Prometheus
    DS -->|"Expose /metrics"| Prometheus

    Grafana -->|"Query metrics"| Prometheus

    US -->|"Send traces"| Jaeger
    InsS -->|"Send traces"| Jaeger

    style IS fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style US fill:#4ECDC4,stroke:#0A9396,color:#fff
    style InsS fill:#FFE66D,stroke:#F4A261,color:#000
    style DS fill:#95E1D3,stroke:#38A3A5,color:#000
    style DB fill:#5C7CFA,stroke:#364FC7,color:#fff
    style Redis fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style MQ fill:#F59E0B,stroke:#D97706,color:#fff
```

**Descripción de Tecnologías:**

| Contenedor | Tecnología | Justificación |
|------------|------------|---------------|
| **IdentityService** | Java 17 + Spring Boot 3.2.10 | Ecosistema maduro para autenticación, Spring Security robusto |
| **UploadService** | Python 3.11 + FastAPI | Excelente para ML (scikit-learn), async performance |
| **InsightService** | Python 3.11 + FastAPI | Integración nativa con Ollama y librerías ML |
| **DataService** | Python 3.11 + FastAPI | Query optimization, async DB access |
| **MySQL** | 8.0 | ACID, transacciones, relaciones complejas |
| **Redis** | 7 | High performance cache, token revocation |
| **RabbitMQ** | 3.12 | Message durability, routing flexible |
| **Ollama** | llama3.1:8b | LLM local, privacidad, sin costos API |

---

## 3. Vista de Componentes

**Propósito:** Muestra los componentes internos de cada contenedor y sus interacciones.

### 3.1 IdentityService - Componentes Internos

```mermaid
graph TB
    subgraph "IdentityService - Layered Architecture"
        subgraph "Controllers Layer"
            AC[AuthController<br/>Login/Register/Logout]
            PRC[PasswordRecoveryController<br/>Recuperación contraseña]
            UIC[UserInfoController<br/>Gestión perfil]
            VC[VerificationController<br/>Códigos verificación]
            OC[OAuth2Controller<br/>Login con terceros]
        end

        subgraph "Application Services Layer"
            RUS[RegisterUserService]
            LUS[LoginUserService]
            LOUS[LogoutUserService]
            PRS[PasswordRecoveryService]
            CUIS[CompleteInfoUserService]
            VTS[ValidateTokenService]
            TRS[TokenRevocationService]
        end

        subgraph "Domain Layer"
            User[User Entity]
            UserInfo[UserInfo Entity]
            Email[Email VO]
            Password[Password VO]
            UR[UserRepository Port]
            UIR[UserInfoRepository Port]
            TP[TokenProvider Port]
            PE[PasswordEncoder Port]
            ES[EmailService Port]
        end

        subgraph "Infrastructure Layer"
            JWT[JwtTokenProvider<br/>JJWT Implementation]
            BCrypt[BCryptPasswordEncoder<br/>Password Hashing]
            MailHog[EmailServiceMailHog<br/>SMTP Client]
            UserRepo[UserRepositoryJpaAdapter<br/>JPA Implementation]
            UIRepo[UserInfoRepositoryJpaAdapter<br/>JPA Implementation]
            RedisRepo[RedisTokenRepository<br/>Token Revocation]
        end

        AC --> RUS
        AC --> LUS
        AC --> LOUS
        PRC --> PRS
        UIC --> CUIS
        VC --> VTS

        RUS --> User
        RUS --> Email
        RUS --> Password
        RUS --> UR
        RUS --> PE
        RUS --> ES

        LUS --> User
        LUS --> UR
        LUS --> TP
        LUS --> PE

        UR -.implements.- UserRepo
        UIR -.implements.- UIRepo
        TP -.implements.- JWT
        PE -.implements.- BCrypt
        ES -.implements.- MailHog

        UserRepo --> DB[(MySQL)]
        UIRepo --> DB
        RedisRepo --> Redis[(Redis)]
    end

    style AC fill:#FFE66D,color:#000
    style RUS fill:#4ECDC4,color:#fff
    style User fill:#95E1D3,color:#000
    style JWT fill:#FF6B6B,color:#fff
```

---

### 3.2 UploadService - Componentes Internos (Hexagonal)

```mermaid
graph TB
    subgraph "UploadService - Hexagonal Architecture"
        subgraph "API Adapter (Infrastructure)"
            TR[TransactionRoutes<br/>FastAPI Endpoints]
        end

        subgraph "Application Layer"
            PBFU[ProcessBankFileUseCase<br/>Orquestación]
            GTBU[GetTransactionBatchUseCase<br/>Consulta estado]
        end

        subgraph "Domain Core"
            Transaction[Transaction Entity]
            Batch[TransactionBatch Entity]

            BPPort[BankParserPort<br/>Interface]
            CPort[ClassifierPort<br/>Interface]
            RPort[RepositoryPort<br/>Interface]
            MQPort[MessageQueuePort<br/>Interface]
        end

        subgraph "Infrastructure Adapters"
            BancParser[BancolombiaParser]
            DaviParser[DaviviendaParser]
            Factory[BankParserFactory<br/>Strategy]

            SKLearn[SklearnClassifier<br/>ML Model]
            Simple[SimpleClassifier<br/>Rule-based]

            MySQLRepo[MySQLTransactionRepository]
            RabbitPub[RabbitMQPublisher]
        end

        TR --> PBFU
        TR --> GTBU

        PBFU --> Transaction
        PBFU --> Batch
        PBFU --> BPPort
        PBFU --> CPort
        PBFU --> RPort
        PBFU --> MQPort

        BPPort -.implements.- Factory
        Factory --> BancParser
        Factory --> DaviParser

        CPort -.implements.- SKLearn
        CPort -.implements.- Simple

        RPort -.implements.- MySQLRepo
        MQPort -.implements.- RabbitPub

        MySQLRepo --> DB[(MySQL)]
        RabbitPub --> MQ[RabbitMQ]
        SKLearn --> Model[ML Model<br/>classifier_v1.joblib]
    end

    style TR fill:#FFE66D,color:#000
    style PBFU fill:#4ECDC4,color:#fff
    style Transaction fill:#95E1D3,color:#000
    style SKLearn fill:#FF6B6B,color:#fff
```

**Key Ports (Abstracciones):**
- `BankParserPort`: Abstracción para parsear diferentes bancos
- `ClassifierPort`: Abstracción para modelos ML
- `RepositoryPort`: Abstracción para persistencia
- `MessageQueuePort`: Abstracción para mensajería

---

### 3.3 InsightService - Componentes Internos (Clean Architecture)

```mermaid
graph TB
    subgraph "InsightService - Clean Architecture"
        subgraph "Interface Adapters"
            RMQConsumer[RabbitMQ Consumer<br/>Event Listener]
            HTTPAPI[HTTP API<br/>Health/Monitoring]
        end

        subgraph "Application Layer"
            GIUC[GenerateInsightsUseCase<br/>Main Flow]
            GetIUC[GetInsightsUseCase<br/>Query Insights]
        end

        subgraph "Domain Layer"
            Insight[Insight Entity]
            IGS[InsightGenerationService<br/>Business Logic]

            LLMP[LLMProviderPort<br/>Interface]
            IRP[InsightRepositoryPort<br/>Interface]
            TRP[TransactionRepositoryPort<br/>Interface]
        end

        subgraph "Infrastructure Layer"
            OllamaP[OllamaProvider<br/>LLM Client]
            OpenAIP[OpenAIProvider<br/>Alternative]

            InsightRepo[MySQLInsightRepository]
            TransRepo[MySQLTransactionRepository]
        end

        RMQConsumer -->|"batch.processed event"| GIUC
        HTTPAPI --> GetIUC

        GIUC --> Insight
        GIUC --> IGS
        GIUC --> LLMP
        GIUC --> IRP
        GIUC --> TRP

        IGS --> LLMP

        LLMP -.implements.- OllamaP
        LLMP -.implements.- OpenAIP
        IRP -.implements.- InsightRepo
        TRP -.implements.- TransRepo

        OllamaP -->|"POST /api/generate"| Ollama[Ollama LLM]
        InsightRepo --> DB[(MySQL)]
        TransRepo --> DB
    end

    style RMQConsumer fill:#FFE66D,color:#000
    style GIUC fill:#4ECDC4,color:#fff
    style Insight fill:#95E1D3,color:#000
    style OllamaP fill:#FF6B6B,color:#fff
```

---

### 3.4 DataService - Componentes Internos (CQRS Read)

```mermaid
graph TB
    subgraph "DataService - CQRS Read Side"
        subgraph "Controllers"
            TC[TransactionController<br/>Query Transactions]
            DC[DashboardController<br/>Aggregated Data]
            IC[InsightController<br/>Query Insights]
            CC[CatalogController<br/>Banks, Categories]
        end

        subgraph "Services"
            TQS[TransactionQueryService]
            DashS[DashboardService<br/>Aggregations]
            CatS[CatalogService]
        end

        subgraph "Repositories (Read-Only)"
            TRepo[TransactionRepository]
            IRepo[InsightRepository]
            BRepo[BankRepository]
            CatRepo[CategoryRepository]
        end

        TC --> TQS
        DC --> DashS
        IC --> TQS
        CC --> CatS

        TQS --> TRepo
        DashS --> TRepo
        DashS --> IRepo
        CatS --> BRepo
        CatS --> CatRepo

        TRepo --> DB[(MySQL<br/>Read-Only)]
        IRepo --> DB
        BRepo --> DB
        CatRepo --> DB
    end

    style TC fill:#FFE66D,color:#000
    style TQS fill:#4ECDC4,color:#fff
    style TRepo fill:#95E1D3,color:#000
```

---

## 4. Vista de Módulos

**Propósito:** Muestra la organización estática del código en módulos, paquetes y dependencias.

### 4.1 IdentityService - Estructura de Módulos

```
com.flowlite.identifyservice/
│
├── application/ (Application Layer)
│ ├── dto/ (Data Transfer Objects)
│ │ ├── ResetPasswordRequest
│ │ ├── PasswordRecoveryRequest
│ │ └── UpdateUserInfoRequest
│ │
│ ├── services/ (Application Services - Use Cases)
│ │ ├── RegisterUserService
│ │ ├── LoginUserService
│ │ ├── LogoutUserService
│ │ ├── PasswordRecoveryService
│ │ ├── CompleteInfoUserService
│ │ ├── ValidateTokenService
│ │ └── TokenRevocationService
│ │
│ └── ports/ (Interfaces para Infrastructure)
│ ├── TokenProvider
│ ├── PasswordEncoder
│ └── EmailService
│
├── domain/ (Domain Layer - Core Business)
│ ├── entities/ (Aggregate Roots)
│ │ ├── User
│ │ ├── UserInfo
│ │ ├── Role
│ │ └── VerificationCode
│ │
│ ├── valueobjects/ (Value Objects)
│ │ ├── Email
│ │ ├── Password
│ │ ├── Username
│ │ └── IdentificationType
│ │
│ └── repositories/ (Repository Interfaces)
│ ├── UserRepository
│ ├── UserInfoRepository
│ └── VerificationCodeRepository
│
├── infrastructure/ (Infrastructure Layer)
│ ├── controllers/ (REST API Controllers)
│ │ ├── AuthController
│ │ ├── PasswordRecoveryController
│ │ ├── UserInfoController
│ │ ├── VerificationController
│ │ └── OAuth2Controller
│ │
│ ├── dtos/ (Infrastructure DTOs)
│ │ ├── LoginRequest
│ │ ├── RegisterRequest
│ │ └── VerifyCodeRequest
│ │
│ ├── persistence/ (JPA Implementation)
│ │ ├── entities/
│ │ │ ├── UserEntity
│ │ │ └── UserInfoEntity
│ │ ├── repositories/
│ │ │ ├── JpaUserRepository
│ │ │ ├── UserRepositoryJpaAdapter
│ │ │ └── UserInfoRepositoryJpaAdapter
│ │ └── mappers/
│ │ ├── UserMapper
│ │ └── UserInfoMapper
│ │
│ ├── security/ (Security Adapters)
│ │ ├── jwt/
│ │ │ ├── JwtTokenProvider
│ │ │ ├── JwtAuthenticationFilter
│ │ │ └── JwtProperties
│ │ ├── encoder/
│ │ │ └── BCryptPasswordEncoderAdapter
│ │ └── oauth2/
│ │ ├── OAuth2UserServiceAdapter
│ │ ├── OAuth2LoginSuccessHandler
│ │ └── OAuth2ClientConfig
│ │
│ ├── services/ (Email Implementation)
│ │ └── EmailServiceMailHog
│ │
│ ├── config/ (Configuration)
│ │ ├── SwaggerConfig
│ │ ├── RedisConfig
│ │ ├── ValidationConfig
│ │ └── EmailConfig
│ │
│ └── exception/ (Exception Handling)
│ └── GlobalExceptionHandler
│
└── IdentifyserviceApplication (Main Entry Point)
```

**Dependencias entre capas:**

```
Infrastructure → Application → Domain
       ↓ ↓
   Frameworks Use Cases Core Business
   (Spring, (Services) (Entities, VOs)
    JPA, JWT)
```

**Reglas de dependencia:**
- Domain NO puede depender de nada
- Application puede depender de Domain
- Infrastructure puede depender de Application y Domain
- Las dependencias apuntan HACIA ADENTRO (hacia Domain)

---

### 4.2 UploadService - Estructura de Módulos (Hexagonal)

```
uploadservice/
│
├── api/ (API Adapter)
│ └── routes/
│ └── transaction_routes.py
│
├── application/ (Application Layer)
│ └── use_cases/
│ ├── process_bank_file.py
│ └── get_transaction_batch.py
│
├── domain/ (Domain Core - Hexagon Center)
│ ├── entities/
│ │ ├── transaction.py
│ │ ├── transaction_batch.py
│ │ ├── bank.py
│ │ └── category.py
│ │
│ └── ports/ (Abstractions)
│ ├── bank_parser.py
│ ├── classifier.py
│ ├── repository.py
│ └── message_queue.py
│
├── infrastructure/ (Infrastructure Adapters)
│ ├── parsers/ (Bank Parser Implementations)
│ │ ├── bancolombia_parser.py
│ │ ├── davivienda_parser.py
│ │ ├── nequi_parser.py
│ │ └── factory.py
│ │
│ ├── ml/ (ML Classifier Implementations)
│ │ ├── sklearn_classifier.py
│ │ └── simple_classifier.py
│ │
│ ├── persistence/ (Repository Implementations)
│ │ └── mysql_transaction_repository.py
│ │
│ └── messaging/ (Message Queue Implementations)
│ └── rabbitmq_publisher.py
│
├── models/ (ML Models)
│ ├── classifier_v1.joblib
│ └── tfidf_vectorizer_v1.joblib
│
├── config.py (Configuration)
├── dependencies.py (Dependency Injection)
└── main.py (Entry Point)
```

**Flujo de dependencias (Hexagonal):**

```
        API Adapter
             ↓
      Application Layer
             ↓
    ← Domain (Ports) →
    ↓ ↓
 Infrastructure Infrastructure
 (Parsers) (ML)
```

---

### 4.3 InsightService - Estructura de Módulos (Clean Architecture)

```
InsightService/
│
├── interface_adapters/ (Interface Adapters Layer)
│ ├── messaging/
│ │ └── rabbitmq_consumer.py
│ └── api/
│ └── health_routes.py
│
├── application/ (Application Layer)
│ └── use_cases/
│ ├── generate_insights.py
│ └── get_insights.py
│
├── domain/ (Domain Layer - Enterprise Business)
│ ├── entities/
│ │ ├── insight.py
│ │ └── insight_category.py
│ │
│ ├── services/ (Domain Services)
│ │ └── insight_generation_service.py
│ │
│ └── ports/ (Abstractions)
│ ├── llm_provider.py
│ ├── repository.py
│ └── transaction_repository.py
│
├── infrastructure/ (Infrastructure Layer)
│ ├── llm/
│ │ ├── ollama_provider.py
│ │ └── openai_provider.py
│ │
│ └── persistence/
│ ├── mysql_insight_repository.py
│ └── mysql_transaction_repository.py
│
├── config.py
└── main.py
```

---

## 5. Vista de Componentes y Conectores

**Propósito:** Muestra el comportamiento en tiempo de ejecución, procesos, comunicación.

### Flujo Completo: Upload → Classification → Insights

```mermaid
sequenceDiagram
    actor User as Usuario
    participant Mobile as App Móvil
    participant IS as IdentityService
    participant US as UploadService
    participant ML as ML Classifier
    participant DB as MySQL
    participant MQ as RabbitMQ
    participant InsS as InsightService
    participant Ollama as Ollama LLM
    participant DS as DataService

    rect rgb(200, 230, 255)
        Note over User,IS: 1. Autenticación
        User->>Mobile: 1.1 Ingresa credenciales
        Mobile->>IS: POST /auth/login
        IS->>DB: SELECT user WHERE email=?
        DB-->>IS: User data
        IS->>IS: Verify password (BCrypt)
        IS->>IS: Generate JWT (15 min)
        IS->>IS: Generate Refresh Token
        IS->>Redis: Store refresh token
        IS-->>Mobile: {access_token, refresh_token}
        Mobile->>Mobile: Store tokens securely
    end

    rect rgb(255, 240, 200)
        Note over User,MQ: 2. Carga y Clasificación
        User->>Mobile: 2.1 Selecciona archivo Excel
        Mobile->>US: POST /transactions/upload<br/>Headers: {Authorization: Bearer JWT}
        US->>IS: GET /auth/validate?token=JWT
        IS->>IS: Validate JWT signature
        IS->>Redis: Check if revoked
        IS-->>US: {valid: true, user_id}

        US->>US: 2.2 Validate file structure<br/>(BancolombiaParser)
        US->>US: Parse transactions<br/>(pandas + openpyxl)

        US->>ML: 2.3 classify_batch(descriptions[])
        ML->>ML: TF-IDF vectorization
        ML->>ML: LogisticRegression.predict()
        ML-->>US: [(category_id, confidence)]

        US->>DB: 2.4 INSERT transaction_batch
        US->>DB: INSERT transactions (batch)
        US->>DB: UPDATE batch SET status='completed'

        US->>MQ: 2.5 publish('batch.processed',<br/>{batch_id, user_id})
        US-->>Mobile: 202 Accepted<br/>{batch_id, status: 'processing'}
        Mobile-->>User: "Transacciones procesadas"
    end

    rect rgb(230, 255, 230)
        Note over MQ,Ollama: 3. Generación de Insights (Asíncrono)
        MQ->>InsS: 3.1 consume('batch.processed')
        InsS->>DB: SELECT transactions WHERE batch_id=?
        DB-->>InsS: Transaction list

        InsS->>InsS: 3.2 Aggregate data<br/>(sum by category, totals)

        InsS->>Ollama: 3.3 POST /api/generate<br/>{prompt: "Analiza estos gastos..."}
        Ollama->>Ollama: LLM inference<br/>(llama3.1:8b)
        Ollama-->>InsS: Generated insight text

        InsS->>DB: 3.4 INSERT insight<br/>(user_id, content, metadata)
        InsS->>MQ: ACK message
    end

    rect rgb(255, 230, 230)
        Note over User,DS: 4. Consulta de Dashboard
        User->>Mobile: 4.1 Abre dashboard
        Mobile->>DS: GET /api/v1/dashboard<br/>Headers: {Authorization: Bearer JWT}
        DS->>IS: Validate JWT
        IS-->>DS: {valid: true, user_id}

        DS->>DB: 4.2 Query aggregations<br/>SELECT category, SUM(amount)...
        DB-->>DS: Aggregated data

        DS->>DB: Query recent insights
        DB-->>DS: Latest insights

        DS-->>Mobile: {expenses_by_category, insights, balance}
        Mobile->>Mobile: Render charts + cards
        Mobile-->>User: Dashboard con gráficos
    end
```

**Leyenda de Colores:**
- Azul: Autenticación
- Amarillo: Procesamiento de datos
- Verde: Generación de insights
- Rojo: Consulta y visualización

---

## 6. Vista de Deployment

**Propósito:** Muestra la infraestructura física/cloud y el mapeo de software a hardware.

### 6.1 Deployment Local/Desarrollo (Docker Compose)

```mermaid
graph TB
    subgraph "Máquina de Desarrollo (localhost)"
        subgraph "Docker Compose Network"
            IS_C[identity-service:8000<br/>Container]
            US_C[upload-service:8001<br/>Container]
            InsS_C[insight-service:8002<br/>Container]
            DS_C[data-service:8003<br/>Container]

            MySQL_C[mysql:3306<br/>Container<br/>Volume: mysql-data]
            Redis_C[redis:6379<br/>Container<br/>Volume: redis-data]
            RabbitMQ_C[rabbitmq:5672<br/>Container<br/>Volume: rabbitmq-data]
            Ollama_C[ollama:11434<br/>Container<br/>Volume: ollama-data]

            Prom_C[prometheus:9090<br/>Container]
            Graf_C[grafana:3000<br/>Container]
        end

        Browser[Chrome/Firefox<br/>localhost:3000]
        Mobile_Emu[Android Emulator<br/>localhost:8000-8003]
    end

    Browser --> Graf_C
    Mobile_Emu --> IS_C
    Mobile_Emu --> US_C
    Mobile_Emu --> DS_C

    IS_C --> MySQL_C
    IS_C --> Redis_C
    US_C --> MySQL_C
    US_C --> RabbitMQ_C
    InsS_C --> MySQL_C
    InsS_C --> RabbitMQ_C
    InsS_C --> Ollama_C
    DS_C --> MySQL_C

    Prom_C --> IS_C
    Prom_C --> US_C
    Graf_C --> Prom_C

    style IS_C fill:#FF6B6B,color:#fff
    style US_C fill:#4ECDC4,color:#fff
    style InsS_C fill:#FFE66D,color:#000
    style DS_C fill:#95E1D3,color:#000
```

---

### 6.2 Deployment Producción (Kubernetes en Cloud)

```mermaid
graph TB
    subgraph "Internet"
        Users[Usuarios Móviles]
    end

    subgraph "Cloud Provider (AWS)"
        subgraph "Application Load Balancer"
            ALB[ALB<br/>HTTPS/TLS<br/>SSL Certificate]
        end

        subgraph "EKS Cluster (Kubernetes)"
            subgraph "Namespace: flowlite"
                subgraph "Backend Deployments"
                    IS_POD1[identity-service-1]
                    IS_POD2[identity-service-2]
                    IS_POD3[identity-service-3]

                    US_POD1[upload-service-1]
                    US_POD2[upload-service-2]

                    InsS_POD1[insight-service-1]

                    DS_POD1[data-service-1]
                    DS_POD2[data-service-2]
                end

                subgraph "Services (ClusterIP)"
                    IS_SVC[identity-service:8000]
                    US_SVC[upload-service:8001]
                    InsS_SVC[insight-service:8002]
                    DS_SVC[data-service:8003]
                end

                subgraph "Monitoring"
                    Prom_POD[prometheus-0<br/>StatefulSet]
                    Graf_POD[grafana-0<br/>StatefulSet]
                    Jaeger_POD[jaeger-0]
                end
            end

            IS_POD1 --> IS_SVC
            IS_POD2 --> IS_SVC
            IS_POD3 --> IS_SVC
            US_POD1 --> US_SVC
            US_POD2 --> US_SVC
            InsS_POD1 --> InsS_SVC
            DS_POD1 --> DS_SVC
            DS_POD2 --> DS_SVC
        end

        subgraph "Managed Services"
            RDS[(RDS MySQL<br/>Multi-AZ<br/>Primary + Standby)]
            ElastiCache[ElastiCache Redis<br/>Replication Group<br/>Primary + Replica]
            AmazonMQ[Amazon MQ<br/>RabbitMQ<br/>Active/Standby]
        end

        subgraph "Storage"
            S3[S3 Bucket<br/>ML Models<br/>Backups]
            EBS[EBS Volumes<br/>Prometheus<br/>Grafana]
        end

        subgraph "Monitoring & Logging"
            CloudWatch[CloudWatch<br/>Logs + Metrics]
        end
    end

    Users -->|HTTPS| ALB
    ALB --> IS_SVC
    ALB --> US_SVC
    ALB --> DS_SVC

    IS_SVC --> RDS
    US_SVC --> RDS
    InsS_SVC --> RDS
    DS_SVC --> RDS

    IS_SVC --> ElastiCache
    US_SVC --> AmazonMQ
    InsS_SVC --> AmazonMQ

    US_SVC --> S3

    Prom_POD --> EBS
    Graf_POD --> EBS

    IS_POD1 --> CloudWatch
    US_POD1 --> CloudWatch
    InsS_POD1 --> CloudWatch

    style ALB fill:#F59E0B,stroke:#D97706,color:#fff
    style RDS fill:#5C7CFA,stroke:#364FC7,color:#fff
    style ElastiCache fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style S3 fill:#38A169,stroke:#2F855A,color:#fff
```

**Características del Deployment de Producción:**

| Componente | Estrategia | Configuración |
|------------|-----------|---------------|
| **Load Balancer** | Application Load Balancer | HTTPS/TLS, sticky sessions |
| **Identity Pods** | 3 réplicas mínimo | HPA: min 2, max 10 |
| **Upload Pods** | 2 réplicas mínimo | HPA: min 2, max 8 |
| **Insight Pods** | 1 réplica | HPA: min 1, max 3 |
| **Data Pods** | 2 réplicas mínimo | HPA: min 2, max 10 |
| **MySQL** | RDS Multi-AZ | Primary + Standby, auto-failover |
| **Redis** | ElastiCache Replication | Primary + Replica, auto-failover |
| **RabbitMQ** | Amazon MQ | Active/Standby cluster |
| **Storage** | S3 + EBS | S3 para modelos, EBS para Prometheus |

---

## 7. Vista de Datos

**Propósito:** Muestra el modelo de datos, esquemas de base de datos y flujo de datos.

### 7.1 Modelo de Entidad-Relación

```mermaid
erDiagram
    USER ||--o{ TRANSACTION : "owns"
    USER ||--o| USER_INFO : "has"
    USER ||--o{ VERIFICATION_CODE : "has"
    USER ||--o{ TRANSACTION_BATCH : "creates"
    USER ||--o{ INSIGHT : "receives"

    TRANSACTION }o--|| TRANSACTION_CATEGORY : "belongs to"
    TRANSACTION }o--|| TRANSACTION_BATCH : "grouped in"
    TRANSACTION }o--|| BANK : "from"

    TRANSACTION_BATCH ||--o{ INSIGHT : "generates"

    INSIGHT }o--|| INSIGHT_CATEGORY : "categorized as"

    USER {
        UUID id PK
        VARCHAR email UK
        VARCHAR password_hash
        ENUM role
        BOOLEAN email_verified
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    USER_INFO {
        UUID id PK
        UUID user_id FK
        VARCHAR full_name
        VARCHAR identification_type
        VARCHAR identification_number
        DATE birth_date
        VARCHAR phone_number
        TIMESTAMP created_at
    }

    VERIFICATION_CODE {
        UUID id PK
        UUID user_id FK
        VARCHAR code
        TIMESTAMP expires_at
        BOOLEAN used
        TIMESTAMP created_at
    }

    BANK {
        INT id PK
        VARCHAR code UK
        VARCHAR name
        VARCHAR country
        BOOLEAN active
    }

    TRANSACTION_CATEGORY {
        INT id PK
        VARCHAR name
        VARCHAR description
        VARCHAR color_hex
        VARCHAR icon
        INT parent_id FK
    }

    TRANSACTION_BATCH {
        UUID id PK
        UUID user_id FK
        INT bank_id FK
        ENUM status
        INT total_transactions
        INT classified_count
        TIMESTAMP created_at
        TIMESTAMP completed_at
    }

    TRANSACTION {
        UUID id PK
        UUID batch_id FK
        UUID user_id FK
        DATE transaction_date
        DECIMAL amount
        TEXT description
        VARCHAR recipient
        INT category_id FK
        DECIMAL confidence_score
        TIMESTAMP created_at
    }

    INSIGHT_CATEGORY {
        INT id PK
        VARCHAR code UK
        VARCHAR name
        VARCHAR description
    }

    INSIGHT {
        UUID id PK
        UUID user_id FK
        UUID batch_id FK
        INT category_id FK
        TEXT content
        JSON metadata
        TIMESTAMP created_at
    }
```

### 7.2 Esquema SQL Completo

```sql
-- ============================================
-- SCHEMA: flowlite_db
-- ============================================

-- ============================================
-- 1. USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id BINARY(16) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'ADMIN') DEFAULT 'USER',
    email_verified BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_oauth (oauth_provider, oauth_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_info (
    id BINARY(16) PRIMARY KEY,
    user_id BINARY(16) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    identification_type VARCHAR(50),
    identification_number VARCHAR(50),
    birth_date DATE,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE verification_code (
    id BINARY(16) PRIMARY KEY,
    user_id BINARY(16) NOT NULL,
    code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_code (user_id, code),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. CATALOGS
-- ============================================

CREATE TABLE bank (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) DEFAULT 'CO',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO bank (code, name) VALUES
    ('bancolombia', 'Bancolombia'),
    ('davivienda', 'Davivienda'),
    ('nequi', 'Nequi'),
    ('bbva', 'BBVA Colombia');

CREATE TABLE transaction_category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color_hex VARCHAR(7) DEFAULT '#6B7280',
    icon VARCHAR(50),
    parent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES transaction_category(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO transaction_category (name, description, color_hex, icon) VALUES
    ('Alimentación', 'Supermercado, restaurantes, comida', '#10B981', 'restaurant'),
    ('Transporte', 'Uber, taxi, gasolina, transporte público', '#3B82F6', 'directions_car'),
    ('Entretenimiento', 'Netflix, cine, suscripciones', '#8B5CF6', 'movie'),
    ('Servicios', 'Luz, agua, gas, internet, celular', '#F59E0B', 'miscellaneous_services'),
    ('Salud', 'Medicina, consultas, seguros', '#EF4444', 'local_hospital'),
    ('Educación', 'Cursos, libros, universidad', '#6366F1', 'school'),
    ('Vivienda', 'Arriendo, administración, reparaciones', '#EC4899', 'home'),
    ('Ropa', 'Vestuario, accesorios', '#14B8A6', 'checkroom'),
    ('Tecnología', 'Dispositivos, software, gadgets', '#06B6D4', 'devices'),
    ('Deportes', 'Gimnasio, equipamiento deportivo', '#F97316', 'fitness_center'),
    ('Ahorro', 'Inversiones, cuentas de ahorro', '#22C55E', 'savings'),
    ('Otros', 'Gastos no categorizados', '#6B7280', 'category');

CREATE TABLE insight_category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO insight_category (code, name, description) VALUES
    ('monthly_analysis', 'Análisis Mensual', 'Análisis general de gastos del mes'),
    ('spending_alert', 'Alerta de Gasto', 'Alerta cuando hay gasto excesivo en una categoría'),
    ('saving_tip', 'Consejo de Ahorro', 'Recomendación personalizada para ahorrar');

-- ============================================
-- 3. TRANSACTIONS
-- ============================================

CREATE TABLE transaction_batch (
    id BINARY(16) PRIMARY KEY,
    user_id BINARY(16) NOT NULL,
    bank_id INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'processing',
    total_transactions INT DEFAULT 0,
    classified_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bank_id) REFERENCES bank(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE transaction (
    id BINARY(16) PRIMARY KEY,
    batch_id BINARY(16) NOT NULL,
    user_id BINARY(16) NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    description TEXT NOT NULL,
    recipient VARCHAR(255),
    category_id INT,
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES transaction_batch(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES transaction_category(id),
    INDEX idx_user_date (user_id, transaction_date DESC),
    INDEX idx_batch (batch_id),
    INDEX idx_category (category_id),
    INDEX idx_amount (amount),
    FULLTEXT idx_description (description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. INSIGHTS
-- ============================================

CREATE TABLE insights (
    id BINARY(16) PRIMARY KEY,
    user_id BINARY(16) NOT NULL,
    batch_id BINARY(16),
    category_id INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (batch_id) REFERENCES transaction_batch(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES insight_category(id),
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_batch (batch_id),
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. VIEWS (Para optimización de queries)
-- ============================================

-- Vista de gastos por categoría (pre-agregada)
CREATE VIEW v_expenses_by_category AS
SELECT
    user_id,
    category_id,
    tc.name AS category_name,
    tc.color_hex AS category_color,
    SUM(ABS(amount)) AS total_expenses,
    COUNT(*) AS transaction_count,
    AVG(ABS(amount)) AS avg_transaction
FROM transaction t
JOIN transaction_category tc ON t.category_id = tc.id
WHERE amount < 0 -- Solo gastos
GROUP BY user_id, category_id, tc.name, tc.color_hex;

-- Vista de insights recientes
CREATE VIEW v_recent_insights AS
SELECT
    i.id,
    i.user_id,
    i.content,
    ic.name AS category_name,
    i.created_at
FROM insights i
JOIN insight_category ic ON i.category_id = ic.id
ORDER BY i.created_at DESC;
```

### 7.3 Índices y Optimización

**Índices Principales:**

| Tabla | Índice | Tipo | Justificación |
|-------|--------|------|---------------|
| `users` | `idx_email` | UNIQUE | Login por email (búsqueda frecuente) |
| `transaction` | `idx_user_date` | COMPOSITE | Dashboard filtrado por usuario y fecha |
| `transaction` | `idx_category` | SIMPLE | Agregación por categoría |
| `transaction` | `idx_description` | FULLTEXT | Búsqueda de transacciones por texto |
| `insights` | `idx_user_created` | COMPOSITE | Consulta de insights ordenados por fecha |

**Particionado (Futuro):**

```sql
-- Particionar transacciones por año para mejorar performance
ALTER TABLE transaction
PARTITION BY RANGE (YEAR(transaction_date)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

---

## 8. Vista de Seguridad

**Propósito:** Muestra mecanismos de seguridad, flujos de autenticación y protección de datos.

### 8.1 Flujo de Autenticación JWT

```mermaid
sequenceDiagram
    actor User
    participant Mobile
    participant IS as IdentityService
    participant Redis
    participant DB as MySQL
    participant US as UploadService

    rect rgb(240, 240, 255)
        Note over User,DB: Login Flow
        User->>Mobile: Enter credentials
        Mobile->>IS: POST /auth/login<br/>{email, password}
        IS->>DB: SELECT * FROM users<br/>WHERE email=?
        DB-->>IS: User record
        IS->>IS: BCrypt.verify(password, hash)
        alt Password valid
            IS->>IS: Generate JWT (15 min)<br/>Claims: {user_id, email, role}
            IS->>IS: Generate Refresh Token (7 days)
            IS->>Redis: SET refresh:{token} = user_id<br/>EX 604800
            IS-->>Mobile: {access_token, refresh_token}
            Mobile->>Mobile: Store in FlutterSecureStorage
        else Password invalid
            IS-->>Mobile: 401 Unauthorized
        end
    end

    rect rgb(255, 240, 240)
        Note over Mobile,US: Protected Request
        Mobile->>US: POST /transactions/upload<br/>Header: Authorization: Bearer {JWT}
        US->>IS: GET /auth/validate?token={JWT}
        IS->>IS: Verify signature (HMAC-SHA512)
        IS->>IS: Check expiration
        IS->>Redis: EXISTS revoked:{JWT}
        Redis-->>IS: false (not revoked)
        IS-->>US: {valid: true, user_id, role}
        US->>US: Process request with user context
    end

    rect rgb(240, 255, 240)
        Note over Mobile,Redis: Token Refresh
        Mobile->>IS: POST /auth/refresh<br/>{refresh_token}
        IS->>Redis: GET refresh:{token}
        Redis-->>IS: user_id
        IS->>IS: Generate new JWT (15 min)
        IS-->>Mobile: {access_token}
    end

    rect rgb(255, 240, 240)
        Note over Mobile,Redis: Logout
        Mobile->>IS: POST /auth/logout<br/>{access_token}
        IS->>Redis: SET revoked:{JWT} = 1<br/>EX {remaining_ttl}
        IS->>Redis: DEL refresh:{token}
        IS-->>Mobile: 200 OK
        Mobile->>Mobile: Clear local storage
    end
```

### 8.2 Mecanismos de Seguridad

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Transport Security"
            TLS[TLS 1.3<br/>HTTPS Everywhere]
        end

        subgraph "Authentication"
            JWT[JWT Tokens<br/>HMAC-SHA512]
            OAuth[OAuth2<br/>Google/GitHub/Microsoft]
            BCrypt[BCrypt<br/>Password Hashing<br/>Cost: 12]
        end

        subgraph "Authorization"
            RBAC[Role-Based Access<br/>USER / ADMIN]
            JWTClaims[JWT Claims<br/>user_id, email, role]
        end

        subgraph "Data Protection"
            Encryption[Encryption at Rest<br/>MySQL TDE]
            Validation[Input Validation<br/>Value Objects]
            Sanitization[SQL Injection Prevention<br/>Prepared Statements]
        end

        subgraph "Session Management"
            TokenRevoke[Token Revocation<br/>Redis Blacklist]
            RefreshToken[Refresh Tokens<br/>7 days expiry]
            RateLimit[Rate Limiting<br/>100 req/min]
        end

        subgraph "Audit & Monitoring"
            Logging[Security Logs<br/>Failed logins, token issues]
            Alerts[Alerting<br/>Multiple failed attempts]
        end
    end

    TLS --> JWT
    TLS --> OAuth
    JWT --> JWTClaims
    OAuth --> JWTClaims
    JWTClaims --> RBAC

    BCrypt --> Validation
    Validation --> Sanitization
    Sanitization --> Encryption

    JWT --> TokenRevoke
    JWT --> RefreshToken
    JWT --> RateLimit

    RBAC --> Logging
    TokenRevoke --> Logging
    Logging --> Alerts
```

**Implementación de Seguridad por Capa:**

| Capa | Mecanismo | Implementación |
|------|-----------|----------------|
| **Transport** | TLS 1.3 | ALB/Ingress con certificados SSL |
| **Authentication** | JWT | JJWT library, HMAC-SHA512, 15 min expiry |
| **Password** | BCrypt | Cost factor: 12 (2^12 = 4096 iterations) |
| **Authorization** | RBAC | Claims en JWT: `role: ['USER', 'ADMIN']` |
| **Data** | Encryption | MySQL Transparent Data Encryption |
| **Input** | Validation | Value Objects (Email, Password) + Jakarta Validation |
| **SQL Injection** | Prepared Statements | JPA + SQLAlchemy ORM |
| **XSS** | Output Encoding | JSON serialization automática |
| **CSRF** | Token-based | JWT elimina necesidad de cookies |
| **Rate Limiting** | Redis | 100 requests/min per user |

---

### 8.3 Gestión de Secretos

**Desarrollo (Docker Compose):**

```bash
# .env file
JWT_SECRET=dev_secret_key_change_in_production
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_PASSWORD=flowlite_dev
```

**Producción (Kubernetes Secrets):**

```yaml
# k8s/secrets.yaml (Base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: flowlite
type: Opaque
data:
  jwt-secret: <base64-encoded-value>
  mysql-password: <base64-encoded-value>
  rabbitmq-password: <base64-encoded-value>
```

**Mejores Prácticas:**
- Usar AWS Secrets Manager / Azure Key Vault en producción
- Rotar secretos periódicamente (cada 90 días)
- Nunca commitear secretos en Git
- Diferentes secretos por ambiente (dev, staging, prod)

---

## Conclusión

Este documento presenta las **8 vistas arquitectónicas** principales del sistema Flowlite Personal Finance:

1. **Vista de Contexto:** Sistema y actores externos
2. **Vista de Contenedores:** Servicios y tecnologías
3. **Vista de Componentes:** Estructura interna de cada servicio
4. **Vista de Módulos:** Organización del código
5. **Vista de Componentes y Conectores:** Flujos en runtime
6. **Vista de Deployment:** Infraestructura física/cloud
7. **Vista de Datos:** Modelo de datos y esquemas
8. **Vista de Seguridad:** Mecanismos de protección

Estas vistas proporcionan una comprensión completa del sistema desde múltiples perspectivas, facilitando:
- Comunicación con stakeholders
- Onboarding de nuevos desarrolladores
- Análisis de impacto de cambios
- Toma de decisiones arquitectónicas
