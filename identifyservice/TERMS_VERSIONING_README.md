# Sistema de Versioning de Términos y Condiciones - Flowlite

## 📋 Resumen

Esta implementación proporciona un sistema completo de versioning y gestión de Términos y Condiciones (Terms of Service) y Políticas de Privacidad (Privacy Policy) para Flowlite, cumpliendo con requisitos legales como GDPR, CCPA, y regulaciones colombianas de protección de datos.

## 🎯 Características Principales

### 1. **Versioning Completo**
- Múltiples versiones de términos con historial completo
- Versionado semántico con formato: `v{major}.{minor}_{YYYY-MM-DD}`
- Estados del ciclo de vida: DRAFT → ACTIVE → SUPERSEDED → ARCHIVED
- Tracking de cambios y resúmenes de modificaciones

### 2. **Control de Aceptación**
- Registro detallado de cada aceptación de usuario
- Información de auditoría (IP, User Agent, timestamp, ubicación)
- Tipos de aceptación: INITIAL_SIGNUP, FORCED_UPDATE, OPTIONAL_UPDATE, REACTIVATION
- Verificación de aceptaciones

### 3. **Cumplimiento Legal**
- Trazabilidad completa de qué versión aceptó cada usuario y cuándo
- Capacidad de forzar re-aceptación para cambios mayores
- Exportabilidad de registros para auditorías
- Retención de historial completo

### 4. **Flexibilidad**
- Soporte para múltiples tipos de documentos (ToS, Privacy Policy, etc.)
- Contenido embebido o por URL externa
- Fechas efectivas programables
- Gestión de cambios mayores vs menores

## 📁 Estructura de la Implementación

```
identifyservice/
├── src/main/java/com/flowlite/identifyservice/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── TermsVersion.java                 # Entidad de dominio para versiones
│   │   │   └── UserTermsAcceptance.java          # Entidad de dominio para aceptaciones
│   │   ├── repositories/
│   │   │   ├── TermsVersionRepository.java       # Repositorio de dominio
│   │   │   └── UserTermsAcceptanceRepository.java
│   │   └── valueobjects/
│   │       ├── TermsStatus.java                  # Estados: DRAFT, ACTIVE, etc.
│   │       └── AcceptanceType.java               # Tipos de aceptación
│   │
│   ├── application/
│   │   ├── dto/
│   │   │   ├── TermsVersionResponse.java         # Response DTO
│   │   │   ├── AcceptTermsRequest.java           # Request DTO
│   │   │   ├── TermsAcceptanceResponse.java
│   │   │   ├── TermsStatusResponse.java
│   │   │   ├── CreateTermsVersionRequest.java    # Admin DTO
│   │   │   └── TermsDtoMapper.java               # Mapper entidad ↔ DTO
│   │   └── services/
│   │       └── TermsService.java                 # Lógica de negocio
│   │
│   └── infrastructure/
│       ├── controllers/
│       │   └── TermsController.java              # REST API endpoints
│       └── persistence/
│           ├── entities/
│           │   ├── TermsVersionEntity.java       # Entidad JPA
│           │   └── UserTermsAcceptanceEntity.java
│           ├── repositories/
│           │   ├── JpaTermsVersionRepository.java
│           │   ├── JpaUserTermsAcceptanceRepository.java
│           │   ├── TermsVersionRepositoryJpaAdapter.java
│           │   └── UserTermsAcceptanceRepositoryJpaAdapter.java
│           └── mappers/
│               ├── TermsVersionMapper.java        # Mapper dominio ↔ JPA
│               └── UserTermsAcceptanceMapper.java
│
└── src/main/resources/db/
    └── terms_seed.sql                             # Seed de versiones iniciales
```

## 🗄️ Modelo de Datos

### Tabla: TermsVersion

