# Estructura de Tabla: FileUploadHistory

## 📊 Esquema de la Tabla

```
FileUploadHistory
├── id_file           CHAR(36)       PK  - UUID del registro
├── id_user           CHAR(36)       NOT NULL, INDEX - Usuario que subió el archivo
├── file_hash         CHAR(64)       NOT NULL, INDEX - Hash SHA256 del contenido
├── file_name         VARCHAR(255)   NOT NULL - Nombre original del archivo
├── bank_code         VARCHAR(50)    NOT NULL - Código del banco (e.g., BANCOLOMBIA)
├── file_size         INT            NOT NULL - Tamaño en bytes
├── upload_date       DATETIME       NOT NULL, DEFAULT CURRENT_TIMESTAMP, INDEX
└── id_batch          CHAR(36)       FK(TransactionBatch) - Batch generado
```

## 🔑 Claves e Índices

### Primary Key
- `id_file` - Identificador único del registro

### Foreign Keys
- `id_batch` → `TransactionBatch(id_batch)`
  - ON DELETE RESTRICT
  - ON UPDATE CASCADE

### Indexes
1. **idx_user** - Individual en `id_user`
2. **idx_hash** - Individual en `file_hash`
3. **idx_user_hash** - Compuesto en `(id_user, file_hash)` ⭐ Principal para duplicados
4. **idx_upload_date** - Individual en `upload_date`

## 📏 Restricciones

- Todos los campos son `NOT NULL`
- `file_hash` debe ser exactamente 64 caracteres (SHA256 hex)
- `id_file`, `id_user`, `id_batch` deben ser UUIDs válidos (36 caracteres)
- `upload_date` se establece automáticamente en la inserción

## 💾 Tamaño Estimado

Por registro:
- Campos fijos: ~200 bytes
- file_name (promedio): ~50 bytes
- **Total por registro: ~250 bytes**

Estimación para 10,000 archivos: ~2.5 MB

## 🎯 Uso Principal

### Detección de Duplicados (Query más común)

```sql
SELECT id_batch, upload_date, file_name
FROM FileUploadHistory
WHERE id_user = ?
  AND file_hash = ?
LIMIT 1;
```

**Performance:** ⚡ Muy rápido gracias al índice compuesto `idx_user_hash`

## 📋 Ejemplo de Registro

```
id_file:      "550e8400-e29b-41d4-a716-446655440000"
id_user:      "7c9e6679-7425-40de-944b-e07fc1f90ae7"
file_hash:    "a3d5e8f9c2b1d4e7f0a8b6c3d1e9f2a5b8c4d7e1f3a6b9c2d5e8f1a4b7c0d3e6"
file_name:    "transacciones_enero_2024.xlsx"
bank_code:    "BANCOLOMBIA"
file_size:    45678
upload_date:  "2024-10-30 14:35:22"
id_batch:     "8b4e2f1a-6c9d-4e3a-b7f5-1d8c9e2a6b3f"
```

## 🔗 Relaciones

```
User (IdentityService)
  ↓ (id_user - No FK, referencia lógica)
FileUploadHistory
  ↓ (id_batch - FK)
TransactionBatch
  ↓ (id_batch)
Transaction (múltiples)
```

## 🛠️ Comandos DDL

### Crear Tabla
```sql
-- Ver: create_file_upload_history_table.sql
```

### Eliminar Tabla (Rollback)
```sql
DROP TABLE IF EXISTS FileUploadHistory;
```

### Verificar Estructura
```sql
DESCRIBE FileUploadHistory;
```

### Ver Índices
```sql
SHOW INDEX FROM FileUploadHistory;
```

## 📈 Queries Útiles

### Ver últimas subidas
```sql
SELECT file_name, bank_code, upload_date
FROM FileUploadHistory
ORDER BY upload_date DESC
LIMIT 10;
```

### Contar archivos por usuario
```sql
SELECT id_user, COUNT(*) as num_files
FROM FileUploadHistory
GROUP BY id_user;
```

### Buscar duplicados (mismo hash, diferentes usuarios)
```sql
SELECT file_hash, COUNT(DISTINCT id_user) as num_users
FROM FileUploadHistory
GROUP BY file_hash
HAVING COUNT(DISTINCT id_user) > 1;
```

### Espacio usado por usuario
```sql
SELECT
    id_user,
    COUNT(*) as num_files,
    SUM(file_size) / 1024 / 1024 as total_mb
FROM FileUploadHistory
GROUP BY id_user;
```

## 🔒 Consideraciones de Seguridad

- ✅ `id_user` permite aislamiento de datos por usuario
- ✅ No hay información sensible almacenada (solo hash, no contenido)
- ✅ El hash SHA256 no es reversible
- ⚠️ Considera agregar índice en `bank_code` si consultas por banco frecuentemente

## ⚙️ Configuración del Motor

```
ENGINE: InnoDB
CHARSET: utf8mb4
COLLATE: utf8mb4_unicode_ci
```

**Motivo:**
- InnoDB soporta transacciones y foreign keys
- utf8mb4 soporta caracteres especiales y emojis
- unicode_ci es case-insensitive para comparaciones

## 🚀 Optimizaciones Futuras

1. **Particionamiento por fecha** (si el volumen crece mucho)
   ```sql
   PARTITION BY RANGE (YEAR(upload_date))
   ```

2. **Índice adicional en bank_code** (si se consulta frecuentemente)
   ```sql
   CREATE INDEX idx_bank ON FileUploadHistory(bank_code);
   ```

3. **Archivado automático** (mover registros antiguos a tabla histórica)
   ```sql
   -- Crear tabla de archivo
   CREATE TABLE FileUploadHistory_Archive LIKE FileUploadHistory;

   -- Mover registros antiguos
   INSERT INTO FileUploadHistory_Archive
   SELECT * FROM FileUploadHistory
   WHERE upload_date < DATE_SUB(NOW(), INTERVAL 2 YEAR);
   ```

---

✅ **Tabla lista para producción**
