# Servicio de Transacciones Bancarias

Servicio FastAPI para procesar y clasificar transacciones bancarias desde archivos Excel utilizando arquitectura hexagonal.

## Características

- Procesamiento de archivos Excel con transacciones bancarias
- Clasificación automática de transacciones (preparado para integración con modelo ML)
- Procesamiento por lotes asíncrono
- Autenticación mediante JWT (OAuth 2.0)
- Arquitectura hexagonal para alta mantenibilidad y escalabilidad
- Soporte extensible para múltiples bancos

## Arquitectura

El proyecto sigue los principios de arquitectura hexagonal (puertos y adaptadores):

```
src/
├── domain/              # Capa de dominio (lógica de negocio)
│   ├── entities/        # Entidades del dominio
│   └── ports/           # Interfaces (puertos)
├── application/         # Capa de aplicación (casos de uso)
│   ├── use_cases/       # Casos de uso
│   └── dto/             # Data Transfer Objects
├── infrastructure/      # Capa de infraestructura (adaptadores)
│   ├── database/        # Modelos y conexión a BD
│   ├── repositories/    # Implementación de repositorios
│   ├── parsers/         # Parsers de archivos Excel
│   └── clasificador/    # Clasificador de transacciones
└── api/                 # Capa de presentación (API REST)
    ├── routes/          # Endpoints
    └── dependencies/    # Dependencias de FastAPI
```

## Modelos de Base de Datos

- **usuarios**: Usuarios del sistema (incluye usuarios de prueba para testing)
- **bancos**: Información de los bancos
- **categorias**: Categorías de transacciones
- **lotes_transaccion**: Lotes de procesamiento
- **transacciones**: Transacciones individuales normalizadas

## Requisitos

- Python 3.11+
- MySQL 8.0+
- Docker y Docker Compose (opcional)

## Instalación

### Opción 1: Instalación Local

1. Clonar el repositorio
```bash
git clone https://github.com/Pliperkiller/Flowlite-Personal-Finance.git
cd Flowlite-Personal-Finance
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Crear la base de datos
```bash
mysql -u root -p
CREATE DATABASE transactions_db;
```

6. Inicializar las tablas y datos de prueba
```bash
python -m scripts.init_db
```

Esto creará:
- Las tablas en la base de datos
- Usuarios de prueba
- Bancos iniciales
- Categorías predefinidas

### Opción 2: Docker Compose

```bash
docker-compose up -d
```

Esto levantará:
- MySQL en el puerto 3306
- API en el puerto 8000

## Ejecución

### Local
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker-compose up
```

La API estará disponible en `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

## Usuarios de Prueba

El script de inicialización crea los siguientes usuarios de prueba:

| Email | Password | Nombre | User ID |
|-------|----------|--------|---------|
| test1@example.com | password123 | Juan Pérez | 1 |
| test2@example.com | password123 | María González | 2 |
| test3@example.com | password123 | Carlos Rodríguez | 3 |
| admin@example.com | admin123 | Admin Sistema | 4 |

### Generar Tokens JWT de Prueba

Para generar tokens JWT para estos usuarios:

```bash
python scripts/generate_test_tokens.py
```

Este script generará tokens válidos por 30 días para cada usuario de prueba. Copia el token y úsalo en el header `Authorization: Bearer <token>` de tus requests.

**Ejemplo de uso:**
```bash
# Generar tokens
python scripts/generate_test_tokens.py

# Usar el token en una request
curl -X GET "http://localhost:8000/api/v1/test/user-id" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Endpoints

### 1. Health Check
```http
GET /api/v1/health
```
Verifica el estado del servicio y la base de datos.

**Respuesta:**
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

### 2. Cargar Archivos de Transacciones
```http
POST /api/v1/transacciones/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Parámetros:**
- `banco_codigo`: Código del banco (ej: BANCOLOMBIA)
- `archivos`: Lista de archivos Excel

**Respuesta:**
```json
{
  "lote_id": 1,
  "message": "Procesamiento iniciado. Use el lote_id 1 para consultar el estado."
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCOLOMBIA" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "archivos=@MovimientosTusCuentasBancolombia07Oct2025.xlsx"
```

### 3. Consultar Estado del Lote
```http
GET /api/v1/transacciones/lote/{lote_id}
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "lote_id": 1,
  "estado": "procesando",
  "total_registros": 190,
  "registros_procesados": 95,
  "porcentaje_procesado": 50.0,
  "created_at": "2025-10-10T10:00:00",
  "updated_at": "2025-10-10T10:05:00"
}
```

### 4. Obtener User ID desde Token (Testing)
```http
GET /api/v1/test/user-id
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "user_id": 123,
  "message": "El token corresponde al usuario con ID 123"
}
```

## Formato de Archivos Excel

### Bancolombia
El archivo debe tener las siguientes columnas:
- **Fecha**: Fecha de la transacción
- **Descripción**: Descripción de la transacción
- **Referencia**: Referencia opcional
- **Valor**: Monto de la transacción

Ejemplo:
| Fecha      | Descripción           | Referencia | Valor      |
|------------|-----------------------|------------|------------|
| 2025-10-05 | TRANSF PEDRO PEREZ |            | 23.0    |
| 2025-09-26 | PAGO DE NOMI   | 1004057  | 123.0  |

## Agregar Soporte para Nuevos Bancos

Para agregar soporte para un nuevo banco:

1. Crear un nuevo parser en `src/infrastructure/parsers/`:

```python
# src/infrastructure/parsers/nuevo_banco_parser.py
from typing import List
import pandas as pd
from io import BytesIO
from decimal import Decimal
from ...domain.ports.excel_parser_port import ExcelParserPort, TransaccionRaw


