# Diagrama UML - Upload Service

## Arquitectura General del Sistema

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI Routes]
        Auth[Authentication]
    end

    subgraph "Application Layer"
        UC1[ProcesarArchivosUseCase]
        UC2[ConsultarEstadoLoteUseCase]
        DTO[DTOs]
    end

    subgraph "Domain Layer"
        E1[Entities]
        P1[Ports/Interfaces]
    end

    subgraph "Infrastructure Layer"
        R1[MySQL Repositories]
        P2[Excel Parsers]
        C1[Clasificador]
        DB[(MySQL Database)]
    end

    API --> UC1
    API --> UC2
    API --> Auth
    UC1 --> P1
    UC2 --> P1
    UC1 --> E1
    UC2 --> E1
    P1 -.implements.- R1
    P1 -.implements.- P2
    P1 -.implements.- C1
    R1 --> DB
```

## Diagrama de Clases - Capa de Dominio

```mermaid
classDiagram
    class Banco {
        +Optional~int~ id
        +str nombre
        +str codigo
        +Optional~datetime~ created_at
        +Optional~datetime~ updated_at
    }

    class Categoria {
        +Optional~int~ id
        +str nombre
        +Optional~str~ descripcion
        +Optional~datetime~ created_at
        +Optional~datetime~ updated_at
    }

    class Transaccion {
        +Optional~int~ id
        +int usuario_id
        +int banco_id
        +int categoria_id
        +int lote_id
        +datetime fecha
        +str descripcion
        +Optional~str~ referencia
        +Decimal valor
        +Optional~datetime~ created_at
        +Optional~datetime~ updated_at
    }

    class LoteTransaccion {
        +Optional~int~ id
        +int usuario_id
        +int banco_id
        +EstadoLote estado
        +int total_registros
        +int registros_procesados
        +Optional~datetime~ created_at
        +Optional~datetime~ updated_at
        +porcentaje_procesado() float
    }

    class EstadoLote {
        <<enumeration>>
        PENDIENTE
        PROCESANDO
        COMPLETADO
        ERROR
    }

    Transaccion --> Banco : banco_id
    Transaccion --> Categoria : categoria_id
    Transaccion --> LoteTransaccion : lote_id
    LoteTransaccion --> Banco : banco_id
    LoteTransaccion --> EstadoLote : estado
```

## Diagrama de Clases - Puertos (Interfaces)

```mermaid
classDiagram
    class TransaccionRepositoryPort {
        <<interface>>
        +save_batch(transacciones: List~Transaccion~)* List~Transaccion~
        +get_by_id(id: int)* Optional~Transaccion~
    }

    class BancoRepositoryPort {
        <<interface>>
        +get_by_codigo(codigo: str)* Optional~Banco~
        +save(banco: Banco)* Banco
        +get_by_id(id: int)* Optional~Banco~
    }

    class CategoriaRepositoryPort {
        <<interface>>
        +get_by_nombre(nombre: str)* Optional~Categoria~
        +save(categoria: Categoria)* Categoria
        +get_by_id(id: int)* Optional~Categoria~
    }

    class LoteTransaccionRepositoryPort {
        <<interface>>
        +save(lote: LoteTransaccion)* LoteTransaccion
        +get_by_id(id: int)* Optional~LoteTransaccion~
        +update(lote: LoteTransaccion)* LoteTransaccion
    }

    class UsuarioRepositoryPort {
        <<interface>>
        +get_by_id(id: int)* bool
    }

    class ExcelParserPort {
        <<interface>>
        +parse(file_content: bytes)* List~TransaccionRaw~
        +get_banco_codigo()* str
    }

    class ClasificadorPort {
        <<interface>>
        +clasificar(descripcion: str)* str
    }

    class TransaccionRaw {
        +datetime fecha
        +str descripcion
        +str referencia
        +Decimal valor
    }

    ExcelParserPort ..> TransaccionRaw : returns
```

## Diagrama de Clases - Implementaciones de Infraestructura

```mermaid
classDiagram
    class MySQLBancoRepository {
        -AsyncSession session
        +get_by_codigo(codigo: str) Optional~Banco~
        +save(banco: Banco) Banco
        +get_by_id(id: int) Optional~Banco~
        -_to_model(entity: Banco) BancoModel
        -_to_entity(model: BancoModel) Banco
    }

    class BancolombiaParser {
        +str BANCO_CODIGO
        +parse(file_content: bytes) List~TransaccionRaw~
        +get_banco_codigo() str
    }

    class ParserFactory {
        -dict _parsers
        +get_parser(banco_codigo: str)$ ExcelParserPort
        +get_supported_banks()$ list
    }

    class ClasificadorSimple {
        +clasificar(descripcion: str) str
    }

    class BancoRepositoryPort {
        <<interface>>
    }

    class ExcelParserPort {
        <<interface>>
    }

    class ClasificadorPort {
        <<interface>>
    }

    MySQLBancoRepository ..|> BancoRepositoryPort
    BancolombiaParser ..|> ExcelParserPort
    ClasificadorSimple ..|> ClasificadorPort
    ParserFactory ..> ExcelParserPort : creates
    ParserFactory ..> BancolombiaParser : creates
