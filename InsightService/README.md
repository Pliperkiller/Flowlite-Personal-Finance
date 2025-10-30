# Financial Insights Service

Servicio de recomendaciones financieras impulsado por IA que analiza transacciones de usuarios y genera insights personalizados mediante un modelo LLM remoto.

## Características

- **API HTTP (Puerto 8002)**: Health checks, monitoreo y verificación de componentes
- **Consumidor RabbitMQ**: Procesamiento asíncrono de eventos de transacciones
- **Generación de Insights con IA**: Integración con Ollama (LLM llama3.1:8b)
- **Persistencia**: Almacenamiento de insights en MySQL

## Arquitectura

- **Clean Architecture** con clara separación de responsabilidades
- **Domain-Driven Design** (DDD)
- **Dependency Injection** para bajo acoplamiento
- **Repository Pattern** para acceso a datos
- **Integración LLM remota** vía Ollama para privacidad y eficiencia
- **Event-Driven Architecture** mediante RabbitMQ
- **API REST** con FastAPI para monitoreo

## Prerequisitos

- Python 3.11+
- **InfrastructureService** corriendo (MySQL y RabbitMQ)
- Acceso a servidor remoto con Ollama y modelo llama3.1:8b

## Importante

Este servicio requiere que **InfrastructureService** esté corriendo primero, ya que proporciona:
- Base de datos MySQL compartida (flowlite_db)
- RabbitMQ para mensajería
- Migraciones de base de datos

**NO es necesario** ejecutar migraciones ni inicializar la base de datos desde este servicio.

## Conexión al Servidor LLM Remoto

Este servicio se conecta a un servidor que ejecuta Ollama para generar insights usando modelos de lenguaje.

**Configuración en .env:**
```bash
# Servidor Ollama local
OLLAMA_HOST=http://localhost:11434

# O servidor remoto
OLLAMA_HOST=http://IP_SERVIDOR:11434
```

**Nota:** Si usas un servidor remoto, asegúrate de que el firewall permita conexiones en el puerto 11434.

## Inicio Rápido

### 1. Iniciar InfrastructureService

**PRIMERO** debes iniciar la infraestructura compartida:

```bash
cd ../InfrastructureService

# Iniciar MySQL y RabbitMQ
docker-compose up -d

# Verificar que los servicios estén corriendo
docker-compose ps

# Ejecutar migraciones (solo la primera vez)
export DATABASE_URL="mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db"
alembic upgrade head
```

Ver más detalles en `InfrastructureService/README.md`

### 2. Instalar Dependencias

```bash
cd InsightService

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus configuraciones
nano .env
```

**Variables principales:**
```bash
# Base de datos MySQL (debe coincidir con InfrastructureService)
DATABASE_URL=mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db

# RabbitMQ (debe coincidir con InfrastructureService)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_QUEUE=batch_processed

# Servidor LLM (Ollama)
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=llama3.1:8b
```

### 4. Verificar Conexión a Ollama

```bash
# Probar endpoint de Ollama
curl http://localhost:11434/api/tags

# O si usas servidor remoto
curl http://IP_SERVIDOR:11434/api/tags
```

### 5. Ejecutar el Servicio

```bash
python main.py
```

El servicio iniciará:
- Servidor HTTP en puerto 8002 para health checks y monitoreo
- Consumidor RabbitMQ para procesar eventos de transacciones

## Endpoints API

Una vez iniciado, el servicio expone los siguientes endpoints HTTP:

```
GET  /health       - Health check básico
GET  /health/db    - Verificar conexión a base de datos
GET  /health/full  - Health check completo de todos los componentes
GET  /info         - Información del servicio y configuración
GET  /docs         - Documentación interactiva (Swagger UI)
```

**Ejemplo de uso**:
```bash
# Health check
curl http://localhost:8002/health

# Database check
curl http://localhost:8002/health/db

# Ver documentación
open http://localhost:8002/docs
```

### 6. Probar el Servicio

```bash
# En otra terminal
python scripts/send_test_message.py <user_id> <batch_id>

# Revisar logs para ver la generación de insights
```

## Estructura del Proyecto

```
InsightService/
├── src/
│   ├── domain/              # Lógica de negocio y entidades
│   ├── application/         # Casos de uso y servicios
│   ├── infrastructure/      # Integraciones externas
│   │   ├── database/        # MySQL (conexión a BD compartida)
│   │   ├── llm/             # Cliente Ollama
│   │   ├── messaging/       # RabbitMQ Consumer
│   │   └── config/          # Configuración
│   └── interfaces/          # Adaptadores
├── scripts/                 # Scripts de utilidad
├── main.py                  # Punto de entrada
└── requirements.txt
```

## Servicios de Infraestructura

La infraestructura (MySQL y RabbitMQ) se gestiona desde **InfrastructureService**.

### URLs de Servicios

- **MySQL**: `localhost:3306`
- **RabbitMQ AMQP**: `localhost:5672`
- **RabbitMQ Management UI**: http://localhost:15672

### Gestión de Infraestructura

```bash
cd ../InfrastructureService

# Ver servicios corriendo
docker-compose ps

# Ver logs
docker-compose logs -f mysql
docker-compose logs -f rabbitmq

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down
```

## Pruebas

```bash
# Pruebas unitarias
pytest tests/

# Con cobertura
pytest --cov=src tests/
```

## Resolución de Problemas

### Error de conexión a Ollama

```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Si usas servidor remoto, verificar conectividad
ping IP_SERVIDOR
curl http://IP_SERVIDOR:11434/api/tags

# Verificar que el modelo esté instalado
ollama list
```

### Error de conexión a RabbitMQ

```bash
# Verificar estado del contenedor
docker-compose ps rabbitmq

# Ver logs
docker-compose logs rabbitmq

# Reiniciar
docker-compose restart rabbitmq
```

### Error de conexión a MySQL

```bash
# Verificar contenedor (desde InfrastructureService)
cd ../InfrastructureService
docker-compose ps mysql

# Probar conexión
docker exec -it flowlite-mysql mysql -u flowlite_user -p flowlite_db

# Verificar que las migraciones estén aplicadas
alembic current
```

## Seguridad

**IMPORTANTE:** Este proyecto utiliza configuración basada en variables de entorno.

**NO COMMITEAR:**
- Archivo `.env` con credenciales reales
- Scripts con credenciales hardcodeadas
- Dumps de base de datos

**Verificar `.gitignore` antes de hacer commit.**

## Configuración de Producción

Para despliegue en producción:

1. Usar variables de entorno del sistema operativo
2. Configurar certificados SSL/TLS para conexiones
3. Implementar autenticación robusta en RabbitMQ
4. Usar secrets managers (AWS Secrets Manager, HashiCorp Vault, etc.)
5. Asegurar el acceso al servidor LLM (firewall, autenticación)
6. Implementar monitoreo y alertas

## Licencia

[Especificar licencia]