```sql
CREATE TABLE TermsVersion (
    id BINARY(16) PRIMARY KEY,
    version_number VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(30) NOT NULL,                    -- TERMS_OF_SERVICE, PRIVACY_POLICY
    title VARCHAR(200) NOT NULL,
    content_text TEXT,                            -- Contenido completo
    content_url VARCHAR(500),                     -- URL alternativa
    change_summary TEXT,                          -- Resumen de cambios
    is_major_change BOOLEAN NOT NULL,
    requires_reacceptance BOOLEAN NOT NULL,
    status VARCHAR(20) NOT NULL,                  -- DRAFT, ACTIVE, SUPERSEDED, ARCHIVED
    effective_date DATETIME,
    created_at DATETIME NOT NULL,
    published_at DATETIME,
    superseded_at DATETIME,
    created_by VARCHAR(100),
    previous_version_id BINARY(16),               -- Referencia a versión anterior
    active BOOLEAN NOT NULL,

    INDEX idx_terms_version_number (version_number),
    INDEX idx_terms_type (type),
    INDEX idx_terms_status (status),
    INDEX idx_terms_active (active)
);
```

### Tabla: UserTermsAcceptance

```sql
CREATE TABLE UserTermsAcceptance (
    id BINARY(16) PRIMARY KEY,
    user_id BINARY(16) NOT NULL,
    terms_version_id BINARY(16) NOT NULL,
    accepted_at DATETIME NOT NULL,
    acceptance_type VARCHAR(30) NOT NULL,         -- INITIAL_SIGNUP, FORCED_UPDATE, etc.
    ip_address VARCHAR(45),                       -- IPv6 compatible
    user_agent VARCHAR(500),
    acceptance_method VARCHAR(30),                -- WEB, MOBILE_APP, API
    accepted_from_country VARCHAR(100),
    accepted_from_city VARCHAR(100),
    verified BOOLEAN NOT NULL,
    verified_at DATETIME,
    created_at DATETIME NOT NULL,
    active BOOLEAN NOT NULL,

    INDEX idx_user_terms_user_id (user_id),
    INDEX idx_user_terms_version_id (terms_version_id),
    INDEX idx_user_terms_accepted_at (accepted_at),
    INDEX idx_user_terms_active (active),
    INDEX idx_user_terms_user_version (user_id, terms_version_id)
);
```

## 🔌 API Endpoints

### Endpoints Públicos/Usuario

#### 1. Obtener Términos Actuales
```http
GET /terms/current?type=TERMS_OF_SERVICE
```

**Response:**
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "versionNumber": "v1.0_2025-01-15",
  "type": "TERMS_OF_SERVICE",
  "title": "Flowlite - Términos de Servicio",
  "contentText": "...",
  "contentUrl": "https://flowlite.com/terms/v1.0",
  "changeSummary": "Versión inicial",
  "isMajorChange": true,
  "requiresReacceptance": true,
  "status": "ACTIVE",
  "effectiveDate": "2025-01-15T00:00:00",
  "createdAt": "2025-01-15T00:00:00",
  "publishedAt": "2025-01-15T00:00:00",
  "active": true
}
```

#### 2. Aceptar Términos (Requiere JWT)
```http
POST /terms/accept
Authorization: Bearer {token}
Content-Type: application/json

