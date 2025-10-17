#!/bin/bash

# ===========================================
# SCRIPT DE GESTIÓN GLOBAL - FLOWLITE
# ===========================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== GESTIÓN GLOBAL FLOWLITE ===${NC}"
    echo ""
    echo "Uso: $0 [COMANDO] [SERVICIO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start-db     - Iniciar base de datos compartida"
    echo "  stop-db      - Detener base de datos compartida"
    echo "  restart-db   - Reiniciar base de datos compartida"
    echo "  start        - Iniciar servicio específico (requiere nombre del servicio)"
    echo "  stop         - Detener servicio específico (requiere nombre del servicio)"
    echo "  restart      - Reiniciar servicio específico (requiere nombre del servicio)"
    echo "  start-all    - Iniciar base de datos y todos los servicios"
    echo "  stop-all     - Detener todo"
    echo "  status       - Ver estado de todos los servicios"
    echo "  logs-db      - Ver logs de la base de datos"
    echo "  logs         - Ver logs de un servicio específico (requiere nombre del servicio)"
    echo "  clean        - Limpiar volúmenes y contenedores"
    echo "  help         - Mostrar esta ayuda"
    echo ""
    echo "Servicios disponibles:"
    echo "  identifyservice"
    echo ""
    echo "Ejemplos:"
    echo "  $0 start-db"
    echo "  $0 start identifyservice"
    echo "  $0 logs identifyservice"
    echo "  $0 status"
    echo ""
}

# Función para iniciar base de datos
start_database() {
    echo -e "${YELLOW}Iniciando base de datos compartida...${NC}"
    cd database
    ./manage-database.sh start-db
    cd ..
    echo -e "${GREEN}Base de datos iniciada correctamente${NC}"
}

# Función para detener base de datos
stop_database() {
    echo -e "${YELLOW}Deteniendo base de datos compartida...${NC}"
    cd database
    ./manage-database.sh stop-db
    cd ..
    echo -e "${GREEN}Base de datos detenida${NC}"
}

# Función para iniciar servicio
start_service() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Debes especificar el nombre del servicio${NC}"
        echo -e "${BLUE}Servicios disponibles: identifyservice${NC}"
        exit 1
    fi
    
    if [ ! -d "$service" ]; then
        echo -e "${RED}Error: El servicio '$service' no existe${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Iniciando servicio: $service${NC}"
    cd "$service"
    docker-compose up -d
    cd ..
    echo -e "${GREEN}Servicio $service iniciado correctamente${NC}"
}

# Función para detener servicio
stop_service() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Debes especificar el nombre del servicio${NC}"
        exit 1
    fi
    
    if [ ! -d "$service" ]; then
        echo -e "${RED}Error: El servicio '$service' no existe${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Deteniendo servicio: $service${NC}"
    cd "$service"
    docker-compose down
    cd ..
    echo -e "${GREEN}Servicio $service detenido${NC}"
}

# Función para ver estado
show_status() {
    echo -e "${BLUE}=== ESTADO DE BASE DE DATOS ===${NC}"
    cd database
    ./manage-database.sh status
    cd ..
    echo ""
    
    echo -e "${BLUE}=== ESTADO DE SERVICIOS ===${NC}"
    for service in identifyservice; do
        if [ -d "$service" ]; then
            echo -e "${YELLOW}--- $service ---${NC}"
            cd "$service"
            docker-compose ps 2>/dev/null || echo "No hay contenedores ejecutándose"
            cd ..
        fi
    done
}

# Función para ver logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo -e "${RED}Error: Debes especificar el nombre del servicio${NC}"
        exit 1
    fi
    
    if [ ! -d "$service" ]; then
        echo -e "${RED}Error: El servicio '$service' no existe${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Mostrando logs del servicio: $service${NC}"
    cd "$service"
    docker-compose logs -f
}

# Función para limpiar
clean_all() {
    echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los datos${NC}"
    read -p "¿Estás seguro? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Limpiando contenedores y volúmenes...${NC}"
        
        # Detener y limpiar servicios
        for service in identifyservice; do
            if [ -d "$service" ]; then
                cd "$service"
                docker-compose down -v 2>/dev/null || true
                cd ..
            fi
        done
        
        # Detener y limpiar base de datos
        cd database
        ./manage-database.sh clean
        cd ..
        
        docker system prune -f
        echo -e "${GREEN}Limpieza completada${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para iniciar todo
start_all() {
    start_database
    sleep 10
    start_service "identifyservice"
}

# Función para detener todo
stop_all() {
    stop_service "identifyservice"
    stop_database
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
    start)
        start_service "$2"
        ;;
    stop)
        stop_service "$2"
        ;;
    restart)
        stop_service "$2"
        start_service "$2"
        ;;
    start-all)
        start_all
        ;;
    stop-all)
        stop_all
        ;;
    status)
        show_status
        ;;
    logs-db)
        cd database
        ./manage-database.sh logs-db
        ;;
    logs)
        show_logs "$2"
        ;;
    clean)
        clean_all
        ;;
    help|*)
        show_help
        ;;
esac
