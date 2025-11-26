# Aplicación de Domain-Driven Design (DDD) en Flowlite Personal Finance

## Resumen Ejecutivo

**Autores:**
- Carlos Felipe Caro Arroyave
- Joiver Andrés Gómez Coronado

Este documento resume la aplicación de conceptos de Domain-Driven Design (DDD) y Arquitectura Hexagonal en los microservicios de Flowlite Personal Finance. Los cuatro servicios analizados (IdentifyService, UploadService, InsightService y DataService) demuestran una implementación coherente y consistente de patrones DDD.

---

## 1. Patrones Tácticos de DDD Aplicados

### 1.1 Entidades (Entities)

**Qué es:** Objetos con identidad única que persisten a través del tiempo.

**Dónde se usa:**

| Servicio | Entidades | Ubicación | Justificación |
|----------|-----------|-----------|---------------|
| **IdentifyService** | `User`, `UserInfo`, `VerificationCode`, `PendingUserData` | `domain/entities/` | Representan conceptos del dominio de autenticación con identidad y ciclo de vida propios |
| **UploadService** | `Transaction`, `TransactionBatch`, `FileUploadHistory` | `domain/entities/` | Modelan transacciones financieras y procesamiento por lotes con identidad única |
| **InsightService** | `Transaction`, `Insight`, `TransactionBatch` | `domain/entities.py` | Representan recomendaciones financieras y datos de transacciones |
| **DataService** | `Transaction`, `User`, `Insight`, `Dashboard` | `domain/entities/` | Encapsulan datos de consulta del dominio financiero |

**Por qué:** Las entidades encapsulan lógica de negocio y mantienen invariantes del dominio. Cada una tiene un identificador único (UUID) y comportamiento propio.

**Ejemplo práctico:**
```java
// IdentifyService - User Entity con comportamiento de dominio
@Data
@Builder
public class User {
    private String id;
    private Username username;
    private Email email;
    private Password password;

    // Comportamiento de dominio
    public void deactivate() { this.active = false; }
    public void changeRole(Role newRole) { this.role = newRole; }
}
```

```python
# InsightService - Insight Entity con factory method
@dataclass
class Insight:
    id_insight: UUID
    id_user: UserId
    title: str
    relevance: int

    @classmethod
    def create(cls, id_user: UserId, title: str, text: str, relevance: int):
        # Validaciones de negocio
        if not 1 <= relevance <= 10:
            raise ValueError("Relevance must be between 1 and 10")
```

---

### 1.2 Value Objects (Objetos de Valor)

**Qué es:** Objetos inmutables definidos por sus atributos, sin identidad propia.

**Dónde se usa:**

| Servicio | Value Objects | Ubicación | Justificación |
|----------|---------------|-----------|---------------|
| **IdentifyService** | `Email`, `Password`, `Username`, `IdentificationType` | `domain/valueobjects/` | Encapsulan validación y reglas de formato, previenen uso de tipos primitivos |
| **UploadService** | `RawTransaction`, `Decimal` (para valores monetarios) | `domain/ports/` | Representan datos inmutables del parsing de Excel |
| **InsightService** | `Money`, `UserId`, `CategoryId`, `BatchId` | `domain/value_objects.py` | Proporcionan type safety y validaciones de negocio |
| **DataService** | `Balance`, `Decimal` (valores monetarios) | `domain/entities/` | Encapsulan cálculos financieros inmutables |

**Por qué:** Los Value Objects previenen "Primitive Obsession", añaden seguridad de tipos y encapsulan validaciones del dominio.

**Ejemplo práctico:**
```java
// IdentifyService - Email Value Object con validación
@Value
public class Email {
    String value;

    public Email(String value) {
        if (value == null || !Pattern.matches("^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$", value)) {
            throw new IllegalArgumentException("Email inválido");
        }
        this.value = value.toLowerCase();
    }
}
```

```python
# InsightService - Money Value Object
@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __str__(self) -> str:
        return f"${self.amount:,.2f}"
```

