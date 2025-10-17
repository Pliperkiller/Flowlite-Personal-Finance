#!/bin/bash

# ===========================================
# SCRIPT DE GESTIÓN DE BASE DE DATOS COMPARTIDA (CROSS-PLATFORM)
# ===========================================

set -e

# Detectar sistema operativo
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== GESTIÓN DE BASE DE DATOS COMPARTIDA ===${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start-db     - Iniciar base de datos compartida"
    echo "  stop-db      - Detener base de datos compartida"
    echo "  restart-db   - Reiniciar base de datos compartida"
    echo "  start-app    - Iniciar aplicación (requiere DB activa)"
    echo "  stop-app     - Detener aplicación"
    echo "  restart-app  - Reiniciar aplicación"
    echo "  start-all    - Iniciar base de datos y aplicación"
    echo "  stop-all     - Detener todo"
    echo "  status       - Ver estado de todos los servicios"
    echo "  logs-db      - Ver logs de la base de datos"
    echo "  logs-app     - Ver logs de la aplicación"
    echo "  clean        - Limpiar volúmenes y contenedores"
    echo "  help         - Mostrar esta ayuda"
    echo ""
}

# Función para iniciar base de datos
start_database() {
    echo -e "${YELLOW}Iniciando base de datos compartida...${NC}"
    if docker-compose -f docker-compose.database.yml up -d; then
        echo -e "${GREEN}Base de datos iniciada correctamente${NC}"
        echo -e "${BLUE}phpMyAdmin disponible en: http://localhost:8081${NC}"
    else
        echo -e "${RED}❌ Error al iniciar la base de datos${NC}"
        exit 1
    fi
}

# Función para detener base de datos
stop_database() {
    echo -e "${YELLOW}Deteniendo base de datos compartida...${NC}"
    if docker-compose -f docker-compose.database.yml down; then
        echo -e "${GREEN}Base de datos detenida${NC}"
    else
        echo -e "${RED}❌ Error al detener la base de datos${NC}"
        exit 1
    fi
}

# Función para iniciar aplicación
start_application() {
    echo -e "${YELLOW}Iniciando aplicación...${NC}"
    echo -e "${BLUE}Nota: Ejecuta este comando desde la carpeta del servicio${NC}"
    echo -e "${BLUE}Ejemplo: cd ../identifyservice && docker-compose up -d${NC}"
}

# Función para detener aplicación
stop_application() {
    echo -e "${YELLOW}Deteniendo aplicación...${NC}"
    echo -e "${BLUE}Nota: Ejecuta este comando desde la carpeta del servicio${NC}"
    echo -e "${BLUE}Ejemplo: cd ../identifyservice && docker-compose down${NC}"
}

# Función para ver estado
show_status() {
    echo -e "${BLUE}=== ESTADO DE BASE DE DATOS ===${NC}"
    docker-compose -f docker-compose.database.yml ps
    echo ""
    echo -e "${BLUE}=== ESTADO DE APLICACIONES ===${NC}"
    echo -e "${YELLOW}Para ver el estado de las aplicaciones, ejecuta desde cada carpeta de servicio:${NC}"
    echo -e "${BLUE}cd ../identifyservice && docker-compose ps${NC}"
}

# Función para limpiar
clean_all() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los datos de la base de datos${NC}"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Limpiando contenedores y volúmenes...${NC}"
        docker-compose down -v
        docker-compose -f docker-compose.database.yml down -v
        docker system prune -f
        echo -e "${GREEN}Limpieza completada${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Procesar comando
case "${1:-help}" in
    start-db)
        start_database
        ;;
    stop-db)
        stop_database
        ;;
    restart-db)
        stop_database
        start_database
        ;;
    start-app)
        start_application
        ;;
    stop-app)
        stop_application
        ;;
    restart-app)
        stop_application
        start_application
        ;;
    start-all)
        start_database
        sleep 10
        start_application
        ;;
    stop-all)
        stop_application
        stop_database
        ;;
    status)
        show_status
        ;;
    logs-db)
        docker-compose -f docker-compose.database.yml logs -f
        ;;
    logs-app)
        echo -e "${BLUE}Para ver logs de aplicaciones, ejecuta desde cada carpeta de servicio:${NC}"
        echo -e "${BLUE}cd ../identifyservice && docker-compose logs -f${NC}"
        ;;
    clean)
        clean_all
        ;;
    help|*)
        show_help
        ;;
esac
