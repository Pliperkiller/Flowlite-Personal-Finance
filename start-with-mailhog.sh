#!/bin/bash

# ===========================================
# SCRIPT DE INICIO CON MAILHOG
# ===========================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== INICIANDO FLOWLITE CON MAILHOG ===${NC}"
echo ""

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Error: Docker no está corriendo${NC}"
        echo "Por favor, inicia Docker Desktop y vuelve a ejecutar este script"
        exit 1
    fi
}

# Función para verificar si los puertos están disponibles
check_ports() {
    echo -e "${BLUE}Verificando puertos...${NC}"
    
    if lsof -Pi :1025 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Puerto 1025 en uso${NC}"
    else
        echo -e "${GREEN}✓ Puerto 1025 disponible${NC}"
    fi
    
    if lsof -Pi :8025 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Puerto 8025 en uso${NC}"
    else
        echo -e "${GREEN}✓ Puerto 8025 disponible${NC}"
    fi
    
    if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Puerto 8080 en uso${NC}"
    else
        echo -e "${GREEN}✓ Puerto 8080 disponible${NC}"
    fi
}

# Función para iniciar MailHog
start_mailhog() {
    echo -e "${BLUE}Iniciando MailHog...${NC}"
    cd mailhog
    ./manage-mailhog.sh start
    cd ..
    echo -e "${GREEN}MailHog iniciado${NC}"
}

# Función para iniciar identifyservice
start_identifyservice() {
    echo -e "${BLUE}Iniciando identifyservice con MailHog...${NC}"
    cd identifyservice
    
    # Configurar variables de entorno para MailHog
    export MAIL_HOST=localhost
    export MAIL_PORT=1025
    export MAIL_USERNAME=
    export MAIL_PASSWORD=
    export APP_EMAIL_FROM=noreply@flowlite.local
    
    # Iniciar con perfil mailhog
    ./gradlew bootRun --args='--spring.profiles.active=mailhog' &
    
    cd ..
    echo -e "${GREEN}identifyservice iniciado${NC}"
}

# Función para mostrar información
show_info() {
    echo ""
    echo -e "${GREEN}=== SERVICIOS INICIADOS ===${NC}"
    echo -e "${YELLOW}MailHog Web UI:${NC} http://localhost:8025"
    echo -e "${YELLOW}identifyservice API:${NC} http://localhost:8080"
    echo -e "${YELLOW}Swagger UI:${NC} http://localhost:8080/swagger-ui.html"
    echo ""
    echo -e "${BLUE}=== COMANDOS ÚTILES ===${NC}"
    echo "Ver logs de MailHog: cd mailhog && ./manage-mailhog.sh logs"
    echo "Ver logs de identifyservice: cd identifyservice && ./gradlew bootRun --args='--spring.profiles.active=mailhog'"
    echo "Detener MailHog: cd mailhog && ./manage-mailhog.sh stop"
    echo ""
    echo -e "${YELLOW}=== TESTING ===${NC}"
    echo "1. Registra un usuario en: http://localhost:8080/auth/preregister"
    echo "2. Ve el email en: http://localhost:8025"
    echo "3. Verifica la cuenta con el token del email"
}

# Función para limpiar al salir
cleanup() {
    echo ""
    echo -e "${YELLOW}Deteniendo servicios...${NC}"
    cd mailhog
    ./manage-mailhog.sh stop
    cd ..
    echo -e "${GREEN}Servicios detenidos${NC}"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

# Ejecutar pasos
echo -e "${BLUE}Paso 1: Verificando Docker...${NC}"
check_docker

echo -e "${BLUE}Paso 2: Verificando puertos...${NC}"
check_ports

echo -e "${BLUE}Paso 3: Iniciando MailHog...${NC}"
start_mailhog

echo -e "${BLUE}Paso 4: Iniciando identifyservice...${NC}"
start_identifyservice

# Esperar un momento para que los servicios se inicien
sleep 5

echo -e "${BLUE}Paso 5: Verificando servicios...${NC}"
# Verificar MailHog
if curl -s http://localhost:8025 > /dev/null; then
    echo -e "${GREEN}✓ MailHog funcionando${NC}"
else
    echo -e "${RED}✗ MailHog no responde${NC}"
fi

# Verificar identifyservice
if curl -s http://localhost:8080/actuator/health > /dev/null; then
    echo -e "${GREEN}✓ identifyservice funcionando${NC}"
else
    echo -e "${YELLOW}⚠ identifyservice aún iniciando...${NC}"
fi

show_info

# Mantener el script corriendo
echo -e "${BLUE}Presiona Ctrl+C para detener todos los servicios${NC}"
while true; do
    sleep 1
done