---

### 1.3 Agregados (Aggregates)

**Qué es:** Grupo de entidades y value objects tratados como una unidad, con una raíz agregada.

**Dónde se usa:**

| Servicio | Agregado Root | Ubicación | Justificación |
|----------|---------------|-----------|---------------|
| **IdentifyService** | `User` (con credenciales), `UserInfo` (con datos personales) | `domain/entities/` | Separados porque tienen diferentes ciclos de vida y consistencia |
| **UploadService** | `TransactionBatch` (contiene transacciones) | `domain/entities/` | Controla el ciclo de vida de las transacciones en un lote |
| **InsightService** | `Insight` | `domain/entities.py` | Agrupa recomendación financiera con metadatos |
| **DataService** | `Dashboard` (agrega User, Balance, Transactions, Insights) | `domain/entities/` | Consolida datos del dashboard como unidad coherente |

**Por qué:** Los agregados garantizan consistencia transaccional y encapsulan reglas de negocio complejas.

**Ejemplo práctico:**
```python
# UploadService - TransactionBatch como Aggregate Root
@dataclass
class TransactionBatch:
    id_batch: Optional[UUID]
    process_status: str
    batch_size: Optional[int]

    @property
    def processed_percentage(self) -> float:
        """Lógica de dominio encapsulada"""
        if self.batch_size == 0 or self.batch_size is None:
            return 0.0
        if self.process_status == "completed":
            return 100.0
        return 0.0
```

```python
# DataService - Dashboard Aggregate
@dataclass
class Dashboard:
    user: User
    balance: Balance
    transactions: List[Transaction]
    recommendations: List[Insight]
    # Agrega múltiples entidades en una vista coherente
```

---

### 1.4 Repositorios (Repositories)

**Qué es:** Abstracción que proporciona interfaz tipo colección para acceso a datos.

**Dónde se usa:**

| Servicio | Repositories | Ubicación | Justificación |
|----------|--------------|-----------|---------------|
| **IdentifyService** | `UserRepository`, `UserInfoRepository`, `VerificationCodeRepository` | `domain/repositories/` (interfaces)<br>`infrastructure/persistence/` (implementaciones) | Abstraen persistencia JPA y Redis del dominio |
| **UploadService** | `TransactionRepositoryPort`, `BankRepositoryPort`, `CategoryRepositoryPort` | `domain/ports/` (interfaces)<br>`infrastructure/repositories/` (implementaciones) | Separan lógica de negocio de detalles de MySQL |
| **InsightService** | `TransactionRepository`, `InsightRepository`, `BatchRepository` | `domain/repositories.py` (interfaces)<br>`infrastructure/database/repositories.py` (implementaciones) | Aíslan dominio de SQLAlchemy |
| **DataService** | `TransactionRepositoryPort`, `DashboardRepositoryPort`, `InsightRepositoryPort` | `domain/ports/` (interfaces)<br>`infrastructure/repositories/` (implementaciones) | Abstraen consultas complejas de base de datos |

**Por qué:** Los repositorios implementan el patrón Repository y son parte fundamental de la Arquitectura Hexagonal (Ports).

**Ejemplo práctico:**
```java
// IdentifyService - Repository Port (Domain)
public interface UserRepository {
    Optional<User> findById(UUID id);
    Optional<User> findByEmail(String email);
    User save(User user);
}

// Infrastructure Adapter
@Repository
public class UserRepositoryJpaAdapter implements UserRepository {
    private final JpaUserRepository jpaUserRepository;

    public User save(User user) {
        var entity = UserMapper.toEntity(user);
        var saved = jpaUserRepository.save(entity);
        return UserMapper.toDomain(saved);
    }
}
```

```python
# UploadService - Repository Port (Domain)
class TransactionRepositoryPort(ABC):
    @abstractmethod
    async def save_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        pass

# Infrastructure Adapter
class MySQLTransactionRepository(TransactionRepositoryPort):
    async def save_batch(self, transactions: List[Transaction]):
        models = [self._to_model(tx) for tx in transactions]
        self.session.add_all(models)
        await self.session.flush()
        return [self._to_entity(model) for model in models]
```

