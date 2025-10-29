#!/bin/bash

# Script para iniciar el InsightService
# =====================================
# NOTA: Este servicio NO expone una API HTTP. Es un consumidor de mensajes
# RabbitMQ que genera insights financieros usando un modelo LLM.

echo "🚀 Iniciando InsightService..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo .env${NC}"
    echo "Por favor, crea un archivo .env con la configuración necesaria"
    echo "Puedes copiar .env.example y editarlo:"
    echo "  cp .env.example .env"
    exit 1
fi

echo -e "${GREEN}✓${NC} Archivo .env encontrado"

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  No se encontró el entorno virtual. Creándolo...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al crear el entorno virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
fi

# Activar entorno virtual
echo -e "${YELLOW}📦 Activando entorno virtual...${NC}"
source venv/bin/activate

# Instalar/actualizar dependencias
echo -e "${YELLOW}📦 Verificando dependencias...${NC}"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Dependencias instaladas"

# Cargar variables de entorno para verificación
echo -e "${YELLOW}🔧 Verificando configuración...${NC}"
source .env

# Verificar servicios externos
echo -e "${YELLOW}🔌 Verificando servicios externos...${NC}"

# MySQL
if command -v mysqladmin &> /dev/null; then
    if mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} MySQL: Conectado (localhost:3306)"
    else
        echo -e "  ${YELLOW}⚠${NC}  MySQL: No se pudo conectar"
    fi
else
    echo -e "  ${YELLOW}⚠${NC}  MySQL: No se pudo verificar (mysqladmin no encontrado)"
fi

# RabbitMQ
RABBITMQ_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://${RABBITMQ_HOST}:15672 2>/dev/null)
if [ "$RABBITMQ_STATUS" = "200" ] || [ "$RABBITMQ_STATUS" = "401" ]; then
    echo -e "  ${GREEN}✓${NC} RabbitMQ: Conectado (${RABBITMQ_HOST}:${RABBITMQ_PORT})"
else
    echo -e "  ${YELLOW}⚠${NC}  RabbitMQ: No se pudo verificar"
fi

# Ollama (LLM)
OLLAMA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${OLLAMA_HOST}/api/tags 2>/dev/null)
if [ "$OLLAMA_STATUS" = "200" ]; then
    echo -e "  ${GREEN}✓${NC} Ollama LLM: Conectado (${OLLAMA_HOST})"
else
    echo -e "  ${RED}✗${NC} Ollama LLM: No se pudo conectar (${OLLAMA_HOST})"
    echo -e "    ${YELLOW}El servicio necesita Ollama para funcionar${NC}"
fi

echo ""
echo -e "${BLUE}ℹ️  Configuración:${NC}"
echo "  • Base de datos: ${DATABASE_URL##*@}"
echo "  • RabbitMQ: ${RABBITMQ_HOST}:${RABBITMQ_PORT}"
echo "  • Cola: ${RABBITMQ_QUEUE}"
echo "  • LLM Model: ${LLM_MODEL}"
echo "  • API Port: ${API_PORT:-8002}"
echo "  • Log Level: ${LOG_LEVEL:-INFO}"

echo ""
echo -e "${GREEN}✓${NC} Configuración completa"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎯 InsightService iniciado${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}🌐 API HTTP disponible:${NC}"
echo "   • Health Check: http://localhost:${API_PORT:-8002}/health"
echo "   • Database Check: http://localhost:${API_PORT:-8002}/health/db"
echo "   • Full Health: http://localhost:${API_PORT:-8002}/health/full"
echo "   • Service Info: http://localhost:${API_PORT:-8002}/info"
echo "   • API Docs: http://localhost:${API_PORT:-8002}/docs"
echo ""
echo -e "${YELLOW}📋 RabbitMQ Consumer:${NC}"
echo "   • Cola: ${RABBITMQ_QUEUE}"
echo "   • Escucha eventos de transacciones procesadas"
echo "   • Genera insights financieros usando IA"
echo "   • Guarda los insights en la base de datos"
echo ""
echo "Para detener el servicio, presiona Ctrl+C"
echo ""

# Iniciar el servicio
python main.py