class NuevoBancoParser(ExcelParserPort):
    BANCO_CODIGO = "NUEVO_BANCO"

    def parse(self, file_content: bytes) -> List[TransaccionRaw]:
        df = pd.read_excel(BytesIO(file_content))

        # Adaptar según el formato del nuevo banco
        transacciones = []
        for _, row in df.iterrows():
            transaccion = TransaccionRaw(
                fecha=pd.to_datetime(row["Fecha"]),
                descripcion=str(row["Descripcion"]),
                referencia=str(row["Ref"]) if pd.notna(row["Ref"]) else None,
                valor=Decimal(str(row["Monto"])),
            )
            transacciones.append(transaccion)

        return transacciones

    def get_banco_codigo(self) -> str:
        return self.BANCO_CODIGO
```

2. Registrar el parser en `ParserFactory`:

```python
# src/infrastructure/parsers/parser_factory.py
from .nuevo_banco_parser import NuevoBancoParser

class ParserFactory:
    _parsers = {
        "BANCOLOMBIA": BancolombiaParser,
        "NUEVO_BANCO": NuevoBancoParser,  # Agregar aquí
    }
```

3. Agregar el banco a la base de datos:

```python
banco = BancoModel(nombre="Nuevo Banco", codigo="NUEVO_BANCO")
```

## Configuración JWT

El servicio espera tokens JWT con el siguiente formato:

```json
{
  "sub": 123,  // user_id
  "exp": 1234567890,
  // otros claims...
}
```

Configurar `JWT_SECRET_KEY` y `JWT_ALGORITHM` en `.env` para que coincidan con el servicio de autenticación.

## Variables de Entorno

```bash
# Base de datos
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/transactions_db

# JWT (debe coincidir con el servicio de autenticación)
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Servidor
HOST=0.0.0.0
PORT=8000
```

## Procesamiento Asíncrono

Las transacciones se procesan en lotes de 500 registros de forma asíncrona. El usuario recibe inmediatamente un `lote_id` que puede usar para consultar el progreso.

Estados del lote:
- `pendiente`: Lote creado, esperando procesamiento
- `procesando`: Procesamiento en curso
- `completado`: Procesamiento completado exitosamente
- `error`: Error durante el procesamiento

## Clasificador de Transacciones

Actualmente, el clasificador retorna la categoría "Otro" para todas las transacciones. Para integrar un modelo de ML:

1. Implementar `ClasificadorPort` en `src/infrastructure/clasificador/`:

```python
class ClasificadorML(ClasificadorPort):
    def __init__(self, model_path: str):
        # Cargar modelo
        self.model = load_model(model_path)

    async def clasificar(self, descripcion: str) -> str:
        # Usar modelo para clasificar
        categoria = self.model.predict(descripcion)
        return categoria
```

2. Actualizar la dependencia en `src/api/dependencies/services.py`:

```python
def get_clasificador() -> ClasificadorPort:
    return ClasificadorML(model_path="path/to/model")
```

## Desarrollo

### Ejecutar tests
```bash
pytest tests/
```

### Linting
```bash
black src/
flake8 src/
```

## Notas Importantes

- El usuario solo puede cargar archivos de un mismo banco por request
- Los archivos se procesan en lotes de 500 transacciones
- Las transacciones se normalizan con IDs de banco, categoría y usuario
- La tabla de usuarios es creada automáticamente por el script de inicialización

## Ejemplo Completo de Testing

### 1. Iniciar el servicio
```bash
# Con Docker
docker-compose up -d

# O localmente
uvicorn src.main:app --reload
```

### 2. Inicializar la base de datos
```bash
python scripts/init_db.py
```

### 3. Generar token de prueba
```bash
python scripts/generate_test_tokens.py
```
Copia el token del usuario test1@example.com (User ID: 1)

### 4. Probar el endpoint de autenticación
```bash
curl -X GET "http://localhost:8000/api/v1/test/user-id" \
  -H "Authorization: Bearer <tu-token>"
```

Deberías ver:
```json
{
  "user_id": 1,
  "message": "El token corresponde al usuario con ID 1"
}
```

### 5. Cargar archivo de transacciones
```bash
curl -X POST "http://localhost:8000/api/v1/transacciones/upload?banco_codigo=BANCOLOMBIA" \
  -H "Authorization: Bearer <tu-token>" \
  -F "archivos=@MovimientosTusCuentasBancolombia07Oct2025.xlsx"
```

Respuesta esperada:
```json
{
  "lote_id": 1,
  "message": "Procesamiento iniciado. Use el lote_id 1 para consultar el estado."
}
```

### 6. Consultar estado del procesamiento
```bash
curl -X GET "http://localhost:8000/api/v1/transacciones/lote/1" \
  -H "Authorization: Bearer <tu-token>"
```

Respuesta esperada:
```json
{
  "lote_id": 1,
  "estado": "completado",
  "total_registros": 190,
  "registros_procesados": 190,
  "porcentaje_procesado": 100.0,
  "created_at": "2025-10-10T10:00:00",
  "updated_at": "2025-10-10T10:05:00"
}
```

## Licencia

MIT
