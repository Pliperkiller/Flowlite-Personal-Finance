# Detección de Archivos Duplicados - Guía de Integración

## 📋 Resumen

Este documento describe la implementación de un sistema de detección de archivos duplicados mediante hash SHA256. El sistema previene que el mismo archivo sea procesado múltiples veces, ahorrando recursos y manteniendo la integridad de los datos.

## 🎯 Funcionalidad

- **Detección silenciosa**: Si un usuario sube el mismo archivo dos veces, el sistema devuelve el `batch_id` original sin notificar al usuario
- **Hash SHA256**: Identifica archivos por su contenido, no por metadatos externos
- **Persistencia**: Guarda historial de archivos subidos en base de datos
- **Sin duplicados**: Evita procesar el mismo archivo múltiples veces

## 📌 Nota Importante sobre Tipos de Datos

**IDs en la Base de Datos:**
- Todos los IDs (id_file, id_user, id_batch) se almacenan como `CHAR(36)` en MySQL
- En las entidades de dominio Python, se usan como `str` (cadenas de texto)
- Los valores son UUIDs pero representados como strings: `"550e8400-e29b-41d4-a716-446655440000"`

**Ejemplo:**
```python
# ✅ CORRECTO
user_id: str = "550e8400-e29b-41d4-a716-446655440000"
file_upload = FileUploadHistory(
    id_file=None,  # Se generará automáticamente
    id_user=user_id,  # str, no UUID
    ...
)

# ❌ INCORRECTO (no usar)
from uuid import UUID
user_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440000")
```

---

## 📁 Estructura de Archivos Creados

```
uploadservice/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── file_upload_history.py          ✅ NUEVA ENTIDAD
│   │   └── ports/
│   │       └── file_upload_history_repository_port.py  ✅ NUEVO PORT
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── file_upload_history_model.py    ✅ NUEVO MODELO
│   │   └── repositories/
│   │       └── mysql_file_upload_history_repository.py  ✅ NUEVO REPOSITORIO
│   ├── application/
│   │   └── use_cases/
│   │       └── process_files_use_case_updated.py  ✅ VERSIÓN ACTUALIZADA
│   └── api/
│       ├── routes/
│       │   └── transactions_updated.py         ✅ VERSIÓN ACTUALIZADA
│       └── dependencies/
│           └── file_upload_history_dependency.py  ✅ NUEVA DEPENDENCIA
├── database/
│   └── create_file_upload_history_table.sql    ✅ SCRIPT SQL
└── DUPLICATE_FILE_DETECTION.md                 📖 ESTE DOCUMENTO
```

---

## 🔧 Pasos de Integración

### Paso 1: Crear la Tabla en Base de Datos

En tu servicio de **infraestructura**, ejecuta el script SQL:

```bash
mysql -u usuario -p nombre_base_datos < database/create_file_upload_history_table.sql
```

O copia y ejecuta el contenido de:
- `database/create_file_upload_history_table.sql`

### Paso 2: Actualizar Imports de Entidades

Edita `src/domain/entities/__init__.py`:

```python
from .transaction import Transaction
from .bank import Bank
from .category import Category
from .transaction_batch import TransactionBatch
from .file_upload_history import FileUploadHistory  # ← AGREGAR

__all__ = [
    "Transaction",
    "Bank",
    "Category",
    "TransactionBatch",
    "FileUploadHistory",  # ← AGREGAR
]
```

### Paso 3: Agregar Modelo a SQLAlchemy

Edita `src/infrastructure/database/models.py` y agrega al final:

```python
# Opción A: Importar el modelo ya creado
from .file_upload_history_model import FileUploadHistoryModel

# Opción B: Copiar el contenido de file_upload_history_model.py al final de models.py
```

### Paso 4: Exportar Nuevo Repositorio

Edita `src/infrastructure/repositories/__init__.py`:

```python
from .mysql_transaction_repository import MySQLTransactionRepository
from .mysql_bank_repository import MySQLBankRepository
from .mysql_category_repository import MySQLCategoryRepository
from .mysql_transaction_batch_repository import MySQLTransactionBatchRepository
from .mysql_user_repository import MySQLUserRepository
from .mysql_file_upload_history_repository import MySQLFileUploadHistoryRepository  # ← AGREGAR

__all__ = [
    "MySQLTransactionRepository",
    "MySQLBankRepository",
    "MySQLCategoryRepository",
    "MySQLTransactionBatchRepository",
    "MySQLUserRepository",
    "MySQLFileUploadHistoryRepository",  # ← AGREGAR
]
```

### Paso 5: Agregar Dependencia

Edita `src/api/dependencies/repositories.py` y agrega:

