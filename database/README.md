# 🗄️ Base de Datos Compartida - Flowlite

Esta carpeta contiene toda la configuración y gestión de la base de datos MySQL compartida para el ecosistema Flowlite.

## 📁 Estructura

```
database/
├── README.md                    # Este archivo
├── docker-compose.database.yml  # Configuración de MySQL y phpMyAdmin
├── init-databases.sql          # Script de inicialización de bases de datos
├── manage-database.sh          # Script de gestión automatizada (Linux/macOS)
├── manage-database.ps1         # Script PowerShell (Windows)
├── manage-database.bat         # Script Batch (Windows)
└── DATABASE_SHARING_GUIDE.md   # Guía completa de uso
```

## 🚀 Inicio Rápido

### 🐧 Linux/macOS
```bash
cd database
./manage-database.sh start-db
./manage-database.sh status
```

### 🪟 Windows (PowerShell - Recomendado)
```powershell
cd database
.\manage-database.ps1 start-db
.\manage-database.ps1 status
```

### 🪟 Windows (CMD/Batch)
```cmd
cd database
manage-database.bat start-db
manage-database.bat status
```

### 🌐 Acceder a phpMyAdmin
- **URL**: http://localhost:8081
- **Usuario**: `root`
- **Contraseña**: `Flowlite10+`

## 🔧 Servicios Incluidos

- **MySQL 8.0**: Base de datos principal (puerto 3306)
- **phpMyAdmin**: Interfaz web de administración (puerto 8081)

## 📋 Bases de Datos Creadas

| Base de Datos | Usuario | Contraseña | Descripción |
|---------------|---------|------------|-------------|
| `identifyservice` | `identifyservice_user` | `identifyservice_pass` | Autenticación y autorización |
| `userservice` | `userservice_user` | `userservice_pass` | Gestión de usuarios |
| `transactionservice` | `transactionservice_user` | `transactionservice_pass` | Transacciones financieras |
| `notificationservice` | `notificationservice_user` | `notificationservice_pass` | Notificaciones |

## 🛠️ Comandos Disponibles

### 🐧 Linux/macOS
```bash
./manage-database.sh start-db      # Iniciar base de datos
./manage-database.sh stop-db       # Detener base de datos
./manage-database.sh restart-db    # Reiniciar base de datos
./manage-database.sh status        # Ver estado
./manage-database.sh logs-db       # Ver logs
./manage-database.sh clean         # Limpiar todo (¡CUIDADO!)
./manage-database.sh help          # Mostrar ayuda
```

### 🪟 Windows (PowerShell)
```powershell
.\manage-database.ps1 start-db     # Iniciar base de datos
.\manage-database.ps1 stop-db      # Detener base de datos
.\manage-database.ps1 restart-db   # Reiniciar base de datos
.\manage-database.ps1 status       # Ver estado
.\manage-database.ps1 logs-db      # Ver logs
.\manage-database.ps1 clean        # Limpiar todo (¡CUIDADO!)
.\manage-database.ps1 help         # Mostrar ayuda
```

### 🪟 Windows (CMD/Batch)
```cmd
manage-database.bat start-db       # Iniciar base de datos
manage-database.bat stop-db        # Detener base de datos
manage-database.bat restart-db    # Reiniciar base de datos
manage-database.bat status        # Ver estado
manage-database.bat logs-db       # Ver logs
manage-database.bat clean         # Limpiar todo (¡CUIDADO!)
manage-database.bat help          # Mostrar ayuda
```

## 🔗 Conexión desde Servicios

### Desde Docker Compose
```yaml
environment:
  SPRING_DATASOURCE_URL: jdbc:mysql://flowlite-shared-mysql:3306/tu_database
  SPRING_DATASOURCE_USERNAME: tu_usuario
  SPRING_DATASOURCE_PASSWORD: tu_password

networks:
  flowlite-shared-network:
    external: true
    name: database_flowlite-shared-network
```

