# 🚀 Guía de Inicio - IdentityService

## ✅ Pre-requisitos

1. **Java 17** instalado
2. **InfrastructureService** corriendo (MySQL, RabbitMQ, Redis)
3. **Base de datos** inicializada

### Verificar Pre-requisitos

```bash
# Verificar Java
java -version

# Verificar InfrastructureService
cd ../InfrastructureService
docker-compose ps
python scripts/check_infrastructure.py
```

---

## 🔧 Configuración

### 1. Archivo `.env`

El archivo `.env` ya está configurado con los valores correctos:

- **Puerto**: 8000
- **Base de datos**: flowlite_db (compartida con InfrastructureService)
- **Redis**: localhost:6379 con password (compartido con InfrastructureService)
- **JWT**: Clave secreta por defecto

### 2. Variables Importantes

```bash
# Servidor
SERVER_PORT=8000

# Base de Datos (InfrastructureService)
SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/flowlite_db
SPRING_DATASOURCE_USERNAME=flowlite_user
SPRING_DATASOURCE_PASSWORD=flowlite_password

# Redis (InfrastructureService)
SPRING_DATA_REDIS_HOST=localhost
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_PASSWORD=flowlite_redis_pass_2024
```

---

## 🚀 Iniciar el Servicio

### **Opción 1: Usando el Script (Recomendado)**

```bash
cd identifyservice
./start.sh
```

Este script:
- ✅ Carga variables del `.env`
- ✅ Configura Java automáticamente
- ✅ Muestra información de configuración
- ✅ Inicia el servicio

### **Opción 2: Manualmente con Gradle**

```bash
cd identifyservice

# Cargar variables de entorno
export $(grep -v '^#' .env | xargs)

# Configurar Java
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"

# Iniciar servicio
gradle bootRun
```

---

## 📊 Verificar que Funciona

### 1. **Registrar un Usuario**

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "username": "usuario",
    "password": "Password123!"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9..."
}
```

### 2. **Login**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "Password123!"
  }'
```

### 3. **Verificar Conexión a Redis**

El servicio usa Redis para:
- **Blacklist de tokens revocados**
- **Cache de sesiones**

Puedes verificar en los logs que Redis se conectó correctamente.

---

## 🌐 Interfaces Disponibles

| URL | Descripción |
|-----|-------------|
| http://localhost:8000/swagger-ui.html | Interfaz Swagger (documentación interactiva) |
| http://localhost:8000/api-docs | Documentación OpenAPI JSON |
| http://localhost:8000/auth/register | Endpoint de registro |
| http://localhost:8000/auth/login | Endpoint de login |
| http://localhost:8000/auth/validate | Endpoint de validación de token |

---

## 🔄 Integración con Otros Servicios

### **UploadService**

El UploadService valida tokens llamando a:
```
POST http://localhost:8000/auth/validate
```

### **Base de Datos Compartida**

Todos los servicios comparten la misma base de datos `flowlite_db`:
- **User**: Usuarios registrados (gestionados por IdentityService)
- **Transaction**: Transacciones (gestionadas por UploadService)
- **Insights**: Insights generados (gestionados por InsightService)

### **Redis Compartido**

Todos los servicios pueden usar el mismo Redis para:
- Cache de sesiones
- Rate limiting
- Blacklist de tokens

---

## 🛑 Detener el Servicio

### Opción 1: Usar el script kill.sh (Recomendado)

```bash
./kill.sh
```

### Opción 2: Manualmente

```bash
# Presiona Ctrl+C en la terminal donde está corriendo

# O busca y mata el proceso:
lsof -ti:8000 | xargs kill -9
```

---

## ❌ Troubleshooting

### **Error: "Connection refused" a MySQL**

```bash
# Verifica que InfrastructureService esté corriendo
cd ../InfrastructureService
docker-compose ps
docker-compose up -d
```

### **Error: "Cannot connect to Redis"**

```bash
# Verifica que Redis esté corriendo con password
docker exec -it flowlite-redis redis-cli -a flowlite_redis_pass_2024 PING

# Debería responder: PONG
```

### **Error: "Port 8000 already in use"**

```bash
# Mata el proceso en el puerto 8000
lsof -ti:8000 | xargs kill -9

# O cambia el puerto en .env
echo "SERVER_PORT=8001" >> .env
```

### **Error: "Table 'User' doesn't exist"**

```bash
# La base de datos no está inicializada
cd ../InfrastructureService
python scripts/init_database.py
python scripts/seed_database.py
```

---

## 📝 Notas de Configuración

### **Diferencias con Configuración Anterior**

| Antes | Ahora |
|-------|-------|
| Base de datos: `auth` | Base de datos: `flowlite_db` (compartida) |
| Puerto: 8080 | Puerto: 8000 |
| Usuario DB: `root` | Usuario DB: `flowlite_user` |
| Redis: Sin password | Redis: Con password `flowlite_redis_pass_2024` |

### **Ventajas de la Nueva Configuración**

✅ **Base de datos compartida**: Todos los servicios usan `flowlite_db`
✅ **Credenciales consistentes**: Mismas credenciales que InfrastructureService
✅ **Redis seguro**: Password configurado
✅ **Fácil inicio**: Script `start.sh` automatizado
✅ **Configuración centralizada**: Archivo `.env` para todas las variables

---

## 🔐 Seguridad

### **En Desarrollo**

El archivo `.env` actual es seguro para desarrollo local.

### **En Producción**

⚠️ **IMPORTANTE**: Cambia estos valores en producción:

```bash
JWT_SECRET=cambiar_por_clave_super_segura_en_produccion
SPRING_DATASOURCE_PASSWORD=cambiar_password_mysql
SPRING_DATA_REDIS_PASSWORD=cambiar_password_redis
```

---

## 📚 Más Información

- **Documentación completa**: Ver `DOCKER_README.md`, `SECURITY_GUIDE.md`
- **Validación de tokens**: Ver `JWT_VERIFICATION_GUIDE.md`
- **Pre-registro**: Ver `PREREGISTER_GUIDE.md`
- **Endpoints públicos**: Ver `PUBLIC_ENDPOINTS.md`

---

## ✅ Checklist de Inicio

- [ ] InfrastructureService corriendo (MySQL, Redis, RabbitMQ)
- [ ] Base de datos inicializada (`init_database.py`)
- [ ] Java 17 instalado
- [ ] Archivo `.env` configurado
- [ ] Script `start.sh` con permisos de ejecución
- [ ] Servicio iniciado (`./start.sh`)
- [ ] Registro de usuario exitoso
- [ ] Login exitoso con token JWT

---

**¡Listo para desarrollar! 🚀**
