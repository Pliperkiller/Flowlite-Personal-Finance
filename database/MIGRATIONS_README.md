# Sistema de Migraciones de Base de Datos - Flowlite

## Descripción

Este directorio contiene el sistema de migraciones de base de datos para Flowlite Personal Finance. Las migraciones se ejecutan automáticamente durante el inicio de la aplicación mediante el script `build_app.sh`.

## Estructura de Directorios

```
database/
├── migrations/              # Archivos de migración SQL
│   ├── 001_fix_userinfo_structure.sql
│   └── 002_next_migration.sql
├── run-migrations.sh        # Script principal de migraciones
├── manage-database.sh       # Script de gestión de base de datos
└── MIGRATIONS_README.md     # Esta documentación
```

## Cómo Funcionan las Migraciones

### 1. Ejecución Automática

Cuando ejecutas `./build_app.sh`, el sistema:
1. ✅ Inicia MySQL (y otros servicios de infraestructura)
2. ✅ **Ejecuta migraciones automáticamente** (`./database/run-migrations.sh`)
3. ✅ Inicia MailHog
4. ✅ Inicia IdentityService
5. ✅ Inicia otros servicios

### 2. Control de Migraciones

El sistema usa una tabla `schema_migrations` para rastrear qué migraciones ya se han aplicado:

```sql
CREATE TABLE schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- ✅ **Cada migración se ejecuta solo UNA vez**
- ✅ Las migraciones se ejecutan en **orden alfabético** (por eso usamos prefijos numéricos)
- ✅ Si una migración falla, el proceso se detiene
- ✅ Las migraciones ya aplicadas se saltan automáticamente

## Uso del Sistema de Migraciones

### Ejecutar Migraciones Automáticamente (Recomendado)

```bash
# Desde la raíz del proyecto
./build_app.sh
```

Esto iniciará todos los servicios Y ejecutará las migraciones pendientes.

### Ejecutar Migraciones Manualmente

```bash
# Desde la raíz del proyecto
cd database
./run-migrations.sh
```

### Listar Estado de Migraciones

```bash
cd database
./run-migrations.sh list
```

Salida ejemplo:
```
📋 Migraciones disponibles:

  ✓ 001_fix_userinfo_structure.sql (aplicada)
  ○ 002_add_user_preferences.sql (pendiente)
  ○ 003_create_transactions_table.sql (pendiente)
```

### Ver Ayuda

```bash
cd database
./run-migrations.sh help
```

## Crear una Nueva Migración

### Paso 1: Nombrar la Migración

Usa el formato: `XXX_descripcion_corta.sql`

- `XXX` = Número secuencial de 3 dígitos (001, 002, 003...)
- `descripcion_corta` = Descripción en snake_case

Ejemplos:
```
001_fix_userinfo_structure.sql
002_add_user_preferences.sql
003_create_transactions_table.sql
004_add_categories_table.sql
```

### Paso 2: Crear el Archivo SQL

```bash
cd database/migrations
nano 002_add_user_preferences.sql
```

### Paso 3: Escribir la Migración

**Estructura recomendada:**

```sql
-- ==============================================================
-- Migración 002: Agregar tabla de preferencias de usuario
-- Descripción: Almacena configuraciones personalizadas por usuario
-- ==============================================================