---

### 1.5 Servicios de Dominio (Domain Services)

**Qué es:** Lógica de negocio que no pertenece a una entidad específica.

**Dónde se usa:**

| Servicio | Domain Services | Ubicación | Justificación |
|----------|-----------------|-----------|---------------|
| **IdentifyService** | Lógica en Application Services (orquestación) | `application/services/` | Coordinan validaciones y operaciones de autenticación |
| **UploadService** | `ClassifierPort` (clasificación ML), `ExcelParserPort` (parsing) | `domain/ports/` | Encapsulan lógica de clasificación y parsing de archivos |
| **InsightService** | `FinancialPromptBuilder` | `domain/prompt_builder.py` | Construye prompts con conocimiento financiero del dominio |
| **DataService** | Lógica de agregación en repositories | `infrastructure/repositories/` | Cálculos de balance y agregaciones financieras |

**Por qué:** Algunos comportamientos no pertenecen naturalmente a una entidad, pero son parte del dominio.

**Ejemplo práctico:**
```python
# InsightService - Domain Service
class FinancialPromptBuilder:
    """Construye prompts con conocimiento del dominio financiero"""

    SYSTEM_PROMPT = """You are an expert financial advisor AI..."""
    CATEGORY_TYPES = ['savings', 'spending', 'investment', 'debt', 'budget']

    @staticmethod
    def build_transaction_summary(transactions: List[TransactionSummary]) -> str:
        """Lógica de dominio para análisis temporal"""
        # Agrupa transacciones por mes/año para análisis de tendencias
```

---

### 1.6 Application Services (Casos de Uso)

**Qué es:** Orquestadores que coordinan el flujo de la aplicación sin contener lógica de negocio.

**Dónde se usa:**

| Servicio | Application Services | Ubicación | Justificación |
|----------|---------------------|-----------|---------------|
| **IdentifyService** | `RegisterUserService`, `LoginUserService`, `PreregisterUserService` | `application/services/` | Orquestan flujos de autenticación y registro |
| **UploadService** | `ProcessFilesUseCase`, `GetBatchStatusUseCase` | `application/use_cases/` | Coordinan parsing, clasificación y persistencia |
| **InsightService** | `GenerateInsightsUseCase` | `application/use_cases/` | Orquesta generación de insights con LLM |
| **DataService** | Implementados en routes (enfoque simplificado) | `api/routes/` | Consultas y transformaciones a DTOs |

**Por qué:** Separan la orquestación de la lógica de negocio, facilitando testing y mantenimiento.

**Ejemplo práctico:**
```java
// IdentifyService - Application Service
@Service
public class RegisterUserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public User register(String username, String email, String rawPassword) {
        // Orquestación sin lógica de negocio
        userRepository.findByEmail(email).ifPresent(u -> {
            throw new IllegalArgumentException("Email ya registrado");
        });

        User newUser = User.builder()
            .username(new Username(username))
            .email(new Email(email))  // Value Objects hacen validación
            .password(new Password(passwordEncoder.encode(rawPassword)))
            .build();

        return userRepository.save(newUser);
    }
}
```

```python
# UploadService - Use Case
class ProcessFilesUseCase:
    def __init__(
        self,
        transaction_repo: TransactionRepositoryPort,
        classifier: ClassifierPort,
        message_broker: MessageBrokerPort,
    ):
        # Dependencias inyectadas (Ports)

    async def execute(self, files_data, parser, user_id):
        # 1. Validar duplicados
        # 2. Parsear archivos
        # 3. Clasificar transacciones
        # 4. Guardar en repositorio
        # 5. Publicar evento de dominio
```

---

## 2. Arquitectura Hexagonal (Ports & Adapters)

### 2.1 Concepto

**Qué es:** Arquitectura que separa la lógica de negocio (dominio) de los detalles técnicos mediante puertos (interfaces) y adaptadores (implementaciones).