```python
from ...infrastructure.repositories.mysql_file_upload_history_repository import (
    MySQLFileUploadHistoryRepository
)

async def get_file_upload_history_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLFileUploadHistoryRepository:
    """Dependency for getting the file upload history repository."""
    return MySQLFileUploadHistoryRepository(db)
```

Luego exporta en `src/api/dependencies/__init__.py`:

```python
from .repositories import (
    get_transaction_repository,
    get_bank_repository,
    get_category_repository,
    get_batch_repository,
    get_user_repository,
    get_file_upload_history_repository,  # ← AGREGAR
)
```

### Paso 6: Reemplazar ProcessFilesUseCase

**Opción A: Reemplazar el archivo original**

```bash
# Backup del original
cp src/application/use_cases/process_files_use_case.py \
   src/application/use_cases/process_files_use_case_backup.py

# Reemplazar con la versión actualizada
cp src/application/use_cases/process_files_use_case_updated.py \
   src/application/use_cases/process_files_use_case.py
```

**Opción B: Aplicar cambios manualmente**

Ver diferencias en `process_files_use_case_updated.py`:
1. Agregar `file_upload_history_repo` en `__init__`
2. Cambiar firma de `execute()` para recibir `files_data` en vez de `files_content`
3. Agregar validación de hash antes de parsear archivos
4. Guardar historial después de crear batch

### Paso 7: Actualizar Endpoint de Upload

Edita `src/api/routes/transactions.py`:

**1. Agregar import de hashlib:**
```python
import hashlib
```

**2. Agregar dependencia en el endpoint:**
```python
from ..dependencies import (
    # ... imports existentes ...
    get_file_upload_history_repository,  # ← AGREGAR
)

@router.post("/upload", ...)
async def upload_files(
    # ... parámetros existentes ...
    file_upload_history_repo=Depends(get_file_upload_history_repository),  # ← AGREGAR
):
```

**3. Calcular hashes al leer archivos:**
```python
# Reemplazar esta sección:
files_content = []
for file in files:
    content = await file.read()
    files_content.append(content)

# Con esta:
files_data = []
for file in files:
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    files_data.append((content, file_hash, file.filename, file_size))
```

**4. Actualizar llamada al use case:**
```python
# Agregar file_upload_history_repo al constructor
use_case = ProcessFilesUseCase(
    transaction_repo=transaction_repo,
    bank_repo=bank_repo,
    category_repo=category_repo,
    batch_repo=batch_repo,
    classifier=classifier,
    message_broker=message_broker,
    file_upload_history_repo=file_upload_history_repo,  # ← AGREGAR
    session_factory=session_factory,
)

# Cambiar llamada a execute
batch_id = await use_case.execute(
    files_data=files_data,  # ← Cambiar de files_content
    parser=parser,
    user_id=user_id,
)
```

---

## 🧪 Pruebas

### Prueba 1: Subir archivo por primera vez

```bash
curl -X POST http://localhost:8000/api/v1/transactions/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "bank_code=BANCOLOMBIA" \
  -F "files=@transacciones.xlsx"
```

**Resultado esperado:**
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Processing started. Use batch_id ... to check the status."
}
```

### Prueba 2: Subir el mismo archivo de nuevo

```bash
curl -X POST http://localhost:8000/api/v1/transactions/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "bank_code=BANCOLOMBIA" \
  -F "files=@transacciones.xlsx"
```

**Resultado esperado:**
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Processing started. Use batch_id ... to check the status."
}
```

**Nota:** Devuelve el **mismo batch_id** y no procesa el archivo nuevamente.

### Prueba 3: Verificar en la base de datos

```sql
SELECT
    file_name,
    bank_code,
    upload_date,
    id_batch,
    LEFT(file_hash, 16) as hash_preview
FROM FileUploadHistory
WHERE id_user = 'tu-user-id'
ORDER BY upload_date DESC;
```

---

## 📊 Diagrama de Flujo

```
Usuario sube archivo
         │
         ▼
Calcular SHA256 hash
         │
         ▼
¿Hash existe en BD para este usuario?
         │
    ┌────┴────┐
   SÍ        NO
    │         │
    │         ▼
    │    Parsear archivo
    │         │
    │         ▼
    │    Crear batch
    │         │
    │         ▼
    │    Guardar FileUploadHistory
    │         │
    │         ▼
    │    Procesar transacciones (async)
    │         │
    └────┬────┘
         │
         ▼
Retornar batch_id
```

---

## 🔍 Cómo Funciona el Hash

### ¿Qué es un hash SHA256?

Un hash SHA256 es una "huella digital" única de un archivo:

```python
import hashlib

content = b"archivo contenido..."  # Bytes del archivo
hash_value = hashlib.sha256(content).hexdigest()
# Resultado: "a3d5e8f9c2b1d4e7..." (64 caracteres hexadecimales)
```

