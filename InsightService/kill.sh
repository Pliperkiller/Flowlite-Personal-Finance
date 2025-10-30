#!/bin/bash

# Script para detener InsightService
# ===================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${YELLOW}🛑 Deteniendo InsightService...${NC}"
echo ""

PORT=8002

# Verificar si hay un proceso corriendo en el puerto
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Matando proceso en puerto $PORT...${NC}"

    # Obtener el PID
    PID=$(lsof -ti:$PORT)

    # Matar el proceso
    kill -9 $PID 2>/dev/null

    # Esperar un momento
    sleep 2

    # Verificar que se detuvo
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}✗ Error: No se pudo detener el servicio${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ InsightService detenido correctamente (PID: $PID)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No hay ningún proceso corriendo en el puerto $PORT${NC}"
fi

echo ""