### 2.2 Aplicación en los Servicios

**Estructura común en todos los servicios:**

```
┌─────────────────────────────────────┐
│    API/Interfaces (Adapters IN)     │  ← REST controllers, Message handlers
│         (Infrastructure)             │
└──────────────┬──────────────────────┘
               ↓
┌──────────────▼──────────────────────┐
│      Application Layer               │  ← Use Cases, DTOs
│    (Orquestación sin lógica)        │
└──────────────┬──────────────────────┘
               ↓
┌──────────────▼──────────────────────┐
│        Domain Layer (CORE)           │  ← Entities, Value Objects, Ports
│    (Lógica de negocio pura)         │
└──────────────▲──────────────────────┘
               ↑ implements
┌──────────────┴──────────────────────┐
│   Infrastructure (Adapters OUT)      │  ← Repositories, External Services
│    (Detalles técnicos)              │
└─────────────────────────────────────┘
```

### 2.3 Ports (Puertos)

**Definidos en la capa de dominio:**

| Servicio | Ports Ejemplos | Justificación |
|----------|----------------|---------------|
| **IdentifyService** | `TokenProvider`, `EmailService`, `PasswordEncoder` | Abstraen JWT, email y encriptación del dominio |
| **UploadService** | `ClassifierPort`, `ExcelParserPort`, `MessageBrokerPort` | Separan ML, parsing y messaging del core |
| **InsightService** | `LLMService`, `TransactionRepository` | Aíslan servicio Ollama y base de datos |
| **DataService** | `TransactionRepositoryPort`, `DashboardRepositoryPort` | Abstraen consultas de SQLAlchemy |

**Ejemplo:**
```python
# Domain Port (Interface)
class ClassifierPort(ABC):
    @abstractmethod
    async def classify(self, description: str) -> str:
        pass
```

### 2.4 Adapters (Adaptadores)

**Implementados en la capa de infraestructura:**

| Servicio | Adapters Ejemplos | Tecnología |
|----------|-------------------|------------|
| **IdentifyService** | `JwtTokenProvider`, `BCryptPasswordEncoderAdapter`, `EmailServiceMailHog` | JWT, BCrypt, SMTP |
| **UploadService** | `MLClassifier`, `BancolombiaParser`, `RabbitMQProducer` | scikit-learn, pandas, RabbitMQ |
| **InsightService** | `OllamaService`, `SQLAlchemyTransactionRepository`, `RabbitMQConsumer` | Ollama, SQLAlchemy, RabbitMQ |
| **DataService** | `TransactionRepository`, `IdentityServiceClient` | SQLAlchemy, HTTP client |

**Ejemplo:**
```python
# Infrastructure Adapter
class MLClassifier(ClassifierPort):
    async def classify(self, description: str) -> str:
        # Implementación con ML (sklearn)
        cleaned = clean_text(description)
        X = self._vectorizer.transform([cleaned])
        prediction = self._model.predict(X)[0]
        return prediction
```

### 2.5 Beneficios Observados

1. **Testabilidad:** Puertos permiten mock de dependencias
2. **Flexibilidad:** Múltiples implementaciones (ej: `SimpleClassifier` vs `MLClassifier`)
3. **Independencia tecnológica:** Dominio no depende de frameworks
4. **Mantenibilidad:** Cambios en infraestructura no afectan dominio

---

## 3. Bounded Contexts (Contextos Acotados)

### 3.1 Concepto

**Qué es:** Límites explícitos donde un modelo de dominio específico es válido y consistente.

### 3.2 Contextos Identificados

| Bounded Context | Servicio | Responsabilidad | Lenguaje Ubicuo |
|-----------------|----------|-----------------|-----------------|
| **Identity & Access Management** | IdentifyService | Autenticación, autorización, gestión de usuarios | User, Token, Verification, Role, Preregister |
| **Transaction Upload & Classification** | UploadService | Carga de archivos, parsing bancario, clasificación | Transaction, Batch, Parser, Classifier, File Hash |
| **Financial Insights Generation** | InsightService | Generación de recomendaciones con IA | Insight, Recommendation, Relevance, LLM, Temporal Analysis |
| **Financial Data Management** | DataService | Consultas y vistas de datos financieros | Dashboard, Balance, Income, Expense, Query |

