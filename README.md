# 🏦 Flowlite - Personal Finance

Sistema de finanzas personales con arquitectura de microservicios.

## 📁 Estructura del Proyecto

```
Flowlite-Personal-Finance/
├── database/                    # Base de datos compartida
│   ├── README.md
│   ├── docker-compose.database.yml
│   ├── init-databases.sql
│   ├── manage-database.sh
│   └── DATABASE_SHARING_GUIDE.md
├── identifyservice/             # Servicio de autenticación
│   ├── src/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── Dockerfile.simple
│   └── DOCKER_README.md
├── manage-flowlite.sh           # Script de gestión global
└── README.md                    # Este archivo
```

## 🚀 Inicio Rápido

### 1. Iniciar Base de Datos
```bash
./manage-flowlite.sh start-db
```

### 2. Iniciar Servicio de Identificación
```bash
./manage-flowlite.sh start identifyservice
```

### 3. Ver Estado
```bash
./manage-flowlite.sh status
```

## 🔗 Accesos

- **API Identificación**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **phpMyAdmin**: http://localhost:8081

## 🛠️ Comandos Disponibles

```bash
# Base de datos
./manage-flowlite.sh start-db      # Iniciar base de datos
./manage-flowlite.sh stop-db       # Detener base de datos
./manage-flowlite.sh restart-db    # Reiniciar base de datos

# Servicios
./manage-flowlite.sh start identifyservice    # Iniciar servicio
./manage-flowlite.sh stop identifyservice     # Detener servicio
./manage-flowlite.sh restart identifyservice  # Reiniciar servicio

# Global
./manage-flowlite.sh start-all     # Iniciar todo
./manage-flowlite.sh stop-all      # Detener todo
./manage-flowlite.sh status        # Ver estado
./manage-flowlite.sh clean         # Limpiar todo
```

## 📋 Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| identifyservice | 8080 | Autenticación y autorización |
| MySQL | 3306 | Base de datos compartida |
| phpMyAdmin | 8081 | Administración de base de datos |

## 🔧 Desarrollo

### Agregar Nuevo Servicio

1. Crear carpeta del servicio
2. Configurar docker-compose.yml
3. Conectar a la red `flowlite-shared-network`
4. Usar base de datos compartida

### Base de Datos

La base de datos está completamente separada en la carpeta `database/`. Cada servicio tiene su propia base de datos y usuario.

## 📚 Documentación

- [Base de Datos Compartida](database/README.md)
- [Guía de Uso de Base de Datos](database/DATABASE_SHARING_GUIDE.md)
- [Docker - Identify Service](identifyservice/DOCKER_README.md)

## 🏗️ Arquitectura

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

## 🚨 Troubleshooting

### Problema: No se puede conectar a la base de datos
```bash
# Verificar que la base de datos esté ejecutándose
./manage-flowlite.sh status

# Ver logs de la base de datos
./manage-flowlite.sh logs-db
```

### Problema: Servicio no inicia
```bash
# Ver logs del servicio
./manage-flowlite.sh logs identifyservice

# Reiniciar servicio
./manage-flowlite.sh restart identifyservice
```

## 📈 Próximos Pasos

- [ ] Agregar servicio de usuarios
- [ ] Agregar servicio de transacciones
- [ ] Implementar API Gateway
- [ ] Configurar monitoreo
- [ ] Implementar CI/CD

---

**Desarrollado con ❤️ para Flowlite**