```

## Diagrama de Clases - Casos de Uso

```mermaid
classDiagram
    class ProcesarArchivosUseCase {
        -TransaccionRepositoryPort transaccion_repo
        -BancoRepositoryPort banco_repo
        -CategoriaRepositoryPort categoria_repo
        -LoteTransaccionRepositoryPort lote_repo
        -ClasificadorPort clasificador
        -sessionmaker session_factory
        +execute(archivos_content, parser, usuario_id) int
        -_procesar_transacciones_async(transacciones_raw, lote, usuario_id, banco_id)
    }

    class ConsultarEstadoLoteUseCase {
        -LoteTransaccionRepositoryPort lote_repo
        +execute(lote_id: int) Optional~LoteStatusDTO~
    }

    class LoteStatusDTO {
        +int lote_id
        +str estado
        +int total_registros
        +int registros_procesados
        +float porcentaje_procesado
        +datetime created_at
        +datetime updated_at
    }

    class TransaccionRepositoryPort {
        <<interface>>
    }

    class BancoRepositoryPort {
        <<interface>>
    }

    class CategoriaRepositoryPort {
        <<interface>>
    }

    class LoteTransaccionRepositoryPort {
        <<interface>>
    }

    class ClasificadorPort {
        <<interface>>
    }

    class ExcelParserPort {
        <<interface>>
    }

    ProcesarArchivosUseCase --> TransaccionRepositoryPort
    ProcesarArchivosUseCase --> BancoRepositoryPort
    ProcesarArchivosUseCase --> CategoriaRepositoryPort
    ProcesarArchivosUseCase --> LoteTransaccionRepositoryPort
    ProcesarArchivosUseCase --> ClasificadorPort
    ProcesarArchivosUseCase --> ExcelParserPort

    ConsultarEstadoLoteUseCase --> LoteTransaccionRepositoryPort
    ConsultarEstadoLoteUseCase ..> LoteStatusDTO : returns
```

## Diagrama de Secuencia - Upload de Archivos

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI Router
    participant Auth as Authentication
    participant UC as ProcesarArchivosUseCase
    participant Parser as ExcelParser
    participant BRepo as BancoRepository
    participant LRepo as LoteRepository
    participant Task as Background Task
    participant TRepo as TransaccionRepository
    participant CRepo as CategoriaRepository
    participant Clasif as Clasificador

    User->>API: POST /api/v1/transacciones/upload
    API->>Auth: validate token
    Auth-->>API: usuario_id

    API->>Parser: ParserFactory.get_parser(banco_codigo)
    Parser-->>API: parser instance

    API->>UC: execute(archivos_content, parser, usuario_id)

    UC->>Parser: parse(file_content)
    Parser-->>UC: List[TransaccionRaw]

    UC->>BRepo: get_by_codigo(banco_codigo)
    BRepo-->>UC: Banco

    UC->>LRepo: save(lote)
    LRepo-->>UC: LoteTransaccion (id)

    UC->>Task: create_task(_procesar_transacciones_async)
    UC-->>API: lote_id
    API-->>User: 202 Accepted {lote_id}

    Note over Task: Procesamiento asíncrono

    loop Para cada batch de 500
        Task->>Clasif: clasificar(descripcion)
        Clasif-->>Task: nombre_categoria

        Task->>CRepo: get_by_nombre(nombre_categoria)
        CRepo-->>Task: Categoria

        Task->>TRepo: save_batch(transacciones)
        TRepo-->>Task: List[Transaccion]

        Task->>LRepo: update(lote)
    end

    Task->>LRepo: update(lote) - COMPLETADO
```

## Diagrama de Secuencia - Consultar Estado de Lote

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI Router
    participant Auth as Authentication
    participant UC as ConsultarEstadoLoteUseCase
    participant LRepo as LoteRepository

    User->>API: GET /api/v1/transacciones/lote/{lote_id}
    API->>Auth: validate token
    Auth-->>API: usuario_id

    API->>UC: execute(lote_id)
    UC->>LRepo: get_by_id(lote_id)
    LRepo-->>UC: LoteTransaccion

    UC-->>API: LoteStatusDTO

    API->>LRepo: get_by_id(lote_id)
    LRepo-->>API: LoteTransaccion

    alt usuario_id matches
        API-->>User: 200 OK {LoteStatusDTO}
    else usuario_id mismatch
        API-->>User: 403 Forbidden
    end
