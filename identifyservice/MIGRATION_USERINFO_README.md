# Guía de Migración - UserInfo

## Problema Identificado

El endpoint `/user-info/update` estaba fallando con el error:
```
Incorrect string value: '\xDC\x1C\xBCw\xEA\xEF...' for column 'id_user' at row 1
```

**Causa raíz:** La tabla `UserInfo` tenía un diseño incorrecto donde `id_user` era la clave primaria en lugar de tener su propio ID único.

## Cambios Realizados

### 1. Estructura de la Tabla (Base de Datos)

**Antes:**
```sql
CREATE TABLE UserInfo (
    id_user [tipo_incorrecto] PRIMARY KEY,
    primerNombre VARCHAR(50),
    ...
);
```

**Después:**
```sql
CREATE TABLE UserInfo (
    id BINARY(16) NOT NULL PRIMARY KEY,      -- Nuevo ID único
    id_user BINARY(16) NOT NULL UNIQUE,      -- Referencia al usuario
    primerNombre VARCHAR(50),
    segundoNombre VARCHAR(50),
    primerApellido VARCHAR(50),
    segundoApellido VARCHAR(50),
    telefono VARCHAR(15),
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    pais VARCHAR(100),
    fechaNacimiento DATE,
    numeroIdentificacion VARCHAR(20) UNIQUE,
    tipoIdentificacion VARCHAR(10),
    genero VARCHAR(20),
    estadoCivil VARCHAR(30),
    ocupacion VARCHAR(100),
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE
);
```

### 2. Entidad JPA (`UserInfoEntity.java`)

**Cambios principales:**
- Nuevo campo `id` como `@Id` (clave primaria)
- Campo `idUser` ahora es `@Column` con `unique = true`
- Agregados todos los campos faltantes: `fechaNacimiento`, `genero`, `estadoCivil`, `ocupacion`, `createdAt`, `updatedAt`, `activo`
- Agregados hooks `@PrePersist` y `@PreUpdate` para manejo automático de timestamps
- Uso de `columnDefinition = "BINARY(16)"` para UUIDs

### 3. Mapper (`UserInfoMapper.java`)

**Cambios principales:**
- Actualizado `toDomain()` para mapear correctamente `id` y `userId` desde la entidad
- Actualizado `toEntity()` para incluir el nuevo campo `id`
- Agregado mapeo completo de todos los campos adicionales
- Mejorado método `createIdentificationType()` con switch para mapear códigos a descripciones

## Pasos de Migración

### Opción 1: Base de Datos Vacía (Recomendado si no hay datos)

Si la tabla `UserInfo` está vacía o los datos no son importantes:

```sql
-- 1. Eliminar tabla existente
DROP TABLE IF EXISTS UserInfo;

-- 2. Ejecutar el script completo
SOURCE migration_fix_userinfo.sql;
```

### Opción 2: Migración con Preservación de Datos

Si ya tienes datos en la tabla:

1. **Hacer backup de la base de datos:**
```bash
mysqldump -u root -p flowlite_db UserInfo > userinfo_backup.sql
```

2. **Ejecutar el script de migración:**
```bash
mysql -u root -p flowlite_db < migration_fix_userinfo.sql
```

El script realiza:
- Crea tabla `UserInfo_new` con la estructura correcta
- Migra datos de `UserInfo` a `UserInfo_new` generando nuevos UUIDs para el campo `id`
- Elimina tabla antigua
- Renombra la nueva tabla

3. **Verificar que los datos se migraron correctamente:**
```sql
SELECT COUNT(*) FROM UserInfo;
SELECT * FROM UserInfo LIMIT 5;
```

### Opción 3: Migración Segura con Backup

Para mayor seguridad:

```sql
-- 1. Renombrar tabla antigua como backup
RENAME TABLE UserInfo TO UserInfo_backup;

-- 2. Crear nueva tabla
-- (ejecutar solo la parte de CREATE TABLE del script)

-- 3. Migrar datos
INSERT INTO UserInfo (id, id_user, primerNombre, ...)
SELECT UUID_TO_BIN(UUID()), id_user, primerNombre, ...
FROM UserInfo_backup;

-- 4. Verificar
SELECT COUNT(*) FROM UserInfo;
SELECT COUNT(*) FROM UserInfo_backup;

-- 5. Si todo está bien, eliminar backup
-- DROP TABLE UserInfo_backup;
```

## Verificación Post-Migración

### 1. Verificar Estructura de la Tabla

```sql
DESCRIBE UserInfo;
```

Deberías ver:
- `id` como PRIMARY KEY (BINARY(16))
- `id_user` como UNIQUE (BINARY(16))
- Todas las columnas adicionales

### 2. Probar el Endpoint

**Request:**
```bash
curl -X PUT http://localhost:8080/user-info/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "primerNombre": "Juan",
    "primerApellido": "García",
    "telefono": "3001234567",
    "numeroIdentificacion": "12345678",
    "tipoIdentificacion": "CC"
  }'
```

**Expected Response (200 OK):**
```json
{
  "message": "Información personal actualizada exitosamente",
  "userInfo": {
    "id": "1a3ec2da-5cfa-45df-b9a0-764db8fde346",
    "userId": "7160fc51-692d-4760-9fbe-6a69591bd8d2",
    "nombreCompleto": "Juan García",
    "telefono": "3001234567",
    "numeroIdentificacion": "12345678",
    "tipoIdentificacion": "Cédula de Ciudadanía",
    "isComplete": true
  }
}
```

### 3. Verificar Logs

No deberías ver más el error:
```
Incorrect string value: '\xDC\x1C\xBCw\xEA\xEF...' for column 'id_user'
```

## Beneficios de la Nueva Estructura

1. **Separación de Responsabilidades:**
   - `id`: Identificador único de la información personal
   - `id_user`: Referencia al usuario (FK)

2. **Compatibilidad con UUIDs:**
   - Uso correcto de `BINARY(16)` para almacenar UUIDs eficientemente

3. **Campos Completos:**
   - Todos los campos del dominio ahora están disponibles en la base de datos
   - Metadatos automáticos (`createdAt`, `updatedAt`)

4. **Validaciones:**
   - `numeroIdentificacion` UNIQUE
   - `telefono` indexado para búsquedas rápidas
   - `id_user` UNIQUE (un usuario solo puede tener una información personal)

## Rollback (En Caso de Problemas)

Si algo sale mal y tienes backup:

```sql
-- 1. Eliminar nueva tabla
DROP TABLE UserInfo;

-- 2. Restaurar desde backup
RENAME TABLE UserInfo_backup TO UserInfo;

-- O desde archivo:
mysql -u root -p flowlite_db < userinfo_backup.sql
```

## Notas Importantes

- ⚠️ **Siempre hacer backup antes de migrar**
- ⚠️ El script usa `UUID_TO_BIN(UUID())` que requiere MySQL 8.0+
- ⚠️ Si usas MySQL 5.7, reemplaza con `UNHEX(REPLACE(UUID(), '-', ''))`
- ✅ Después de migrar, reinicia la aplicación Spring Boot
- ✅ Verifica que los tests pasen

## Contacto

Si tienes problemas con la migración, contacta al equipo de desarrollo.
