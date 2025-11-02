#!/bin/bash

# Script para iniciar todos los servicios de Flowlite
# ====================================================
# Orden de inicio:
# 1. InfrastructureService (MySQL, Redis, RabbitMQ)
# 2. IdentityService (puerto 8000)
# 3. InsightService (consumidor RabbitMQ)
# 4. UploadService (puerto 8001)

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directorio raíz del proyecto (compatible con bash y zsh)
if [ -n "$BASH_SOURCE" ]; then
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
fi

# Archivo para guardar PIDs de los servicios
PID_FILE="$PROJECT_ROOT/.flowlite_services.pid"

# ============================================
# FUNCIONES AUXILIARES
# ============================================

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Puerto en uso
    else
        return 1  # Puerto libre
    fi
}

# Función para esperar que un puerto esté disponible (para servicios sin health)
wait_for_port() {
    local port=$1
    local service=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Esperando que $service esté disponible en puerto $port...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if check_port $port; then
            echo -e "${GREEN}✓${NC} $service está disponible"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo -e "${RED}✗${NC} Timeout esperando $service"
    return 1
}

# Función para esperar que un servicio esté saludable vía HTTP
wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Esperando que $service esté saludable en $url...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if curl -fs "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $service está saludable"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo -e "${RED}✗${NC} Timeout esperando $service (no responde en $url)"
    return 1
}

# Función para verificar si un servicio docker está corriendo
check_docker_service() {
    local service_name=$1
    if docker ps --format '{{.Names}}' | grep -q "^${service_name}$"; then
        return 0  # Corriendo
    else
        return 1  # No corriendo
    fi
}

# ============================================
# INICIO DEL SCRIPT
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      🚀 INICIANDO FLOWLITE - PERSONAL FINANCE      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Limpiar archivo de PIDs si existe
> "$PID_FILE"

# Crear directorio de logs si no existe
mkdir -p "$PROJECT_ROOT/logs"

# ============================================
# 1. INFRASTRUCTURE SERVICE
# ============================================
echo -e "${BLUE}[1/5]${NC} Iniciando InfrastructureService..."
echo "      (MySQL, Redis, RabbitMQ)"
echo ""

cd "$PROJECT_ROOT/InfrastructureService"

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}✗${NC} Error: No se encontró docker-compose.yml en InfrastructureService"
    exit 1
fi

# Iniciar contenedores
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Error al iniciar InfrastructureService"
    exit 1
fi

echo -e "${GREEN}✓${NC} InfrastructureService iniciado"
echo ""

# Esperar a que los servicios estén listos
echo -e "${YELLOW}⏳ Esperando que los servicios de infraestructura estén listos...${NC}"
sleep 5

# Verificar MySQL
if check_docker_service "flowlite-mysql"; then
    echo -e "${GREEN}✓${NC} MySQL está corriendo"
else
    echo -e "${RED}✗${NC} MySQL no está corriendo"
fi

# Verificar Redis
if check_docker_service "flowlite-redis"; then
    echo -e "${GREEN}✓${NC} Redis está corriendo"
else
    echo -e "${RED}✗${NC} Redis no está corriendo"
fi

# Verificar RabbitMQ
if check_docker_service "flowlite-rabbitmq"; then
    echo -e "${GREEN}✓${NC} RabbitMQ está corriendo"
else
    echo -e "${RED}✗${NC} RabbitMQ no está corriendo"
fi

echo ""
sleep 2

# ============================================
# 1.5. MAILHOG SERVICE
# ============================================
echo -e "${BLUE}[1.5/5]${NC} Iniciando MailHog..."
echo "      (SMTP Mock Server para desarrollo)"
echo ""

cd "$PROJECT_ROOT/mailhog"

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}⚠️  No se encontró docker-compose.yml en mailhog. Saltando...${NC}"
else
    # Iniciar MailHog
    docker-compose up -d

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗${NC} Error al iniciar MailHog"
        # No exit, continuar sin MailHog
    else
        echo -e "${GREEN}✓${NC} MailHog iniciado"

        # Verificar MailHog
        sleep 2
        if check_docker_service "flowlite-mailhog"; then
            echo -e "${GREEN}✓${NC} MailHog está corriendo"
            echo -e "${CYAN}   📧 Web UI: http://localhost:8025${NC}"
            echo -e "${CYAN}   📨 SMTP: localhost:1025${NC}"
        else
            echo -e "${YELLOW}⚠️${NC} MailHog no está corriendo"
        fi
    fi
fi

echo ""
sleep 2

# ============================================
# 2. IDENTITY SERVICE
# ============================================
echo -e "${BLUE}[2/5]${NC} Iniciando IdentityService (puerto 8000)..."
echo ""

cd "$PROJECT_ROOT/identifyservice"

if [ ! -f "start.sh" ]; then
    echo -e "${RED}✗${NC} Error: No se encontró start.sh en identifyservice"
    exit 1
fi

# Verificar si el puerto está en uso
if check_port 8000; then
    echo -e "${YELLOW}⚠️  IdentityService ya está corriendo en el puerto 8000. Saltando arranque...${NC}"
    echo "identifyservice:EXTERNAL" >> "$PID_FILE"
    echo -e "${GREEN}✓${NC} IdentityService detectado como iniciado correctamente"