### Propiedades importantes:

✅ **Determinístico**: Mismo contenido = mismo hash (siempre)
✅ **Único**: Contenido diferente = hash diferente (99.999999%)
✅ **Irreversible**: No puedes obtener el archivo del hash
✅ **Rápido**: Se calcula en milisegundos

### Comparación con metadatos:

| Escenario | Hash | Metadatos (nombre, fecha) |
|-----------|------|---------------------------|
| Archivo renombrado | ✅ Mismo hash | ❌ Nombre cambió |
| Archivo copiado | ✅ Mismo hash | ❌ Fecha cambió |
| Descarga múltiple | ✅ Mismo hash | ❌ Fecha/nombre pueden cambiar |
| Contenido editado | ❌ Hash diferente | ⚠️ Puede ser igual |

---

## 🛠️ Mantenimiento

### Limpiar registros antiguos (opcional)

Si deseas eliminar historial de archivos antigos:

```sql
-- Eliminar registros de más de 1 año
DELETE FROM FileUploadHistory
WHERE upload_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);
```

### Verificar duplicados entre usuarios

```sql
-- Ver si múltiples usuarios subieron el mismo archivo
SELECT
    file_hash,
    COUNT(*) as num_uploads,
    COUNT(DISTINCT id_user) as num_users,
    MIN(file_name) as example_filename
FROM FileUploadHistory
GROUP BY file_hash
HAVING COUNT(DISTINCT id_user) > 1;
```

### Estadísticas del sistema

```sql
SELECT
    COUNT(*) as total_uploads,
    COUNT(DISTINCT id_user) as unique_users,
    COUNT(DISTINCT file_hash) as unique_files,
    SUM(file_size) / 1024 / 1024 as total_mb,
    MIN(upload_date) as first_upload,
    MAX(upload_date) as last_upload
FROM FileUploadHistory;
```

---

## 🚨 Troubleshooting

### Error: "Table 'FileUploadHistory' doesn't exist"

**Solución:** Ejecuta el script SQL en la base de datos.

### Error: "No module named 'file_upload_history'"

**Solución:** Verifica que agregaste los imports en los `__init__.py`.

### Error: "get_file_upload_history_repository() is not defined"

**Solución:** Agrega la función de dependencia en `repositories.py`.

### Los archivos duplicados se siguen procesando

**Solución:** Verifica que estás usando la versión actualizada de `ProcessFilesUseCase`.

### Hash diferente para el mismo archivo

**Problema:** Si abres y guardas el archivo en Excel, el contenido binario cambia aunque los datos sean iguales.

**Esto es correcto:** El hash detecta cualquier cambio en el archivo, incluso metadatos internos de Excel.

---

## 📝 Notas Adicionales

### Comportamiento con múltiples archivos

Si el usuario sube 3 archivos en una sola request:
- Si **todos son nuevos**: Se procesan todos, se crea 1 batch
- Si **uno es duplicado**: Se retorna el batch_id del duplicado, los otros no se procesan
- **Recomendación**: Validar todos primero, o procesar archivo por archivo

### Índices de base de datos

La tabla tiene un índice compuesto `(id_user, file_hash)` que hace la validación extremadamente rápida:

```sql
-- Esta consulta es muy eficiente gracias al índice
SELECT * FROM FileUploadHistory
WHERE id_user = ? AND file_hash = ?;
```

### Logs

El sistema genera logs informativos:

```
INFO - Duplicate file detected: transacciones.xlsx (hash: a3d5e8f9c2b1d4e7...)
       Original upload: 2025-10-30 10:00:00, Batch ID: 550e8400...

INFO - Saved file upload history: transacciones.xlsx (hash: a3d5e8f9c2b1d4e7...)
       Batch ID: 550e8400...
```

---

## ✅ Checklist de Integración

- [ ] Ejecutar script SQL para crear tabla `FileUploadHistory`
- [ ] Actualizar `domain/entities/__init__.py`
- [ ] Actualizar `infrastructure/database/models.py`
- [ ] Actualizar `infrastructure/repositories/__init__.py`
- [ ] Agregar dependencia en `api/dependencies/repositories.py`
- [ ] Actualizar `api/dependencies/__init__.py`
- [ ] Reemplazar o actualizar `ProcessFilesUseCase`
- [ ] Actualizar endpoint `transactions.py`
- [ ] Probar subir archivo nuevo
- [ ] Probar subir archivo duplicado
- [ ] Verificar registros en base de datos

---

## 📞 Soporte

Si tienes dudas sobre la implementación, revisa:
- Los comentarios en cada archivo creado
- Los ejemplos en `transactions_updated.py`
- El script SQL con queries de ejemplo

¡Listo para integrar! 🚀
