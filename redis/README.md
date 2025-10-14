# 🚀 Redis para Flowlite - Blacklist de Tokens

Este directorio contiene la configuración independiente de Redis para el sistema de blacklist de tokens JWT de Flowlite.

## 📁 Estructura

```
redis/
├── docker-compose.yml    # Configuración de Redis
├── manage-redis.sh        # Script de gestión
└── README.md             # Este archivo
```

## 🚀 Inicio Rápido

### 1. Iniciar Redis
```bash
cd redis
./manage-redis.sh start
```

### 2. Verificar Estado
```bash
./manage-redis.sh status
```

### 3. Conectar a Redis CLI
```bash
./manage-redis.sh connect
```

## 🔧 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `start` | Iniciar Redis |
| `stop` | Detener Redis |
| `restart` | Reiniciar Redis |
| `status` | Ver estado |
| `logs` | Ver logs |
| `connect` | Conectar a CLI |
| `clean` | Limpiar datos |
| `help` | Mostrar ayuda |

## ⚙️ Configuración

### Puerto
- **Puerto**: 6379
- **Host**: localhost

### Volúmenes
- **Datos**: `redis_data` (persistente)
- **Configuración**: In-memory con persistencia AOF

### Características
- ✅ **Persistencia**: AOF (Append Only File)
- ✅ **Memoria**: 256MB máximo
- ✅ **Política**: LRU (Least Recently Used)
- ✅ **Health Check**: Ping cada 30s
- ✅ **Restart**: Automático

## 🔗 Conexión desde Flowlite

### Variables de Entorno
```bash
SPRING_DATA_REDIS_HOST=localhost
SPRING_DATA_REDIS_PORT=6379
SPRING_DATA_REDIS_DATABASE=0
```

### Configuración en application.properties
```properties
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.database=0
```

## 🧪 Pruebas

### 1. Verificar Conexión
```bash
./manage-redis.sh connect
> ping
PONG
```

### 2. Probar Blacklist
```bash
./manage-redis.sh connect
> SADD revoked_tokens "test_token_123"
> SISMEMBER revoked_tokens "test_token_123"
> SMEMBERS revoked_tokens
```

### 3. Ver Estadísticas
```bash
./manage-redis.sh connect
> INFO memory
> INFO keyspace
```

## 🔍 Monitoreo

### Logs en Tiempo Real
```bash
./manage-redis.sh logs
```

### Estado del Contenedor
```bash
./manage-redis.sh status
```

### Información de Redis
```bash
./manage-redis.sh connect
> INFO
```

## 🛠️ Troubleshooting

### Redis No Inicia
```bash
# Ver logs
./manage-redis.sh logs

# Verificar puerto
netstat -tulpn | grep 6379
```

### Conexión Fallida
```bash
# Verificar contenedor
docker ps | grep redis

# Reiniciar
./manage-redis.sh restart
```

### Limpiar Datos
```bash
./manage-redis.sh clean
```

## 📊 Uso en Flowlite

### Estrategia de Revocación
```properties
# En application.properties
app.token-revocation.strategy=redis
```

### Endpoints de Blacklist
- `POST /auth/logout` - Revocar token
- `GET /auth/validate` - Validar token

### TTL Automático
- **Tokens revocados**: 30 días
- **Limpieza automática**: Por TTL
- **Memoria optimizada**: LRU policy

## 🔒 Seguridad

### Configuración de Red
- Redis solo accesible desde localhost
- No exposición externa por defecto
- Red interna para contenedores

### Persistencia
- Datos encriptados en disco
- Backup automático con AOF
- Recuperación ante fallos

## 📈 Escalabilidad

### Para Producción
- Usar Redis Cluster
- Configurar replicación
- Monitoreo con Redis Sentinel

### Para Desarrollo
- Redis standalone (actual)
- Persistencia local
- Configuración simple