### 3.3 Integración entre Contextos

**Event-Driven Architecture:**
```
UploadService (procesa archivo)
    ↓ Publica evento
RabbitMQ: "batch_processed"
    ↓ Consume evento
InsightService (genera insights)
```

**Shared Database (con aislamiento lógico):**
- Cada servicio accede a sus propias tablas
- Referencias por UUID (sin foreign keys entre contextos)
- Loose coupling mediante IDs

**Anti-Corruption Layers:**
- DTOs previenen leak de modelos entre contextos
- Mappers convierten entre representaciones
- `CategoryMapper` en InsightService traduce categorías del LLM

---

## 4. Lenguaje Ubicuo (Ubiquitous Language)

### 4.1 Concepto

**Qué es:** Vocabulario compartido entre desarrolladores y expertos del dominio, usado consistentemente en código y conversación.

### 4.2 Términos por Contexto

**IdentifyService:**
- User, UserInfo, Email, Password, Username
- Verification, VerificationCode
- Preregister, PendingUser
- Token, Role
- Recovery (password recovery)

**UploadService:**
- Transaction, TransactionBatch
- Parser, Classifier
- FileUploadHistory, FileHash
- RawTransaction (pre-procesamiento)
- BatchStatus (pending, processing, completed)

**InsightService:**
- Insight, Recommendation
- Relevance (1-10)
- TransactionSummary
- TemporalAnalysis (year-month)
- FinancialCategory (savings, spending, investment, debt, budget)

**DataService:**
- Dashboard
- Balance (totalBalance, incomes, expenses)
- TransactionType (income, expense)
- Pagination (page, pageSize)

### 4.3 Evidencia en Código

**Nombres de clases:**
```java
// Refleja lenguaje del negocio
public class PreregisterUserService
public class PasswordRecoveryService
public class VerificationCode
```

**Nombres de métodos:**
```python
# Lenguaje del dominio financiero
def aggregate_by_category(...)
def generate_recommendations(...)
def is_processed(...)
def processed_percentage(...)
```

**Comentarios de dominio:**
```python
"""Groups transactions by category, year-month, and type for temporal analysis"""
```

---

## 5. Separación en Capas

### 5.1 Domain Layer (Núcleo)

**Características:**
- Sin dependencias externas (frameworks, librerías de infraestructura)
- Contiene lógica de negocio pura
- Define contratos (Ports) pero no implementaciones

**Ejemplos:**
```
IdentifyService/domain/
├── entities/
├── valueobjects/
└── repositories/ (interfaces)

UploadService/domain/
├── entities/
└── ports/

InsightService/domain/
├── entities.py
├── value_objects.py
└── repositories.py (interfaces)
```

### 5.2 Application Layer (Orquestación)

**Características:**
- Coordina casos de uso
- No contiene lógica de negocio
- Depende de Domain
- Define DTOs para comunicación

**Ejemplos:**
```
*/application/
├── services/ o use_cases/
└── dto/
```

### 5.3 Infrastructure Layer (Detalles Técnicos)

**Características:**
- Implementa Ports del dominio
- Contiene detalles de frameworks
- Maneja persistencia, APIs externas, messaging

**Ejemplos:**
```
*/infrastructure/
├── persistence/ o repositories/
├── messaging/
├── clients/
└── parsers/
```

### 5.4 Regla de Dependencias

**Principio clave:** Las dependencias apuntan HACIA ADENTRO

```
Infrastructure → Application → Domain
     ✓              ✓           ✗ (no depende de nadie)
```

**Evidencia:**
- Domain no importa nada de Application ni Infrastructure
- Application importa Domain
- Infrastructure importa Domain y Application
- API/Controllers importan todo (composition root)