```

## Diagrama de Componentes

```mermaid
graph TB
    subgraph Client
        C[Cliente HTTP]
    end

    subgraph "FastAPI Application"
        subgraph "API Routes"
            R1[/api/v1/transacciones/upload]
            R2[/api/v1/transacciones/lote/:id]
            R3[/health]
        end

        subgraph "Dependencies"
            D1[Auth Dependencies]
            D2[Service Dependencies]
        end

        subgraph "Application Layer"
            UC1[ProcesarArchivosUseCase]
            UC2[ConsultarEstadoLoteUseCase]
        end

        subgraph "Domain Layer"
            DOM[Entities & Ports]
        end

        subgraph "Infrastructure"
            REPO[MySQL Repositories]
            PARSE[Excel Parsers]
            CLAS[Clasificador]
        end
    end

    subgraph "External"
        DB[(MySQL Database)]
    end

    C -->|HTTP| R1
    C -->|HTTP| R2
    C -->|HTTP| R3

    R1 --> D1
    R1 --> D2
    R2 --> D1
    R2 --> D2

    R1 --> UC1
    R2 --> UC2

    UC1 --> DOM
    UC2 --> DOM

    DOM -.-> REPO
    DOM -.-> PARSE
    DOM -.-> CLAS

    REPO --> DB
```

## Modelo de Datos (Entidad-Relación)

```mermaid
erDiagram
    USUARIOS ||--o{ TRANSACCIONES : "tiene"
    USUARIOS ||--o{ LOTES_TRANSACCION : "crea"
    BANCOS ||--o{ TRANSACCIONES : "procesa"
    BANCOS ||--o{ LOTES_TRANSACCION : "asociado"
    CATEGORIAS ||--o{ TRANSACCIONES : "clasifica"
    LOTES_TRANSACCION ||--o{ TRANSACCIONES : "contiene"

    USUARIOS {
        int id PK
        string email UK
        string nombre
        string apellido
        string password_hash
        boolean activo
        datetime created_at
        datetime updated_at
    }

    BANCOS {
        int id PK
        string nombre
        string codigo UK
        datetime created_at
        datetime updated_at
    }

    CATEGORIAS {
        int id PK
        string nombre UK
        text descripcion
        datetime created_at
        datetime updated_at
    }

    LOTES_TRANSACCION {
        int id PK
        int usuario_id FK
        int banco_id FK
        enum estado
        int total_registros
        int registros_procesados
        datetime created_at
        datetime updated_at
    }

    TRANSACCIONES {
        int id PK
        int usuario_id FK
        int banco_id FK
        int categoria_id FK
        int lote_id FK
        datetime fecha
        text descripcion
        string referencia
        decimal valor
        datetime created_at
        datetime updated_at
    }
```

## Patrones de Diseño Utilizados

### 1. Arquitectura Hexagonal (Ports & Adapters)
- **Puertos**: Interfaces en `domain/ports/`
- **Adaptadores**: Implementaciones en `infrastructure/`
- **Dominio**: Entidades en `domain/entities/`

### 2. Factory Pattern
- `ParserFactory`: Crea parsers según el código del banco

### 3. Repository Pattern
- Abstracción de acceso a datos mediante puertos
- Implementaciones específicas para MySQL

### 4. Use Case Pattern
- Casos de uso encapsulan la lógica de negocio
- `ProcesarArchivosUseCase`
- `ConsultarEstadoLoteUseCase`

### 5. Dependency Injection
- FastAPI dependencies para inyectar repositorios y servicios

### 6. DTO Pattern
- `LoteStatusDTO`: Transferencia de datos entre capas

## Notas de Arquitectura

1. **Separación de Responsabilidades**: El proyecto sigue una arquitectura hexagonal clara con separación entre dominio, aplicación e infraestructura.

2. **Inversión de Dependencias**: La capa de dominio define los puertos (interfaces) que son implementados por la capa de infraestructura.

3. **Extensibilidad**: El uso de Factory Pattern permite agregar fácilmente nuevos bancos sin modificar el código existente.

4. **Procesamiento Asíncrono**: Las transacciones se procesan en background usando asyncio.create_task, permitiendo respuestas rápidas al usuario.

5. **Procesamiento por Lotes**: Las transacciones se guardan en batches de 500 para optimizar el rendimiento.

6. **Clasificación**: Actualmente usa un clasificador simple que retorna "Otro", pero está diseñado para integrar un modelo de ML en el futuro.