{
  "termsVersionId": "11111111-1111-1111-1111-111111111111",
  "acceptedFromCountry": "Colombia",
  "acceptedFromCity": "Bogotá"
}
```

**Response:**
```json
{
  "message": "Terms accepted successfully",
  "acceptance": {
    "id": "...",
    "userId": "...",
    "termsVersionId": "...",
    "versionNumber": "v1.0_2025-01-15",
    "acceptanceType": "INITIAL_SIGNUP",
    "acceptedAt": "2025-01-15T10:30:00",
    "ipAddress": "192.168.***.***",
    "acceptanceMethod": "WEB",
    "acceptedFromCountry": "Colombia",
    "verified": false,
    "active": true
  }
}
```

#### 3. Verificar Estado de Términos del Usuario (Requiere JWT)
```http
GET /terms/status?type=TERMS_OF_SERVICE
Authorization: Bearer {token}
```

**Response:**
```json
{
  "userId": "...",
  "currentTermsVersionId": "...",
  "currentVersionNumber": "v1.0_2025-01-15",
  "acceptedTermsVersionId": null,
  "acceptedVersionNumber": null,
  "needsAcceptance": true,
  "requiresReacceptance": true,
  "isMajorChange": true,
  "acceptedAt": null,
  "changeSummary": "Versión inicial de Términos de Servicio",
  "message": "You need to accept the latest terms and conditions"
}
```

#### 4. Obtener Historial de Aceptaciones (Requiere JWT)
```http
GET /terms/acceptance/history
Authorization: Bearer {token}
```

#### 5. Obtener Versión Específica
```http
GET /terms/{versionId}
```

#### 6. Obtener Historial de Versiones
```http
GET /terms/history?type=TERMS_OF_SERVICE
```

### Endpoints de Administración

#### 7. Crear Nueva Versión (Admin)
```http
POST /terms/admin/create
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "versionNumber": "v2.0_2025-06-15",
  "type": "TERMS_OF_SERVICE",
  "title": "Flowlite - Términos de Servicio",
  "contentText": "...",
  "changeSummary": "Agregado sección de uso de datos de ML",
  "isMajorChange": true,
  "requiresReacceptance": true,
  "effectiveDate": "2025-06-15T00:00:00",
  "previousVersionId": "11111111-1111-1111-1111-111111111111",
  "createdBy": "admin@flowlite.com"
}
```

#### 8. Publicar Versión (Admin)
```http
POST /terms/admin/publish/{versionId}
Authorization: Bearer {admin_token}
```

#### 9. Obtener Estadísticas de Aceptación (Admin)
```http
GET /terms/admin/stats/{versionId}
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "termsVersionId": "...",
  "totalAcceptances": 1542
}
```

## 🔄 Flujos de Trabajo

### Flujo 1: Usuario Nuevo se Registra

1. Usuario completa registro
2. Frontend llama `GET /terms/status`
3. Backend responde `needsAcceptance: true`
4. Frontend muestra modal de términos
5. Usuario lee y acepta
6. Frontend llama `POST /terms/accept` con termsVersionId
7. Backend registra aceptación con tipo `INITIAL_SIGNUP`
8. Usuario puede continuar usando la app

### Flujo 2: Publicar Nueva Versión de Términos

1. Admin crea nueva versión: `POST /terms/admin/create` → Estado DRAFT
2. Admin revisa contenido
3. Admin publica: `POST /terms/admin/publish/{versionId}`
4. Backend:
   - Marca versión anterior como SUPERSEDED
   - Activa nueva versión
   - Establece `requiresReacceptance = true` si es cambio mayor

### Flujo 3: Usuario Existente con Términos Desactualizados

1. Usuario hace login
2. Backend/Middleware verifica: `GET /terms/status`
3. Si `needsAcceptance: true`:
   - Frontend muestra modal bloqueante o semi-bloqueante
   - Muestra `changeSummary` de nuevos términos
   - Botón "Ver cambios" (diff con versión anterior)
   - Botón "Aceptar nuevos términos"
4. Usuario acepta: `POST /terms/accept` con tipo `FORCED_UPDATE`
5. Usuario puede continuar

### Flujo 4: Auditoría y Compliance

1. Regulador solicita auditoría
2. Admin consulta:
   - `GET /terms/history` → Todas las versiones
   - `GET /terms/admin/stats/{versionId}` → Cuántos aceptaron
3. Para usuario específico:
   - `GET /terms/acceptance/history` (con userId)
4. Se genera reporte con:
   - Qué versión aceptó cada usuario
   - Cuándo la aceptó
   - Desde dónde (IP, ubicación)
   - Historial completo de cambios

## 🚀 Inicialización

### 1. Crear Tablas (Hibernate lo hace automáticamente)

Las entidades JPA crearán las tablas automáticamente al iniciar el servicio si `spring.jpa.hibernate.ddl-auto` está configurado adecuadamente.

### 2. Cargar Términos Iniciales

```bash
# Ejecutar seed script
mysql -u identifyservice_user -p identifyservice < identifyservice/src/main/resources/db/terms_seed.sql
```

O, alternativamente, crear mediante API:

```bash
# Crear Terms of Service v1.0
curl -X POST http://localhost:8081/terms/admin/create \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "versionNumber": "v1.0_2025-01-15",
    "type": "TERMS_OF_SERVICE",
    "title": "Flowlite - Términos de Servicio",
    "contentText": "...",
    "isMajorChange": true,
    "requiresReacceptance": true,
    "createdBy": "system"
  }'