---

## 6. Patrones Complementarios

### 6.1 Factory Pattern

**Dónde:**
- `ParserFactory` (UploadService): Crea parsers por banco
- `EmailServiceFactory` (IdentifyService): Selecciona proveedor de email
- `Insight.create()` (InsightService): Factory method para crear insights

**Por qué:** Encapsula lógica de creación compleja

### 6.2 Mapper Pattern (Anti-Corruption Layer)

**Dónde:**
- `UserMapper` (IdentifyService): Domain ↔ JPA Entity
- `TransactionMapper` (InsightService): Domain ↔ SQLAlchemy Model
- `CategoryMapper` (InsightService): LLM categories → Domain categories

**Por qué:** Aísla dominio de modelos externos (ORM, APIs)

**Ejemplo:**
```java
// IdentifyService
public class UserMapper {
    public static User toDomain(UserEntity entity) {
        return User.builder()
            .username(new Username(entity.getUsername()))
            .email(new Email(entity.getEmail()))
            .password(new Password(entity.getPassword()))
            .build();
    }
}
```

### 6.3 Dependency Injection

**Dónde:**
- FastAPI `Depends()` (Python services)
- Spring `@Autowired` / Constructor Injection (IdentifyService)
- `Container` class (InsightService)

**Por qué:** Invierte control, facilita testing, permite cambiar implementaciones

### 6.4 Domain Events

**Dónde:**
- `MessageBrokerPort.publish_batch_processed()` (UploadService)
- RabbitMQ event consumption (InsightService)

**Por qué:** Comunicación asíncrona entre bounded contexts

---

## 7. Justificación de la Arquitectura

### 7.1 ¿Por qué DDD?

1. **Complejidad del dominio financiero:**
   - Reglas de negocio complejas (clasificación, validaciones, cálculos)
   - Múltiples conceptos interrelacionados (usuarios, transacciones, insights)
   - Necesidad de lenguaje común entre desarrolladores y stakeholders

2. **Evolución del sistema:**
   - Arquitectura facilita agregar nuevos bancos (solo nuevo Parser)
   - Cambiar clasificadores (SimpleClassifier → MLClassifier)
   - Modificar proveedores externos sin afectar dominio

3. **Separación de responsabilidades:**
   - Cada bounded context evoluciona independientemente
   - Equipos pueden trabajar en paralelo

### 7.2 ¿Por qué Arquitectura Hexagonal?

1. **Testabilidad:**
   - Dominio testeable sin base de datos ni APIs externas
   - Ports permiten crear mocks fácilmente

2. **Independencia tecnológica:**
   - Cambiar de MySQL a PostgreSQL: solo cambiar adapters
   - Reemplazar Ollama: solo cambiar `OllamaService` adapter
   - Migrar de FastAPI a otro framework: solo cambiar API layer

3. **Mantenibilidad:**
   - Cambios en infraestructura no afectan lógica de negocio
   - Código del dominio es limpio y enfocado

### 7.3 ¿Por qué Bounded Contexts separados?

1. **Escalabilidad:**
   - Servicios pueden desplegarse independientemente
   - Escalar solo UploadService si hay mucha carga de archivos

2. **Desacoplamiento:**
   - Fallo en InsightService no afecta autenticación
   - Comunicación asíncrona mediante eventos

3. **Evolución independiente:**
   - Cambiar modelo de datos de insights sin tocar upload
   - Agregar OAuth providers sin afectar data service

---

## 8. Métricas de Calidad DDD

### 8.1 Checklist de Patrones Implementados

