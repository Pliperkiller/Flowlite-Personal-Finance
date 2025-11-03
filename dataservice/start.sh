#!/bin/bash

# Script para iniciar el DataService
# ====================================

echo "🚀 Iniciando DataService..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Cargar variables de entorno
echo -e "${YELLOW}🔧 Cargando variables de entorno...${NC}"
export $(cat .env | grep -v '^#' | xargs)

# Establecer valores por defecto si no están definidos
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8003}

echo -e "${GREEN}✓${NC} Variables de entorno cargadas"

# Verificar conexión a servicios externos
echo -e "${YELLOW}🔌 Verificando servicios externos...${NC}"
echo "  - Base de datos: MySQL en localhost:3306"
echo "  - IdentityService: $IDENTITY_SERVICE_URL"

echo ""
echo -e "${GREEN}✓${NC} Configuración completa"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎯 DataService iniciado en http://${HOST}:${PORT}${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Endpoints disponibles:"
echo "  • Health Check:        http://localhost:${PORT}/health"
echo "  • API Docs:            http://localhost:${PORT}/docs"
echo "  • Transactions:        http://localhost:${PORT}/transactions"
echo "  • Insights:            http://localhost:${PORT}/insights"
echo "  • Banks:               http://localhost:${PORT}/banks"
echo "  • Transaction Categories: http://localhost:${PORT}/transaction-categories"
echo "  • Insight Categories:  http://localhost:${PORT}/insight-categories"
echo ""
echo "Para detener el servicio, presiona Ctrl+C"
echo ""

# Iniciar el servidor
uvicorn src.main:app --host $HOST --port $PORT --reload
