# 🚀 Guía de Inicio Rápido - UploadService

## Prerrequisitos

Antes de iniciar el UploadService, asegúrate de tener:

1. **Python 3.11+** instalado
2. **InfrastructureService** corriendo con:
   - MySQL en puerto 3306
   - RabbitMQ en puerto 5672
3. **IdentityService** corriendo en puerto 8000

## Inicio Rápido

### 1. Verificar servicios externos

Asegúrate que los siguientes servicios estén corriendo:

```bash
# Verificar InfrastructureService
docker ps

# Deberías ver:
# - MySQL (puerto 3306)
# - Redis (puerto 6379)
# - RabbitMQ (puertos 5672, 15672)
```

### 2. Iniciar UploadService

```bash
cd uploadservice
./start.sh
```

El script automáticamente:
- ✅ Verifica el archivo `.env`
- ✅ Crea/activa el entorno virtual
- ✅ Instala las dependencias desde `requirements.txt`
- ✅ Carga las variables de entorno
- ✅ Inicia el servidor en `http://localhost:8001`

### 3. Verificar que está funcionando

Abre tu navegador en:
- **Health Check**: http://localhost:8001/health
- **API Docs**: http://localhost:8001/docs
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## Configuración

El archivo `.env` contiene todas las configuraciones necesarias:

```bash
# Base de datos compartida
DATABASE_URL=mysql+aiomysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# IdentityService para validación de tokens
IDENTITY_SERVICE_URL=http://localhost:8000
IDENTITY_SERVICE_TIMEOUT=5.0

# RabbitMQ para mensajería asíncrona
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE_NAME=batch_processed

# Configuración del servidor
HOST=0.0.0.0
PORT=8001

# CORS (opcional)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Clasificador ML (opcional)
# USE_SIMPLE_CLASSIFIER=false  # true para usar clasificador simple en lugar de ML
# ML_MODELS_PATH=/path/to/models  # Ruta personalizada a archivos de modelo
```

## Clasificador de Transacciones con ML

El UploadService incluye un clasificador de transacciones basado en Machine Learning con **99.7% de precisión**.

### Características del Modelo

- **Algoritmo**: Logistic Regression con TF-IDF vectorization
- **Precisión**: 99.7% en conjunto de test
- **Confianza promedio**: 96.8%
- **Features**: Descripción de transacción + tipo (ingreso/egreso)
- **Entrenamiento**: +5,000 transacciones reales de bancos colombianos

### Archivos del Modelo

El clasificador requiere 4 archivos en `uploadservice/models/`:

```
models/
├── classifier.pkl       # Modelo Logistic Regression entrenado
├── vectorizer.pkl       # TF-IDF vectorizer
├── label_encoder.pkl    # Encoder para tipo de transacción
└── metadata.json        # Metadatos del modelo (accuracy, fecha, etc)
```

**Nota**: Estos archivos ya están incluidos en el repositorio. Si no los tienes, cópialos desde `ml_pipeline/models/final/`.

### Configuración

#### Usar ML Classifier (por defecto)

El clasificador ML está activado por defecto. No requiere configuración adicional:

```bash
# No es necesario configurar nada - usa ML por defecto
python -m uvicorn src.main:app --reload
```

#### Usar Simple Classifier (testing/desarrollo)

Para usar el clasificador simple (retorna "Other" para todas las transacciones):

```bash
# En .env o como variable de entorno
USE_SIMPLE_CLASSIFIER=true

# O al iniciar el servicio
USE_SIMPLE_CLASSIFIER=true python -m uvicorn src.main:app --reload
```

#### Ruta personalizada de modelos

Si tus modelos están en otra ubicación:

```bash
# En .env o como variable de entorno
ML_MODELS_PATH=/custom/path/to/models
```

### Categorías Soportadas

El modelo clasifica transacciones en las siguientes categorías:

- Alimentación
- Transporte
- Entretenimiento
- Salud
- Educación
- Servicios Públicos
- Compras
- Retiros de Efectivo
- Transferencias
- Salarios/Ingresos
- Otros Ingresos
- Other (fallback)

### Rendimiento

- **Lazy Loading**: Los modelos se cargan solo en la primera clasificación
- **Singleton Pattern**: Una única carga en memoria para todas las peticiones
- **Procesamiento rápido**: ~2-5ms por transacción
- **Memory footprint**: ~130KB (todos los archivos de modelo)

### Testing

Ejecuta los tests del clasificador:

```bash
# Tests unitarios del clasificador
pytest tests/test_ml_classifier.py -v

# Tests con output detallado
pytest tests/test_ml_classifier.py -v -s

# Test específico
pytest tests/test_ml_classifier.py::TestMLClassifier::test_classify_basic_transaction -v
```

### Logging

El clasificador incluye logging detallado:

```python
# Logs que verás
INFO - Using MLClassifier (ML-based classification)
INFO - Loading ML models from: /path/to/models
INFO - Model loaded successfully: Logistic Regression with TF-IDF + Transaction Type (Accuracy: 99.71%)
DEBUG - Classified 'COMPRA STARBUCKS...' as 'Alimentación' (confidence: 98.5%, type: egreso)
```

