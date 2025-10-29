# 🎛️ Dashboard de Monitoreo - Flowlite

Dashboard web interactivo para monitorear en tiempo real todos los servicios y componentes de la plataforma Flowlite.

## 🚀 Inicio Rápido

```bash
# Opción 1: Desde terminal
open dashboard.html

# Opción 2: Navegar directamente
# Abre en tu navegador: file:///ruta/al/proyecto/dashboard.html
```

## 📋 Características

### Monitoreo en Tiempo Real

- **Auto-refresh**: Actualización automática cada 10 segundos
- **Refresh manual**: Botón para actualizar manualmente cuando lo necesites
- **Indicadores visuales**: Códigos de colores intuitivos (verde=ok, rojo=error, amarillo=advertencia)
- **Animaciones**: Indicadores pulsantes para mostrar estado activo

### Servicios Monitoreados

#### 1. IdentityService (Puerto 8000)
- **Estado general**: UP/DOWN
- **Componentes**:
  - 🗄️ Database (MySQL)
  - ⚡ Redis (Cache)
  - 🏓 Ping (Conectividad)

#### 2. UploadService (Puerto 8001)
- **Estado general**: healthy/unhealthy
- Health check básico del servicio

#### 3. InsightService (Puerto 8002)
- **Estado general**: healthy/unhealthy/degraded
- **Componentes**:
  - 🗄️ Database (MySQL)
  - 🐰 RabbitMQ (Message Queue)
  - 🤖 LLM (Ollama - Modelo de IA)

### Infraestructura

Sección dedicada a mostrar los servicios de infraestructura:
- **MySQL** (localhost:3306)
- **Redis** (localhost:6379)
- **RabbitMQ** (localhost:5672)
- **RabbitMQ UI** (localhost:15672) - Incluye link directo

## 🎨 Interfaz del Dashboard

### Código de Colores

| Color | Estado | Significado |
|-------|--------|-------------|
| 🟢 Verde | Healthy / UP | Componente funcionando correctamente |
| 🔴 Rojo | Unhealthy / DOWN | Componente con error o no disponible |
| 🟡 Amarillo | Degraded / Warning | Componente con advertencias |
| ⚪ Gris | Unknown | Estado desconocido o no configurado |

### Tarjetas de Servicio

Cada servicio se muestra en una tarjeta con:
- **Nombre e icono** del servicio
- **Badge de estado** en la esquina superior derecha
- **URL principal** del servicio (clickeable)
- **Link a documentación** API (clickeable)
- **Lista de componentes** con su estado individual
- **Mensajes de error** si existen problemas

### Efectos Visuales

- **Hover effects**: Las tarjetas se elevan al pasar el cursor
- **Animación de pulso**: Los indicadores de estado tienen animación continua
- **Spinner de carga**: Indicador visual mientras se cargan los datos
- **Responsive design**: Se adapta a diferentes tamaños de pantalla

## 🔧 Configuración

### Auto-refresh

Por defecto, el dashboard se actualiza automáticamente cada 10 segundos. Puedes:

1. **Desactivar auto-refresh**: Desmarca el checkbox "Auto-refresh cada 10 segundos"
2. **Activar auto-refresh**: Marca el checkbox nuevamente
3. **Refresh manual**: Haz clic en el botón "🔄 Refrescar Ahora" en cualquier momento

### Timeout de Peticiones

- Las peticiones HTTP tienen un timeout de **5 segundos**
- Si un servicio no responde en ese tiempo, se marca como "unhealthy"
- El error mostrado será "Timeout"

## 📊 Endpoints Consultados

El dashboard hace peticiones a los siguientes endpoints:

```javascript
// IdentityService
GET http://localhost:8000/actuator/health

// UploadService
GET http://localhost:8001/health

// InsightService
GET http://localhost:8002/health/full
```

## 🔍 Interpretación de Estados

### IdentityService

**Formato de respuesta (Spring Boot Actuator)**:
```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP" },
    "redis": { "status": "UP" },
    "ping": { "status": "UP" }
  }
}
```

### UploadService

**Formato de respuesta (FastAPI)**:
```json
{
  "status": "ok"
}
```

### InsightService