| Patrón | IdentifyService | UploadService | InsightService | DataService |
|--------|-----------------|---------------|----------------|-------------|
| Entities | Sí | Sí | Sí | Sí |
| Value Objects | Sí | Sí | Sí | Sí |
| Aggregates | Sí | Sí | Sí | Sí |
| Repositories | Sí | Sí | Sí | Sí |
| Domain Services | Sí | Sí | Sí | Parcial |
| Application Services | Sí | Sí | Sí | Sí |
| Ports (Interfaces) | Sí | Sí | Sí | Sí |
| Adapters | Sí | Sí | Sí | Sí |
| Bounded Context | Sí | Sí | Sí | Sí |
| Ubiquitous Language | Sí | Sí | Sí | Sí |
| Layered Architecture | Sí | Sí | Sí | Sí |
| DTOs | Sí | Sí | Sí | Sí |
| Mappers | Sí | Sí | Sí | Sí |
| Domain Events | Sí | Sí | Sí | No |
| Factory Pattern | Sí | Sí | Sí | No |

### 8.2 Fortalezas

1. **Consistencia arquitectónica:** Todos los servicios siguen los mismos principios
2. **Separación clara:** Capas bien definidas en todos los servicios
3. **Type safety:** Uso extensivo de Value Objects
4. **Testabilidad:** Arquitectura facilita testing unitario
5. **Documentación implícita:** Código auto-documentado con lenguaje ubicuo

### 8.3 Áreas de Mejora

1. **DataService:** Podría implementar Use Cases explícitos en lugar de lógica en routes
2. **Domain Events:** DataService no los implementa (es un servicio de lectura)
3. **Validaciones:** Algunas validaciones podrían moverse de Application a Domain
4. **Testing:** Agregar tests que demuestren los beneficios de la arquitectura

---

## 9. Conclusión

Los servicios de Flowlite Personal Finance demuestran una **implementación sólida y coherente de Domain-Driven Design y Arquitectura Hexagonal**.

**Principales logros:**

1. **Dominio protegido:** Lógica de negocio aislada de detalles técnicos
2. **Bounded Contexts claros:** Cada servicio tiene responsabilidad bien definida
3. **Lenguaje ubicuo:** Terminología del dominio consistente en código
4. **Ports & Adapters:** Inversión de dependencias correctamente aplicada
5. **Patrones tácticos:** Entities, Value Objects, Repositories, Aggregates bien usados
6. **Event-driven:** Comunicación asíncrona entre contextos
7. **Tecnología agnóstica:** Fácil cambiar implementaciones sin afectar dominio

**Impacto:**

- **Mantenibilidad:** Código fácil de entender y modificar
- **Escalabilidad:** Servicios independientes y escalables
- **Testabilidad:** Arquitectura facilita pruebas automatizadas
- **Evolución:** Sistema preparado para crecer y cambiar

Esta arquitectura posiciona a Flowlite como un **sistema robusto, profesional y preparado para el futuro**.

---

## Referencias Rápidas

### Estructura de Directorios DDD

```
<servicio>/src/
├── domain/                    # CORE - Lógica de negocio
│   ├── entities/             # Entidades con identidad
│   ├── valueobjects/         # Objetos inmutables (Java)
│   ├── value_objects.py      # Objetos inmutables (Python)
│   ├── repositories/         # Interfaces de repositorios
│   └── ports/                # Interfaces para servicios externos
│
├── application/              # Orquestación
│   ├── services/             # Casos de uso (Java)
│   ├── use_cases/            # Casos de uso (Python)
│   ├── dto/                  # Data Transfer Objects
│   └── ports/                # Interfaces de aplicación
│
├── infrastructure/           # Detalles técnicos
│   ├── persistence/          # Repositorios JPA/SQLAlchemy
│   ├── repositories/         # Implementaciones de repositorios
│   ├── messaging/            # RabbitMQ
│   ├── clients/              # HTTP clients externos
│   └── parsers/              # Parsers de archivos
│
└── api/ o interfaces/        # Puntos de entrada
    ├── routes/               # FastAPI routes
    ├── controllers/          # Spring controllers
    └── dependencies/         # Dependency injection
```

### Flujo de Dependencias

```
API/Controllers
    ↓ usa
Application Services (Use Cases)
    ↓ usa
Domain (Entities, Value Objects, Ports)
    ↑ implementado por
Infrastructure (Adapters)

