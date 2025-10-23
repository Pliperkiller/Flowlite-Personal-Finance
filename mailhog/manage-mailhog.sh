#!/bin/bash

# ===========================================
# SCRIPT DE GESTIÓN DE MAILHOG
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
    echo -e "${BLUE}=== GESTIÓN DE MAILHOG ===${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar MailHog"
    echo "  stop      - Detener MailHog"
    echo "  restart   - Reiniciar MailHog"
    echo "  status    - Ver estado de MailHog"
    echo "  logs      - Ver logs de MailHog"
    echo "  clean     - Limpiar datos de MailHog"
    echo "  web       - Abrir interfaz web de MailHog"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 start"
    echo "  $0 logs"
    echo "  $0 web"
}

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker no está corriendo${NC}"
        exit 1
    fi
}

# Función para iniciar MailHog
start_mailhog() {
    echo -e "${BLUE}Iniciando MailHog...${NC}"
    check_docker
    
    # Crear red si no existe
    docker network create flowlite-network 2>/dev/null || true
    
    docker-compose up -d
    
    echo -e "${GREEN}MailHog iniciado correctamente${NC}"
    echo -e "${YELLOW}SMTP Server: localhost:1025${NC}"
    echo -e "${YELLOW}Web UI: http://localhost:8025${NC}"
}

# Función para detener MailHog
stop_mailhog() {
    echo -e "${BLUE}Deteniendo MailHog...${NC}"
    docker-compose down
    echo -e "${GREEN}MailHog detenido${NC}"
}

# Función para reiniciar MailHog
restart_mailhog() {
    echo -e "${BLUE}Reiniciando MailHog...${NC}"
    stop_mailhog
    start_mailhog
}

# Función para ver estado
status_mailhog() {
    echo -e "${BLUE}Estado de MailHog:${NC}"
    docker-compose ps
}

# Función para ver logs
logs_mailhog() {
    echo -e "${BLUE}Logs de MailHog:${NC}"
    docker-compose logs -f
}

# Función para limpiar datos
clean_mailhog() {
    echo -e "${YELLOW}¿Estás seguro de que quieres limpiar todos los datos de MailHog? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Limpiando datos de MailHog...${NC}"
        docker-compose down -v
        docker volume rm mailhog_mailhog_data 2>/dev/null || true
        echo -e "${GREEN}Datos limpiados${NC}"
    else
        echo -e "${YELLOW}Operación cancelada${NC}"
    fi
}

# Función para abrir interfaz web
web_mailhog() {
    echo -e "${BLUE}Abriendo interfaz web de MailHog...${NC}"
    
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open http://localhost:8025
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open http://localhost:8025
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start http://localhost:8025
    else
        echo -e "${YELLOW}Por favor, abre manualmente: http://localhost:8025${NC}"
    fi
}

# Función para verificar configuración
check_config() {
    echo -e "${BLUE}Verificando configuración...${NC}"
    
    # Verificar si el puerto 1025 está disponible
    if lsof -Pi :1025 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Puerto 1025 disponible${NC}"
    else
        echo -e "${YELLOW}⚠ Puerto 1025 en uso${NC}"
    fi
    
    # Verificar si el puerto 8025 está disponible
    if lsof -Pi :8025 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Puerto 8025 disponible${NC}"
    else
        echo -e "${YELLOW}⚠ Puerto 8025 en uso${NC}"
    fi
}

# Procesar comando
case "${1:-help}" in
    start)
        start_mailhog
        ;;
    stop)
        stop_mailhog
        ;;
    restart)
        restart_mailhog
        ;;
    status)
        status_mailhog
        ;;
    logs)
        logs_mailhog
        ;;
    clean)
        clean_mailhog
        ;;
    web)
        web_mailhog
        ;;
    check)
        check_config
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Comando no reconocido: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