**Formato de respuesta (FastAPI personalizado)**:
```json
{
  "service": "InsightService",
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "type": "MySQL"
    },
    "rabbitmq": {
      "status": "configured",
      "queue": "batch_processed"
    },
    "llm": {
      "status": "configured",
      "host": "http://localhost:11434",
      "model": "llama3.1:8b"
    }
  }
}
```

## 🐛 Solución de Problemas

### Dashboard no carga los servicios

**Problema**: Todas las tarjetas muestran "unhealthy" o errores de conexión.

**Causas comunes**:
1. Los servicios no están corriendo
2. CORS está bloqueando las peticiones (navegador)
3. Timeout en las peticiones

**Solución**:
```bash
# 1. Verificar que los servicios estén corriendo
./build_app.sh

# 2. Verificar puertos con lsof
lsof -i :8000  # IdentityService
lsof -i :8001  # UploadService
lsof -i :8002  # InsightService

# 3. Verificar logs
tail -f logs/identifyservice.log
tail -f logs/uploadservice.log
tail -f logs/insightservice.log
```

### Error de CORS

**Problema**: El navegador bloquea peticiones por política de CORS.

**Nota**: Este dashboard hace peticiones desde `file://` a `http://localhost:*`, lo cual puede causar problemas de CORS en algunos navegadores.

**Solución alternativa**: Servir el dashboard desde un servidor HTTP simple:

```bash
# Opción 1: Python
python3 -m http.server 3000

# Opción 2: Node.js (si tienes http-server instalado)
npx http-server -p 3000

# Luego abrir:
open http://localhost:3000/dashboard.html
```

### Componente muestra estado "unknown"

**Problema**: Un componente no muestra su estado correcto.

**Causas**:
1. El endpoint de health check no retorna el formato esperado
2. El componente no está configurado en el servicio

**Verificación**:
```bash
# Verificar respuesta directamente
curl http://localhost:8002/health/full | jq
```

## 📱 Compatibilidad

### Navegadores Soportados

- ✅ Chrome/Edge (versión 90+)
- ✅ Firefox (versión 88+)
- ✅ Safari (versión 14+)
- ✅ Opera (versión 76+)

### Dispositivos

- ✅ Desktop (óptimo)
- ✅ Tablet (responsive)
- ✅ Mobile (responsive, tamaño mínimo recomendado: 350px)

## 🎯 Casos de Uso

### 1. Monitoreo durante Desarrollo

Mantén el dashboard abierto mientras desarrollas para:
- Ver inmediatamente cuando un servicio se cae
- Verificar que los componentes siguen funcionando después de cambios
- Detectar problemas de configuración rápidamente

### 2. Presentaciones y Demos

- Muestra el estado de toda la plataforma en una sola pantalla
- Demuestra la arquitectura de microservicios
- Visualiza la separación de responsabilidades

### 3. Troubleshooting

- Identifica rápidamente qué servicio tiene problemas
- Ve qué componente específico está fallando
- Accede directamente a la documentación de cada servicio

## 🚀 Mejoras Futuras

Posibles mejoras para el dashboard:

- [ ] Historial de estados (gráficas de uptime)
- [ ] Notificaciones de escritorio cuando un servicio falla
- [ ] Métricas de rendimiento (latencia, throughput)
- [ ] Logs en tiempo real integrados
- [ ] Configuración de intervalos de refresh personalizados
- [ ] Exportar reporte de estado
- [ ] Integración con alertas (email, Slack, etc.)
- [ ] Dark mode

## 🔐 Seguridad

**IMPORTANTE**: Este dashboard es para **uso local en desarrollo**.

Para producción, considera:
- ✅ Autenticación para acceder al dashboard
- ✅ HTTPS para todas las conexiones
- ✅ Restricción de IPs permitidas
- ✅ API Gateway para centralizar health checks
- ✅ Rate limiting en los endpoints
- ✅ No exponer detalles internos del sistema

## 📚 Referencias

- [Spring Boot Actuator](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
- [FastAPI Health Checks](https://fastapi.tiangolo.com/)
- [Health Check Pattern](https://microservices.io/patterns/observability/health-check-api.html)

---

**Dashboard creado para**: Flowlite Personal Finance Platform
**Versión**: 1.0.0
**Última actualización**: Octubre 2024