# Publicar versión
curl -X POST http://localhost:8081/terms/admin/publish/{versionId} \
  -H "Authorization: Bearer {admin_token}"
```

## 🔒 Consideraciones de Seguridad

### 1. **Endpoints Protegidos**
- Todos los endpoints de aceptación requieren JWT válido
- Endpoints de administración requieren rol ADMIN (implementar)
- No se permite aceptar términos en nombre de otro usuario

### 2. **Auditoría**
- Toda aceptación registra IP y User Agent
- Timestamps inmutables (no se pueden modificar)
- Soft deletes (active flag) para mantener historial

### 3. **Validaciones**
- No se puede aceptar versión no ACTIVE
- No se puede publicar versión que no existe
- No se puede tener dos versiones ACTIVE del mismo tipo simultáneamente

## 📊 Casos de Uso Avanzados

### 1. Comparar Versiones (Frontend)

```javascript
// Frontend obtiene dos versiones
const currentVersion = await fetch('/terms/current?type=TERMS_OF_SERVICE');
const userAcceptedVersion = await fetch(`/terms/${user.acceptedTermsVersionId}`);

// Muestra diff side-by-side
showDiff(userAcceptedVersion.contentText, currentVersion.contentText);
```

### 2. Notificación Proactiva

```javascript
// Cron job diario que detecta usuarios sin términos actualizados
const usersNeedingAcceptance = await termsService.getUsersNeedingAcceptance(latestVersionId);

for (const userId of usersNeedingAcceptance) {
  await notificationService.send(userId, {
    type: 'TERMS_UPDATE',
    message: 'Hemos actualizado nuestros términos. Por favor revísalos.',
    urgency: 'HIGH'
  });
}
```

### 3. Período de Gracia

```java
// En el servicio, verificar si usuario está en período de gracia
boolean isInGracePeriod(UUID userId, TermsVersion newVersion) {
    var acceptance = getUserLatestAcceptance(userId, newVersion.getType());

    if (acceptance.isEmpty()) return false;

    var daysSincePublished = ChronoUnit.DAYS.between(
        newVersion.getPublishedAt(),
        LocalDateTime.now()
    );

    return daysSincePublished <= 30; // 30 días de gracia
}
```

## 🧪 Testing

### Test de Aceptación
```java
@Test
void userShouldAcceptTermsSuccessfully() {
    // Given
    var user = createTestUser();
    var terms = createAndPublishTerms("v1.0");

    // When
    var acceptance = termsService.acceptTerms(
        user.getId(),
        terms.getId(),
        AcceptanceType.INITIAL_SIGNUP,
        "192.168.1.1",
        "Mozilla/5.0",
        "WEB",
        "Colombia",
        "Bogotá"
    );

    // Then
    assertNotNull(acceptance);
    assertEquals(user.getId(), acceptance.getUserId());
    assertTrue(acceptance.isActive());
}
```

## 📝 Mejoras Futuras

1. **Diff Automático**: Generar diff automático entre versiones
2. **Traducciones**: Soporte multiidioma
3. **Firma Digital**: Agregar hash criptográfico de cada aceptación
4. **Exportación**: Endpoint para exportar aceptación como PDF firmado
5. **Workflow de Aprobación**: Proceso de revisión antes de publicar
6. **Notificaciones**: Integración con servicio de notificaciones
7. **Analytics**: Dashboard de adopción de términos

## 🔗 Referencias

- [GDPR](https://gdpr.eu/)
- [Ley 1581 de 2012 (Colombia)](https://www.sic.gov.co/tema/proteccion-de-datos-personales)
- [CCPA](https://oag.ca.gov/privacy/ccpa)

## 👤 Autor

Implementado para Flowlite Personal Finance
Fecha: Enero 2025