-- Crear nueva tabla
CREATE TABLE IF NOT EXISTS UserPreferences (
    id BINARY(16) NOT NULL PRIMARY KEY,
    id_user BINARY(16) NOT NULL UNIQUE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'es',
    currency VARCHAR(3) DEFAULT 'COP',
    timezone VARCHAR(50) DEFAULT 'America/Bogota',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_id_user (id_user)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar valores por defecto para usuarios existentes
INSERT INTO UserPreferences (id, id_user)
SELECT UUID_TO_BIN(UUID()), id FROM User
WHERE id NOT IN (SELECT id_user FROM UserPreferences);
```

**⚠️ Buenas Prácticas:**

1. **Usar `IF NOT EXISTS`** en CREATE TABLE para evitar errores
2. **Comentar bien** qué hace cada parte
3. **Ser idempotente** (poder ejecutar varias veces sin romper nada)
4. **Incluir rollback** en comentarios si es posible
5. **Probar primero** en un ambiente de desarrollo

### Paso 4: Probar la Migración

```bash
# 1. Hacer backup de la BD
docker exec flowlite-mysql mysqldump -uroot -pflowlite123 flowlite_db > backup.sql

# 2. Ejecutar migración
cd database
./run-migrations.sh

# 3. Verificar resultados
docker exec -it flowlite-mysql mysql -uroot -pflowlite123 flowlite_db -e "DESCRIBE UserPreferences;"

# 4. Si algo sale mal, restaurar backup
docker exec -i flowlite-mysql mysql -uroot -pflowlite123 flowlite_db < backup.sql
```

### Paso 5: Commit y Push

```bash
git add database/migrations/002_add_user_preferences.sql
git commit -m "feat(db): Add user preferences table migration"
git push
```

## Migraciones Actuales

### 001_fix_userinfo_structure.sql

**Propósito:** Corregir la estructura de la tabla `UserInfo`

**Cambios:**
- Separar `id` (PRIMARY KEY) de `id_user` (FK)
- Usar `BINARY(16)` para UUIDs
- Agregar campos faltantes: `fechaNacimiento`, `genero`, `estadoCivil`, `ocupacion`, `createdAt`, `updatedAt`, `activo`
- Migrar datos existentes preservando referencias

**Estado:** ✅ Aplicada automáticamente al ejecutar `build_app.sh`

## Configuración Avanzada

### Variables de Entorno

Puedes personalizar la conexión a MySQL usando variables de entorno:

```bash
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_NAME=flowlite_db
export DB_USER=root
export DB_PASSWORD=flowlite123

./database/run-migrations.sh
```

### Deshabilitar Migraciones Automáticas

Si por alguna razón necesitas deshabilitar las migraciones automáticas durante el inicio:

```bash
# Opción 1: Renombrar temporalmente el script
mv database/run-migrations.sh database/run-migrations.sh.disabled

# Opción 2: Comentar la sección en build_app.sh (líneas 193-216)
```

## Rollback de Migraciones

El sistema actual **NO soporta rollback automático**. Para revertir una migración:

### Opción 1: Restaurar desde Backup

```bash
# Restaurar backup completo
docker exec -i flowlite-mysql mysql -uroot -pflowlite123 flowlite_db < backup.sql
```

### Opción 2: Migración de Rollback Manual

Crear una nueva migración que revierta los cambios:

```sql
-- 003_rollback_user_preferences.sql
DROP TABLE IF EXISTS UserPreferences;

-- Eliminar de tracking
DELETE FROM schema_migrations WHERE migration_name = '002_add_user_preferences.sql';
```

## Solución de Problemas

### Error: "MySQL no está disponible"

```bash
# Verificar que MySQL esté corriendo
docker ps | grep flowlite-mysql

# Si no está corriendo, iniciar infraestructura
cd InfrastructureService
docker-compose up -d
```

### Error: "Migración ya aplicada"

```bash
# Ver migraciones aplicadas
docker exec flowlite-mysql mysql -uroot -pflowlite123 flowlite_db -e "SELECT * FROM schema_migrations;"

# Forzar re-ejecución (eliminar entrada)
docker exec flowlite-mysql mysql -uroot -pflowlite123 flowlite_db -e "DELETE FROM schema_migrations WHERE migration_name = '001_fix_userinfo_structure.sql';"
```

### Error: "Permission denied" al ejecutar script

```bash
chmod +x database/run-migrations.sh
```

### Verificar Logs de Migración

Los logs se muestran en la consola durante la ejecución de `build_app.sh`:

```bash
# Ver logs completos
./build_app.sh | tee build.log
```

## Mejoras Futuras

Posibles mejoras al sistema de migraciones:

1. ✅ **Versionado de esquema** - Rastrear versión actual de BD
2. ✅ **Checksums de migraciones** - Detectar cambios en migraciones aplicadas
3. ✅ **Rollback automático** - Soportar migraciones reversibles
4. ✅ **Migraciones de datos** - Scripts separados para migración de datos
5. ✅ **Integración con Flyway/Liquibase** - Herramientas profesionales de migración

## Referencias

- [Flyway](https://flywaydb.org/) - Herramienta de migración profesional para Java
- [Liquibase](https://www.liquibase.org/) - Alternativa popular a Flyway
- [Spring Boot Database Migrations](https://www.baeldung.com/database-migrations-with-flyway)

## Soporte

Si tienes problemas con las migraciones:

1. Revisa los logs de MySQL: `docker logs flowlite-mysql`
2. Verifica el estado de migraciones: `./database/run-migrations.sh list`
3. Consulta esta documentación
4. Contacta al equipo de desarrollo
