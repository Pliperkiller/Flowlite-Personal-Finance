#!/bin/bash

# Script para detener todos los servicios de Flowlite
# ====================================================
# Orden de detención (inverso al inicio):
# 1. DataService
# 2. UploadService
# 3. InsightService
# 4. IdentityService
# 5. InfrastructureService (MySQL, Redis, RabbitMQ)

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

# Archivo de PIDs
PID_FILE="$PROJECT_ROOT/.flowlite_services.pid"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      🛑 DETENIENDO FLOWLITE - PERSONAL FINANCE      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cargar variables de entorno globales para obtener los puertos
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# Establecer puertos por defecto si no están definidos
export IDENTITY_SERVICE_PORT=${IDENTITY_SERVICE_PORT:-8000}
export UPLOAD_SERVICE_PORT=${UPLOAD_SERVICE_PORT:-8001}
export INSIGHT_SERVICE_PORT=${INSIGHT_SERVICE_PORT:-8002}
export DATA_SERVICE_PORT=${DATA_SERVICE_PORT:-8003}

# Función para matar proceso por PID
kill_process() {
    local pid=$1
    local service_name=$2

    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${YELLOW}⏳ Deteniendo $service_name (PID: $pid)...${NC}"
        kill $pid 2>/dev/null
        sleep 2

        # Si aún está corriendo, forzar
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Forzando detención de $service_name...${NC}"
            kill -9 $pid 2>/dev/null
            sleep 1
        fi

        if ! ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $service_name detenido"
        else
            echo -e "${RED}✗${NC} No se pudo detener $service_name"
        fi
    else
        echo -e "${YELLOW}⚠️${NC}  $service_name no está corriendo (PID: $pid)"
    fi
}

# Función para matar proceso por puerto
kill_by_port() {
    local port=$1
    local service_name=$2

    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}⏳ Deteniendo $service_name en puerto $port (PID: $pid)...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        echo -e "${GREEN}✓${NC} $service_name detenido"
    else
        echo -e "${YELLOW}⚠️${NC}  No hay proceso corriendo en puerto $port"
    fi
}

# ============================================
# 1. DETENER DATA SERVICE
# ============================================
echo -e "${BLUE}[1/5]${NC} Deteniendo DataService..."
echo ""

# Intentar desde archivo de PIDs
if [ -f "$PID_FILE" ]; then
    DATA_PID=$(grep "dataservice:" "$PID_FILE" | cut -d: -f2)
    if [ ! -z "$DATA_PID" ]; then
        kill_process $DATA_PID "DataService"
    fi
fi

# Verificar por puerto como fallback
kill_by_port $DATA_SERVICE_PORT "DataService"

echo ""

# ============================================
# 2. DETENER UPLOAD SERVICE
# ============================================
echo -e "${BLUE}[2/5]${NC} Deteniendo UploadService..."
echo ""

# Intentar desde archivo de PIDs
if [ -f "$PID_FILE" ]; then
    UPLOAD_PID=$(grep "uploadservice:" "$PID_FILE" | cut -d: -f2)
    if [ ! -z "$UPLOAD_PID" ]; then
        kill_process $UPLOAD_PID "UploadService"
    fi
fi

# Verificar por puerto como fallback
kill_by_port $UPLOAD_SERVICE_PORT "UploadService"

echo ""

# ============================================
# 3. DETENER INSIGHT SERVICE
# ============================================
echo -e "${BLUE}[3/5]${NC} Deteniendo InsightService..."
echo ""

# Intentar desde archivo de PIDs
if [ -f "$PID_FILE" ]; then
    INSIGHT_PID=$(grep "insightservice:" "$PID_FILE" | cut -d: -f2)
    if [ ! -z "$INSIGHT_PID" ]; then
        kill_process $INSIGHT_PID "InsightService"
    fi
fi

# Buscar procesos de Python que ejecuten main.py de InsightService
INSIGHT_PIDS=$(ps aux | grep "[p]ython.*InsightService.*main.py" | awk '{print $2}')
if [ ! -z "$INSIGHT_PIDS" ]; then
    for pid in $INSIGHT_PIDS; do
        kill_process $pid "InsightService"
    done
fi

# Verificar por puerto como fallback
kill_by_port $INSIGHT_SERVICE_PORT "InsightService"

echo ""

# ============================================
# 4. DETENER IDENTITY SERVICE
# ============================================
echo -e "${BLUE}[4/5]${NC} Deteniendo IdentityService..."
echo ""

# Intentar desde archivo de PIDs
if [ -f "$PID_FILE" ]; then
    IDENTITY_PID=$(grep "identifyservice:" "$PID_FILE" | cut -d: -f2)
    if [ ! -z "$IDENTITY_PID" ]; then
        kill_process $IDENTITY_PID "IdentityService"
    fi