else
    # Iniciar servicio en background y guardar PID
    nohup ./start.sh > "$PROJECT_ROOT/logs/identifyservice.log" 2>&1 &
    IDENTITY_PID=$!
    echo "identifyservice:$IDENTITY_PID" >> "$PID_FILE"
    echo -e "${YELLOW}⏳ Iniciando IdentityService (PID: $IDENTITY_PID)...${NC}"
    # Esperar a que el servicio esté saludable
    if wait_for_service "http://localhost:8000/actuator/health" "IdentityService"; then
        echo -e "${GREEN}✓${NC} IdentityService iniciado correctamente"
    else
        echo -e "${RED}✗${NC} Error al iniciar IdentityService"
        exit 1
    fi
fi

echo ""
sleep 2

# ============================================
# 3. INSIGHT SERVICE
# ============================================
echo -e "${BLUE}[3/5]${NC} Iniciando InsightService (puerto 8002 + RabbitMQ consumer)..."
echo ""

cd "$PROJECT_ROOT/InsightService"

if [ ! -f "start.sh" ]; then
    echo -e "${RED}✗${NC} Error: No se encontró start.sh en InsightService"
    exit 1
fi

# Verificar si el puerto está en uso
if check_port 8002; then
    echo -e "${YELLOW}⚠️  Puerto 8002 ya está en uso. Deteniendo proceso...${NC}"
    lsof -ti:8002 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Iniciar servicio en background y guardar PID
nohup ./start.sh > "$PROJECT_ROOT/logs/insightservice.log" 2>&1 &
INSIGHT_PID=$!
echo "insightservice:$INSIGHT_PID" >> "$PID_FILE"

echo -e "${YELLOW}⏳ Iniciando InsightService (PID: $INSIGHT_PID)...${NC}"

# Esperar a que el servicio esté saludable (por HTTP)
if wait_for_service "http://localhost:8002/health" "InsightService API"; then
    echo -e "${GREEN}✓${NC} InsightService iniciado correctamente"
else
    echo -e "${RED}✗${NC} Error al iniciar InsightService"
    echo "Ver logs en: $PROJECT_ROOT/logs/insightservice.log"
    # No exit, continuar con UploadService
fi

echo ""
sleep 2

# ============================================
# 4. UPLOAD SERVICE
# ============================================
echo -e "${BLUE}[4/5]${NC} Iniciando UploadService (puerto 8001)..."
echo ""

cd "$PROJECT_ROOT/uploadservice"

if [ ! -f "start.sh" ]; then
    echo -e "${RED}✗${NC} Error: No se encontró start.sh en uploadservice"
    exit 1
fi

# Verificar si el puerto está en uso
if check_port 8001; then
    echo -e "${YELLOW}⚠️  Puerto 8001 ya está en uso. Deteniendo proceso...${NC}"
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Iniciar servicio en background y guardar PID
nohup bash ./start.sh > "$PROJECT_ROOT/logs/uploadservice.log" 2>&1 &
UPLOAD_PID=$!
echo "uploadservice:$UPLOAD_PID" >> "$PID_FILE"

echo -e "${YELLOW}⏳ Iniciando UploadService (PID: $UPLOAD_PID)...${NC}"


# Esperar a que el servicio esté saludable (por HTTP)
if wait_for_service "http://localhost:8001/api/v1/health" "UploadService"; then
    echo -e "${GREEN}✓${NC} UploadService iniciado correctamente"
else
    echo -e "${RED}✗${NC} Error al iniciar UploadService"
    echo "Ver logs en: $PROJECT_ROOT/logs/uploadservice.log"
    exit 1
fi

echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ TODOS LOS SERVICIOS ESTÁN CORRIENDO${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}📋 Servicios activos:${NC}"
echo ""
echo -e "  ${GREEN}✓${NC} InfrastructureService"
echo "      • MySQL:    localhost:3306"
echo "      • Redis:    localhost:6379"
echo "      • RabbitMQ: localhost:5672 (UI: http://localhost:15672)"
echo ""
echo -e "  ${GREEN}✓${NC} MailHog (SMTP Mock Server)"
echo "      • Web UI:   http://localhost:8025"
echo "      • SMTP:     localhost:1025"
echo ""
echo -e "  ${GREEN}✓${NC} IdentityService (PID: $IDENTITY_PID)"
echo "      • API:      http://localhost:8000"
echo "      • Swagger:  http://localhost:8000/swagger-ui/index.html"
echo "      • API Docs: http://localhost:8000/v3/api-docs"
echo "      • Health:   http://localhost:8000/actuator/health"
echo ""
echo -e "  ${GREEN}✓${NC} InsightService (PID: $INSIGHT_PID)"
echo "      • API:      http://localhost:8002"
echo "      • Health:   http://localhost:8002/health"
echo "      • Docs:     http://localhost:8002/docs"
echo "      • Consumer: RabbitMQ queue 'batch_processed'"
echo "      • LLM:      Conectado a Ollama"
echo ""
echo -e "  ${GREEN}✓${NC} UploadService (PID: $UPLOAD_PID)"
echo "      • API:      http://localhost:8001"
echo "      • Docs:     http://localhost:8001/docs"
echo "      • Health:   http://localhost:8001/health"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📁 Logs disponibles en:${NC}"
echo "   • IdentityService: $PROJECT_ROOT/logs/identifyservice.log"
echo "   • InsightService:  $PROJECT_ROOT/logs/insightservice.log"
echo "   • UploadService:   $PROJECT_ROOT/logs/uploadservice.log"
echo ""
echo -e "${YELLOW}🛑 Para detener todos los servicios:${NC}"
echo "   ./destroy_app.sh"
echo ""
echo -e "${YELLOW}📊 Para ver logs en tiempo real:${NC}"
echo "   tail -f logs/identifyservice.log"
echo "   tail -f logs/uploadservice.log"
echo "   tail -f logs/insightservice.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
