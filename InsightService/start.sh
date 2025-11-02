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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para encontrar Python 3.11+ de forma multiplataforma
find_python() {
    local python_cmd=""

    # 1. Verificar variable de entorno PYTHON_CMD (override manual)
    if [ ! -z "$PYTHON_CMD" ]; then
        if command -v "$PYTHON_CMD" &> /dev/null; then
            python_cmd="$PYTHON_CMD"
            echo -e "${GREEN}✓${NC} Usando Python desde variable PYTHON_CMD: $python_cmd" >&2
            echo "$python_cmd"
            return 0
        fi
    fi

    # 2. Buscar en ubicaciones comunes según el sistema operativo
    local candidates=(
        # Homebrew (macOS)
        "/opt/homebrew/opt/python@3.11/bin/python3.11"
        "/usr/local/opt/python@3.11/bin/python3.11"
        # pyenv
        "$HOME/.pyenv/versions/3.11.*/bin/python"
        # Sistema (Linux/macOS)
        "$(command -v python3.11 2>/dev/null)"
        "$(command -v python3.12 2>/dev/null)"
        "$(command -v python3.13 2>/dev/null)"
        "$(command -v python3 2>/dev/null)"
        # Windows (Git Bash, WSL)
        "/c/Python311/python.exe"
        "/mnt/c/Python311/python.exe"
        "$(command -v python 2>/dev/null)"
    )

    # 3. Probar cada candidato
    for candidate in "${candidates[@]}"; do
        if [ ! -z "$candidate" ] && [ -f "$candidate" ] || command -v "$candidate" &> /dev/null; then
            # Verificar que sea Python 3.11+
            local version=$($candidate --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)

            if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
                python_cmd="$candidate"
                echo -e "${GREEN}✓${NC} Python $version encontrado: $python_cmd" >&2
                echo "$python_cmd"
                return 0
            fi
        fi
    done

    # 4. No se encontró Python 3.11+
    echo -e "${RED}❌ Error: No se encontró Python 3.11 o superior${NC}" >&2
    echo "" >&2
    echo "Por favor, instala Python 3.11+ o establece la variable PYTHON_CMD:" >&2
    echo "  export PYTHON_CMD=/ruta/a/python3.11" >&2
    echo "" >&2
    echo "Instalación según tu sistema:" >&2
    echo "  • macOS:   brew install python@3.11" >&2
    echo "  • Ubuntu:  sudo apt install python3.11" >&2
    echo "  • Windows: https://www.python.org/downloads/" >&2
    return 1
}

# Detectar Python
PYTHON_BIN=$(find_python)
if [ $? -ne 0 ]; then
    exit 1
fi

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
    $PYTHON_BIN -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al crear el entorno virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
fi

# Activar entorno virtual (compatible con Linux/macOS y Windows)
echo -e "${YELLOW}📦 Activando entorno virtual...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo -e "${RED}❌ Error: No se encontró el script de activación del venv${NC}"
    exit 1
fi

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

# Establecer valores por defecto si no están definidos
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-8002}

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