### Desde Aplicación Externa
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/tu_database
spring.datasource.username=tu_usuario
spring.datasource.password=tu_password
```

## 📊 Monitoreo

### phpMyAdmin
- **URL**: http://localhost:8081
- **Usuario**: `root`
- **Contraseña**: `Flowlite10+`

### Logs
```bash
# Ver logs de MySQL
docker logs flowlite-shared-mysql

# Ver logs de phpMyAdmin
docker logs flowlite-phpmyadmin
```

## 🔒 Seguridad

- Cada servicio tiene su propio usuario y base de datos
- Contraseñas diferentes para cada servicio
- Acceso restringido por usuario
- Conexiones encriptadas disponibles

## 🚨 Troubleshooting

### Problema: No se puede conectar
```bash
# Verificar que esté ejecutándose
docker ps | grep mysql

# Verificar logs
docker logs flowlite-shared-mysql

# Verificar red
docker network ls | grep flowlite-shared
```

### Problema: Base de datos no existe
```bash
# Conectar y crear
docker exec -it flowlite-shared-mysql mysql -u root -p
CREATE DATABASE tu_database;
```

### Problema: Scripts no funcionan en Windows
```powershell
# Si aparece error de política de ejecución en PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar que Docker esté ejecutándose
docker --version
docker-compose --version
```

### Problema: Permisos en Linux/macOS
```bash
# Hacer ejecutable el script
chmod +x manage-database.sh
```

## 📈 Para Producción

1. Usar MySQL en servidor dedicado
2. Configurar replicación
3. Implementar backup automático
4. Usar connection pooling
5. Configurar SSL/TLS

## 🔄 Migraciones de Base de Datos

### Scripts de Migración Disponibles

#### `reset-migrations.sh` ⭐ (Recomendado)
Herramienta experta para resetear y aplicar migraciones limpiamente.

```bash
cd database
./reset-migrations.sh
```

**Qué hace:**
- ✅ Limpia estados de migraciones fallidas
- ✅ Aplica migración consolidada
- ✅ Verifica estructura de base de datos
- ✅ Muestra próximos pasos

#### `run-migrations.sh`
Ejecutor automático de migraciones para bases de datos frescas.

```bash
cd database
./run-migrations.sh
```

#### `clean-and-migrate.sh`
⚠️ **PELIGRO**: Elimina TODOS los datos de UserInfo.

```bash
cd database
./clean-and-migrate.sh
```

### Migraciones Disponibles

#### 001_create_userinfo_table_english.sql
**Estado**: ✅ Activa
**Tipo**: Migración Consolidada Maestra
**Propósito**: Crea tabla UserInfo con nombres de columnas en inglés

**Características:**
- Idempotente (puede ejecutarse múltiples veces)
- Crea backup antes de eliminar tabla antigua
- Almacenamiento correcto de UUIDs (BINARY(16))
- Nombres de columnas en inglés
- Índices optimizados

### Solución de Problemas de Migraciones

#### Error: "Data too long for column 'id_user'"
**Solución**: Usa `reset-migrations.sh`

Este error ocurre cuando datos UUID antiguos están almacenados como VARCHAR.

#### Error: "Unknown column 'fechaNacimiento'"
**Solución**: Usa `reset-migrations.sh`

Esto pasa cuando migraciones parciales fallaron.

#### Error: "Docker not available"
**Solución**: Inicia MySQL primero

```bash
cd ../InfrastructureService
docker-compose up -d mysql
cd ../database
./reset-migrations.sh
```

### Verificar Migraciones

```bash
# Ver migraciones aplicadas
docker exec flowlite-mysql mysql -uroot -prootpassword flowlite_db \
  -e "SELECT * FROM schema_migrations;"

# Ver estructura de tabla
docker exec flowlite-mysql mysql -uroot -prootpassword flowlite_db \
  -e "DESCRIBE UserInfo;"
```

---

**Nota**: Esta configuración es ideal para desarrollo. Para producción, considera servicios gestionados como AWS RDS, Google Cloud SQL, o Azure Database.
