# Financial Insights Service

Servicio de recomendaciones financieras impulsado por IA que analiza transacciones de usuarios y genera insights personalizados mediante un modelo LLM remoto.

## Arquitectura

- **Clean Architecture** con clara separación de responsabilidades
- **Domain-Driven Design** (DDD)
- **Dependency Injection** para bajo acoplamiento
- **Repository Pattern** para acceso a datos
- **Integración LLM remota** vía Ollama para privacidad y eficiencia

## Prerequisitos

- Python 3.11+
- PostgreSQL
- RabbitMQ
- Acceso a servidor remoto con Ollama y modelo llama3.1:8b
- Docker y Docker Compose (opcional, para PostgreSQL y RabbitMQ locales)

## Conexión al Servidor LLM Remoto

Este servicio se conecta a un servidor remoto que ejecuta Ollama. Existen dos métodos de conexión:

### Opción 1: Túnel SSH (Recomendado)

Conexión segura y encriptada sin exponer el servidor Ollama públicamente.

**Configuración:**
```bash
# Configurar variables de entorno
export OLLAMA_REMOTE_USER=tu_usuario
export OLLAMA_REMOTE_HOST=ip_del_servidor

# Iniciar túnel SSH
./scripts/start_ollama_tunnel.sh

# En .env configurar:
OLLAMA_HOST=http://localhost:11434
```

**Ventajas:**
- Conexión encriptada
- No requiere abrir firewall
- Seguro para redes públicas

### Opción 2: Conexión Directa

Conexión directa al servidor remoto (solo para redes internas/privadas).

**Configuración en .env:**
```bash
OLLAMA_HOST=http://IP_SERVIDOR:11434
```

**Nota:** Asegúrate de que el firewall del servidor permita conexiones en el puerto 11434.

## Inicio Rápido

### 1. Clonar e Instalar Dependencias

```bash
# Clonar repositorio
git clone <tu-repositorio>
cd InsightService

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus configuraciones
nano .env
```

**Variables principales:**
```bash
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Servidor LLM remoto
OLLAMA_HOST=http://localhost:11434  # Si usas túnel SSH
# O
OLLAMA_HOST=http://IP_SERVIDOR:11434  # Conexión directa
```

### 3. Iniciar Servicios de Infraestructura

**Opción A: Con Docker Compose (Recomendado para desarrollo)**

```bash
# Iniciar PostgreSQL y RabbitMQ
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

**Opción B: Servicios locales instalados**

Asegúrate de que PostgreSQL y RabbitMQ estén ejecutándose en tu sistema.

### 4. Conectar al Servidor LLM Remoto

**Si usas túnel SSH:**
```bash
# Terminal separado - mantener abierto
export OLLAMA_REMOTE_USER=tu_usuario
export OLLAMA_REMOTE_HOST=192.168.1.100  # IP del servidor
./scripts/start_ollama_tunnel.sh
```

**Si usas conexión directa:**
```bash
# Verificar conectividad
curl http://IP_SERVIDOR:11434/api/tags
```

### 5. Configurar Base de Datos

```bash
# Ejecutar migraciones
alembic upgrade head

# Cargar datos de prueba (opcional)
python scripts/seed_database.py
```

### 6. Ejecutar el Servicio

```bash
python main.py
```

El servicio comenzará a escuchar mensajes de RabbitMQ y generará insights usando el LLM remoto.

### 7. Probar el Servicio

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
│   │   ├── database/        # PostgreSQL
│   │   ├── llm/             # Cliente Ollama
│   │   ├── messaging/       # RabbitMQ
│   │   └── config/          # Configuración
│   └── interfaces/          # Adaptadores
├── scripts/                 # Scripts de utilidad
├── alembic/                 # Migraciones de BD
├── main.py                  # Punto de entrada
└── requirements.txt
```

## Administración de Servicios Docker

### Comandos Básicos

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose stop

# Ver logs
docker-compose logs -f postgres
docker-compose logs -f rabbitmq

# Reiniciar servicio específico
docker-compose restart postgres

# Detener y eliminar contenedores
docker-compose down

# ADVERTENCIA: Eliminar también los volúmenes (pérdida de datos)
docker-compose down -v
```

### URLs de Servicios

- **PostgreSQL**: `localhost:5432`
- **RabbitMQ AMQP**: `localhost:5672`
- **RabbitMQ Management UI**: http://localhost:15672

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
# Verificar conectividad al servidor remoto
ping IP_SERVIDOR

# Verificar túnel SSH (si aplica)
ps aux | grep ssh

# Probar endpoint de Ollama
curl http://localhost:11434/api/tags  # Con túnel
curl http://IP_SERVIDOR:11434/api/tags  # Directo
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

### Error de conexión a PostgreSQL

```bash
# Verificar contenedor
docker-compose ps postgres

# Probar conexión
psql -h localhost -U postgres -d insights_db

# Reiniciar migraciones
alembic downgrade base
alembic upgrade head
```

## Seguridad

**IMPORTANTE:** Este proyecto utiliza configuración basada en variables de entorno.

**NO COMMITEAR:**
- Archivo `.env` con credenciales reales
- Scripts con credenciales hardcodeadas
- Dumps de base de datos
- Llaves SSH o certificados

**Verificar `.gitignore` antes de hacer commit.**

## Configuración de Producción

Para despliegue en producción:

1. Usar variables de entorno del sistema operativo
2. Configurar certificados SSL/TLS para conexiones
3. Implementar autenticación robusta en RabbitMQ
4. Usar secrets managers (AWS Secrets Manager, HashiCorp Vault, etc.)
5. Configurar firewall y VPN para acceso al servidor LLM
6. Implementar monitoreo y alertas

## Licencia

[Especificar licencia]