### Actualizar el Modelo

Para actualizar a una nueva versión del modelo:

1. Entrena un nuevo modelo en `ml_pipeline/`
2. Copia los nuevos archivos `.pkl` y `metadata.json` a `uploadservice/models/`
3. Reinicia el servicio (el modelo se recargará automáticamente)

```bash
# Desde ml_pipeline
python run_pipeline.py

# Copiar modelos actualizados
cp ml_pipeline/models/final/*.pkl uploadservice/models/
cp ml_pipeline/models/final/metadata.json uploadservice/models/

# Reiniciar servicio
./kill.sh && ./start.sh
```

## Uso

### 1. Obtener un token JWT

Primero, registra un usuario y obtén un token desde IdentityService:

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "usuario",
    "password": "Password123!"
  }'

# Login para obtener token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "usuario",
    "password": "Password123!"
  }'
```

### 2. Subir un archivo de transacciones

```bash
# Reemplaza <your-token> con el token obtenido en el paso anterior
curl -X POST "http://localhost:8001/api/v1/transactions/upload?bank_code=BANCOLOMBIA" \
  -H "Authorization: Bearer <your-token>" \
  -F "files=@/ruta/a/tu/archivo.xlsx"
```

### 3. Consultar estado del lote

```bash
curl -X GET "http://localhost:8001/api/v1/transactions/batch/<batch-id>" \
  -H "Authorization: Bearer <your-token>"
```

## Arquitectura

El UploadService implementa arquitectura hexagonal:

```
uploadservice/
├── src/
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── domain/                    # Entidades del dominio
│   │   ├── entities/              # Transaction, Bank, Category, Batch
│   │   └── ports/                 # Interfaces (Repositories, Parsers)
│   ├── application/               # Casos de uso
│   │   ├── use_cases/             # ProcessFilesUseCase, ConsultarEstadoLote
│   │   └── dto/                   # Data Transfer Objects
│   ├── infrastructure/            # Implementaciones
│   │   ├── repositories/          # MySQL repositories
│   │   ├── parsers/               # Excel parsers (Bancolombia, etc)
│   │   ├── clasificador/          # Transaction classifier
│   │   └── database/              # Database models & connection
│   └── api/                       # API REST
│       ├── routes/                # Endpoints
│       └── dependencies/          # Dependency injection
```

## Bancos Soportados

Actualmente soporta parsing de archivos Excel para:

- **Bancolombia**: Formato estándar de extracto bancario
- Fácilmente extensible para otros bancos

## Procesamiento Asíncrono

1. El archivo se sube y se crea un lote con estado `PENDING`
2. Las transacciones se procesan y se guardan en la base de datos
3. Se envía un mensaje a RabbitMQ cuando el procesamiento termina
4. El InsightService consume el mensaje para generar análisis

## Solución de Problemas

### Error: "Cannot connect to MySQL"
```bash
# Verificar que MySQL está corriendo
docker ps | grep mysql

# Verificar credenciales en .env
cat .env | grep DATABASE_URL
```

### Error: "Cannot validate token"
```bash
# Verificar que IdentityService está corriendo
curl http://localhost:8000/health

# Verificar URL en .env
cat .env | grep IDENTITY_SERVICE_URL
```

### Error: "Cannot connect to RabbitMQ"
```bash
# Verificar que RabbitMQ está corriendo
docker ps | grep rabbitmq

# Verificar credenciales en .env
cat .env | grep RABBITMQ
```

## Detener el Servicio

### Opción 1: Usar el script kill.sh (Recomendado)

```bash
./kill.sh
```

### Opción 2: Manualmente

Presiona `Ctrl+C` en la terminal donde está corriendo el servicio.

## Logs

Los logs se muestran en la consola con información sobre:
- Requests HTTP entrantes
- Procesamiento de archivos
- Validación de tokens
- Conexiones a base de datos
- Mensajes RabbitMQ

## Base de Datos Compartida

Este servicio usa la base de datos `flowlite_db` compartida con IdentityService:

- **Tabla User**: Gestionada por IdentityService
- **Tablas Bank, Category, Transaction, TransactionBatch**: Gestionadas por UploadService

La tabla Transaction tiene `id_user` que referencia a la tabla User, pero sin constraint FK para permitir independencia entre servicios.

## API Endpoints

### Health Check
```
GET /health
```

### Upload Transactions
```
POST /api/v1/transactions/upload?bank_code=BANCOLOMBIA
Headers: Authorization: Bearer <token>
Body: multipart/form-data con archivo(s) Excel
Response: 202 Accepted con batch_id
```

### Get Batch Status
```
GET /api/v1/transactions/batch/{batch_id}
Headers: Authorization: Bearer <token>
Response: Información del lote y sus transacciones
```

### Test Endpoint (solo desarrollo)
```
GET /api/v1/test/protected
Headers: Authorization: Bearer <token>
Response: Información del usuario autenticado
```

---

Para más información, consulta:
- **README.md**: Documentación completa del servicio
- **API Docs**: http://localhost:8001/docs (cuando el servicio está corriendo)
