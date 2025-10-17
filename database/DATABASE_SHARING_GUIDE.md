# 🗄️ Guía de Base de Datos Compartida

Esta guía explica cómo usar la base de datos MySQL compartida para múltiples servicios en el ecosistema Flowlite.

## 🎯 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Base de Datos Compartida                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MySQL 8.0 (Puerto 3306)               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │identifyservice│ │userservice │ │transactionservice│ │   │
│  │  │   database   │ │  database  │ │   database  │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Servicios de Aplicación                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │Identify     │ │User         │ │Transaction  │           │
│  │Service      │ │Service      │ │Service      │           │
│  │:8080        │ │:8081        │ │:8082        │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Configuración Inicial

### 1. Iniciar Base de Datos Compartida

```bash
# Iniciar solo la base de datos
./manage-database.sh start-db

# O manualmente
docker-compose -f docker-compose.database.yml up -d
```

### 2. Verificar Estado

```bash
# Ver estado de la base de datos
./manage-database.sh status

# Acceder a phpMyAdmin
# http://localhost:8081
```

## 🔧 Configuración para Nuevos Servicios

### Para un nuevo servicio (ej: UserService)

1. **Crear docker-compose.yml del servicio:**

```yaml
version: '3.8'

services:
  userservice:
    build: .
    container_name: flowlite-userservice
    ports:
      - "8081:8080"
    environment:
      # Configuración de base de datos
      SPRING_DATASOURCE_URL: jdbc:mysql://flowlite-shared-mysql:3306/userservice?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
      SPRING_DATASOURCE_USERNAME: userservice_user
      SPRING_DATASOURCE_PASSWORD: userservice_pass
      SPRING_DATASOURCE_DRIVER_CLASS_NAME: com.mysql.cj.jdbc.Driver
      
      # Configuración JPA
      SPRING_JPA_HIBERNATE_DDL_AUTO: update
      SPRING_JPA_SHOW_SQL: "true"
    networks:
      - flowlite-shared-network

networks:
  flowlite-shared-network:
    external: true
    name: database_flowlite-shared-network
```

2. **Configurar application.properties:**

```properties
# Base de datos
spring.datasource.url=jdbc:mysql://flowlite-shared-mysql:3306/userservice?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
spring.datasource.username=userservice_user
spring.datasource.password=userservice_pass
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA/Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
```

## 📋 Bases de Datos Disponibles

| Base de Datos | Usuario | Contraseña | Descripción |
|---------------|---------|------------|-------------|
| `identifyservice` | `identifyservice_user` | `identifyservice_pass` | Autenticación y autorización |
| `userservice` | `userservice_user` | `userservice_pass` | Gestión de usuarios |
| `transactionservice` | `transactionservice_user` | `transactionservice_pass` | Transacciones financieras |
| `notificationservice` | `notificationservice_user` | `notificationservice_pass` | Notificaciones |

## 🛠️ Comandos de Gestión

```bash
# Iniciar base de datos
./manage-database.sh start-db

# Iniciar aplicación específica
./manage-database.sh start-app

# Iniciar todo
./manage-database.sh start-all

# Ver estado
./manage-database.sh status

# Ver logs
./manage-database.sh logs-db
./manage-database.sh logs-app

# Limpiar todo (¡CUIDADO!)
./manage-database.sh clean
```

## 🔗 Conexión desde Aplicaciones

### Desde Docker Compose
```yaml
environment:
  SPRING_DATASOURCE_URL: jdbc:mysql://flowlite-shared-mysql:3306/tu_database
  SPRING_DATASOURCE_USERNAME: tu_usuario
  SPRING_DATASOURCE_PASSWORD: tu_password
```

### Desde Aplicación Externa
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/tu_database
spring.datasource.username=tu_usuario
spring.datasource.password=tu_password
```

## 🔒 Seguridad

- Cada servicio tiene su propio usuario y base de datos
- Contraseñas diferentes para cada servicio
- Acceso restringido por usuario
- Conexiones encriptadas (SSL disponible)

## 📊 Monitoreo

### phpMyAdmin
- **URL**: http://localhost:8081
- **Usuario**: `root`
- **Contraseña**: `Flowlite10+`

### Logs de Base de Datos
```bash
docker logs flowlite-shared-mysql
```

## 🚨 Troubleshooting

### Problema: No se puede conectar a la base de datos
```bash
# Verificar que la base de datos esté ejecutándose
docker ps | grep mysql

# Verificar logs
docker logs flowlite-shared-mysql

# Verificar red
docker network ls | grep flowlite-shared
```

### Problema: Base de datos no existe
```bash
# Conectar a MySQL y crear la base de datos
docker exec -it flowlite-shared-mysql mysql -u root -p
CREATE DATABASE tu_database;
```

### Problema: Usuario no tiene permisos
```bash
# Conectar como root y otorgar permisos
docker exec -it flowlite-shared-mysql mysql -u root -p
GRANT ALL PRIVILEGES ON tu_database.* TO 'tu_usuario'@'%';
FLUSH PRIVILEGES;
```

## 📈 Escalabilidad

### Para Producción
1. Usar MySQL en un servidor dedicado
2. Configurar replicación maestro-esclavo
3. Implementar backup automático
4. Usar connection pooling
5. Configurar SSL/TLS

### Para Desarrollo
1. Usar Docker Compose como está
2. Volúmenes persistentes para datos
3. Scripts de inicialización automática
4. phpMyAdmin para administración

## 🔄 Migración de Datos

### Backup
```bash
docker exec flowlite-shared-mysql mysqldump -u root -p --all-databases > backup.sql
```

### Restore
```bash
docker exec -i flowlite-shared-mysql mysql -u root -p < backup.sql
```

---

**Nota**: Esta configuración es ideal para desarrollo y testing. Para producción, considera usar servicios de base de datos gestionados como AWS RDS, Google Cloud SQL, o Azure Database.
