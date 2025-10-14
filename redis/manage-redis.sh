#!/bin/bash

# ===========================================
# SCRIPT DE GESTIÓN PARA REDIS
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
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}  GESTIÓN DE REDIS PARA FLOWLITE${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  start     - Iniciar Redis"
    echo "  stop      - Detener Redis"
    echo "  restart   - Reiniciar Redis"
    echo "  status    - Ver estado de Redis"
    echo "  logs      - Ver logs de Redis"
    echo "  connect   - Conectar a Redis CLI"
    echo "  clean     - Limpiar datos de Redis"
    echo "  help      - Mostrar esta ayuda"
    echo ""
}

# Función para iniciar Redis
start_redis() {
    echo -e "${GREEN}🚀 Iniciando Redis...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Redis iniciado correctamente${NC}"
    echo -e "${BLUE}📍 Puerto: 6379${NC}"
    echo -e "${BLUE}📍 Host: localhost${NC}"
}

# Función para detener Redis
stop_redis() {
    echo -e "${YELLOW}🛑 Deteniendo Redis...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Redis detenido correctamente${NC}"
}

# Función para reiniciar Redis
restart_redis() {
    echo -e "${YELLOW}🔄 Reiniciando Redis...${NC}"
    docker-compose down
    docker-compose up -d
    echo -e "${GREEN}✅ Redis reiniciado correctamente${NC}"
}

# Función para ver estado
show_status() {
    echo -e "${BLUE}📊 Estado de Redis:${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}📊 Información del contenedor:${NC}"
    docker inspect flowlite-redis --format='{{.State.Status}}' 2>/dev/null || echo "Contenedor no encontrado"
}

# Función para ver logs
show_logs() {
    echo -e "${BLUE}📋 Logs de Redis:${NC}"
    docker-compose logs -f
}

# Función para conectar a Redis CLI
connect_redis() {
    echo -e "${BLUE}🔗 Conectando a Redis CLI...${NC}"
    docker exec -it flowlite-redis redis-cli
}

# Función para limpiar datos
clean_redis() {
    echo -e "${RED}⚠️  ¿Estás seguro de que quieres limpiar todos los datos de Redis? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🧹 Limpiando datos de Redis...${NC}"
        docker-compose down -v
        docker volume rm redis_redis_data 2>/dev/null || true
        echo -e "${GREEN}✅ Datos de Redis limpiados${NC}"
    else
        echo -e "${BLUE}❌ Operación cancelada${NC}"
    fi
}

# Procesar comando
case "${1:-help}" in
    start)
        start_redis
        ;;
    stop)
        stop_redis
        ;;
    restart)
        restart_redis
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    connect)
        connect_redis
        ;;
    clean)
        clean_redis
        ;;
    help|*)
        show_help
        ;;
esac
