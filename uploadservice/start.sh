#!/bin/bash

# Script para iniciar el UploadService
# ====================================

echo "🚀 Iniciando UploadService..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: No se encontró el archivo .env${NC}"
    echo "Por favor, crea un archivo .env con la configuración necesaria"
    exit 1
fi

echo -e "${GREEN}✓${NC} Archivo .env encontrado"

# Verificar que existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  No se encontró el entorno virtual. Creándolo...${NC}"
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al crear el entorno virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
fi

# Activar entorno virtual
echo -e "${YELLOW}📦 Activando entorno virtual...${NC}"
source venv/Scripts/activate

# Instalar/actualizar dependencias
echo -e "${YELLOW}📦 Verificando dependencias...${NC}"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Dependencias instaladas"

# Cargar variables de entorno
echo -e "${YELLOW}🔧 Cargando variables de entorno...${NC}"
export $(cat .env | grep -v '^#' | xargs)
echo -e "${GREEN}✓${NC} Variables de entorno cargadas"

# Verificar conexión a la base de datos
echo -e "${YELLOW}🔌 Verificando servicios externos...${NC}"
echo "  - Base de datos: MySQL en localhost:3306"
echo "  - IdentityService: $IDENTITY_SERVICE_URL"
echo "  - RabbitMQ: $RABBITMQ_HOST:$RABBITMQ_PORT"

echo ""
echo -e "${GREEN}✓${NC} Configuración completa"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎯 UploadService iniciado en http://${HOST}:${PORT}${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Endpoints disponibles:"
echo "  • Health Check:  http://localhost:${PORT}/health"
echo "  • API Docs:      http://localhost:${PORT}/docs"
echo "  • Upload:        http://localhost:${PORT}/api/v1/transactions/upload"
echo ""
echo "Para detener el servicio, presiona Ctrl+C"
echo ""

# Iniciar el servidor
uvicorn src.main:app --host $HOST --port $PORT --reload