fi

# Verificar por puerto como fallback
kill_by_port $IDENTITY_SERVICE_PORT "IdentityService"

# Matar procesos Java de Gradle si quedaron activos
GRADLE_PIDS=$(ps aux | grep "[g]radle.*identifyservice" | awk '{print $2}')
if [ ! -z "$GRADLE_PIDS" ]; then
    echo -e "${YELLOW}⏳ Deteniendo procesos Gradle de IdentityService...${NC}"
    for pid in $GRADLE_PIDS; do
        kill -9 $pid 2>/dev/null
    done
    echo -e "${GREEN}✓${NC} Procesos Gradle detenidos"
fi

echo ""

# ============================================
# 5. DETENER INFRASTRUCTURE SERVICE
# ============================================
echo -e "${BLUE}[5/5]${NC} Deteniendo InfrastructureService..."
echo ""

cd "$PROJECT_ROOT/InfrastructureService"

if [ -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}⏳ Deteniendo contenedores Docker...${NC}"
    docker-compose down

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} InfrastructureService detenido"
        echo "      • MySQL detenido"
        echo "      • Redis detenido"
        echo "      • RabbitMQ detenido"
    else
        echo -e "${RED}✗${NC} Error al detener InfrastructureService"
    fi
else
    echo -e "${RED}✗${NC} No se encontró docker-compose.yml en InfrastructureService"
fi

echo ""

# ============================================
# LIMPIEZA
# ============================================
echo -e "${YELLOW}🧹 Limpiando archivos temporales...${NC}"

# Eliminar archivo de PIDs
if [ -f "$PID_FILE" ]; then
    rm "$PID_FILE"
    echo -e "${GREEN}✓${NC} Archivo de PIDs eliminado"
fi

# Limpiar logs antiguos (opcional)
if [ -d "$PROJECT_ROOT/logs" ]; then
    LOG_COUNT=$(ls -1 "$PROJECT_ROOT/logs" 2>/dev/null | wc -l)
    if [ $LOG_COUNT -gt 0 ]; then
        echo -e "${YELLOW}ℹ️${NC}  Logs guardados en: $PROJECT_ROOT/logs"
        echo "   Para limpiar logs: rm -rf logs/*.log"
    fi
fi

echo ""

# ============================================
# VERIFICACIÓN FINAL
# ============================================
echo -e "${YELLOW}🔍 Verificando puertos...${NC}"

# Verificar puerto IdentityService
if lsof -Pi :$IDENTITY_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗${NC} Puerto $IDENTITY_SERVICE_PORT (IdentityService) aún está en uso"
else
    echo -e "${GREEN}✓${NC} Puerto $IDENTITY_SERVICE_PORT (IdentityService) libre"
fi

# Verificar puerto UploadService
if lsof -Pi :$UPLOAD_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗${NC} Puerto $UPLOAD_SERVICE_PORT (UploadService) aún está en uso"
else
    echo -e "${GREEN}✓${NC} Puerto $UPLOAD_SERVICE_PORT (UploadService) libre"
fi

# Verificar puerto InsightService
if lsof -Pi :$INSIGHT_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗${NC} Puerto $INSIGHT_SERVICE_PORT (InsightService) aún está en uso"
else
    echo -e "${GREEN}✓${NC} Puerto $INSIGHT_SERVICE_PORT (InsightService) libre"
fi

# Verificar puerto DataService
if lsof -Pi :$DATA_SERVICE_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗${NC} Puerto $DATA_SERVICE_PORT (DataService) aún está en uso"
else
    echo -e "${GREEN}✓${NC} Puerto $DATA_SERVICE_PORT (DataService) libre"
fi

# Verificar contenedores Docker
DOCKER_COUNT=$(docker ps --filter "name=flowlite" --format '{{.Names}}' | wc -l)
if [ $DOCKER_COUNT -gt 0 ]; then
    echo -e "${RED}✗${NC} Algunos contenedores Docker aún están corriendo:"
    docker ps --filter "name=flowlite" --format "   • {{.Names}}"
else
    echo -e "${GREEN}✓${NC} No hay contenedores Docker corriendo"
fi

echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ TODOS LOS SERVICIOS HAN SIDO DETENIDOS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}📋 Servicios detenidos:${NC}"
echo -e "  ${GREEN}✓${NC} DataService"
echo -e "  ${GREEN}✓${NC} UploadService"
echo -e "  ${GREEN}✓${NC} InsightService"
echo -e "  ${GREEN}✓${NC} IdentityService"
echo -e "  ${GREEN}✓${NC} InfrastructureService (MySQL, Redis, RabbitMQ)"
echo ""
echo -e "${YELLOW}🚀 Para iniciar los servicios nuevamente:${NC}"
echo "   ./build_app.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""