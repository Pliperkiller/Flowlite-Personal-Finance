# 🐳 Docker - Identify Service

Este documento contiene las instrucciones para ejecutar el servicio de identificación (identifyservice) usando Docker.

## 📋 Prerrequisitos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 2.0 o superior)
- Al menos 2GB de RAM disponible
- Puerto 8080 y 3306 disponibles en tu sistema

## 🚀 Opciones de Despliegue

### Opción 1: Dockerfile Multi-stage (Recomendado)

```bash
# Construir la imagen (incluye compilación)
docker build -t flowlite-identifyservice .

# Ejecutar el contenedor
docker run -d \
  --name flowlite-identifyservice \
  -p 8080:8080 \
  -e SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/auth \
  -e SPRING_DATASOURCE_USERNAME=root \
  -e SPRING_DATASOURCE_PASSWORD=Flowlite10+ \
  flowlite-identifyservice
```

### Opción 2: Dockerfile Simple (Más rápido)

Si tienes problemas de red o quieres una construcción más rápida:

```bash
# Primero construir la aplicación localmente
./gradlew clean build -x test

# Luego construir la imagen Docker
docker build -f Dockerfile.simple -t flowlite-identifyservice .

# Ejecutar el contenedor
docker run -d \
  --name flowlite-identifyservice \
  -p 8080:8080 \
  -e SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/auth \
  -e SPRING_DATASOURCE_USERNAME=root \
  -e SPRING_DATASOURCE_PASSWORD=Flowlite10+ \
  flowlite-identifyservice
```

### Opción 2: Stack Completo con Docker Compose (Recomendado para producción)

```bash
# Ejecutar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f identifyservice

# Detener todos los servicios
docker-compose down
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SPRING_PROFILES_ACTIVE` | Perfil de Spring activo | `docker` |
| `SERVER_PORT` | Puerto del servidor | `8080` |
| `JWT_SECRET` | Clave secreta para JWT | `mi_clave_super_secreta_de_32_caracteres_minimo_123456789` |
| `SPRING_DATASOURCE_URL` | URL de conexión a la base de datos | `jdbc:mysql://mysql:3306/auth` |
| `SPRING_DATASOURCE_USERNAME` | Usuario de la base de datos | `root` |
| `SPRING_DATASOURCE_PASSWORD` | Contraseña de la base de datos | `Flowlite10+` |

### Puertos Expuestos

- **8080**: API del servicio de identificación
- **3306**: Base de datos MySQL (solo en docker-compose)
- **80**: Nginx proxy (solo en docker-compose)

## 📊 Monitoreo y Salud

### Health Checks

El contenedor incluye health checks automáticos:

```bash
# Verificar estado del contenedor
docker ps

# Ver logs de health check
docker inspect flowlite-identifyservice | grep -A 10 Health
```

### Endpoints de Monitoreo

- **Health Check**: `http://localhost:8080/actuator/health`
- **Swagger UI**: `http://localhost:8080/swagger-ui.html`
- **API Docs**: `http://localhost:8080/api-docs`

## 🛠️ Comandos Útiles

### Construcción y Ejecución

```bash
# Construir imagen
docker build -t flowlite-identifyservice .

# Ejecutar en modo interactivo (para debugging)
docker run -it --rm -p 8080:8080 flowlite-identifyservice

# Ejecutar con variables de entorno personalizadas
docker run -d \
  --name flowlite-identifyservice \
  -p 8080:8080 \
  -e JWT_SECRET=tu_clave_secreta_aqui \
  flowlite-identifyservice
```

### Gestión de Contenedores

```bash
# Ver contenedores en ejecución
docker ps

# Ver logs del servicio
docker logs flowlite-identifyservice

# Entrar al contenedor
docker exec -it flowlite-identifyservice sh

# Detener y eliminar contenedor
docker stop flowlite-identifyservice
docker rm flowlite-identifyservice
```

### Docker Compose

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs de un servicio específico
docker-compose logs -f identifyservice

# Reiniciar un servicio
docker-compose restart identifyservice

# Detener y eliminar volúmenes
docker-compose down -v
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **Puerto ya en uso**:
   ```bash
   # Cambiar puerto en docker-compose.yml o usar otro puerto
   docker run -p 8081:8080 flowlite-identifyservice
   ```

2. **Error de conexión a base de datos**:
   ```bash
   # Verificar que MySQL esté ejecutándose
   docker-compose ps mysql
   
   # Ver logs de MySQL
   docker-compose logs mysql
   ```

3. **Problemas de memoria**:
   ```bash
   # Aumentar memoria disponible para Docker
   # En Docker Desktop: Settings > Resources > Memory
   ```

### Logs y Debugging

```bash
# Ver logs detallados
docker logs --tail 100 -f flowlite-identifyservice

# Ver logs de todos los servicios
docker-compose logs

# Ejecutar con debug habilitado
docker run -e SPRING_JPA_SHOW_SQL=true flowlite-identifyservice
```

## 🔐 Seguridad

### Recomendaciones

1. **Cambiar credenciales por defecto**:
   - Modificar `JWT_SECRET` en producción
   - Cambiar contraseñas de base de datos
   - Usar variables de entorno para credenciales sensibles

2. **Configurar firewall**:
   - Solo exponer puertos necesarios
   - Usar HTTPS en producción

3. **Actualizar regularmente**:
   - Mantener imágenes base actualizadas
   - Revisar vulnerabilidades de seguridad

## 📝 Notas Adicionales

- El contenedor usa OpenJDK 17 con Alpine Linux para optimizar el tamaño
- Se ejecuta con un usuario no-root para mayor seguridad
- Incluye health checks automáticos
- Configurado para zona horaria de Colombia (America/Bogota)
- Optimizado para desarrollo y producción

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar los logs del contenedor
2. Verificar la configuración de variables de entorno
3. Consultar la documentación de Spring Boot
4. Revisar la configuración de red de Docker
