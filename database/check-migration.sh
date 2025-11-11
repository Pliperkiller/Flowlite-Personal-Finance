#!/bin/bash

# ============================================
# Script para verificar estado de la migración
# Compatible con Windows/Git Bash
# ============================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      🔍 VERIFICANDO ESTADO DE MIGRACIONES      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Función para verificar Docker
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Docker no está disponible"
        echo -e "${YELLOW}💡 Asegúrate de que Docker Desktop esté corriendo${NC}"
        return 1
    fi
    echo -e "${GREEN}✓${NC} Docker está disponible"
    return 0
}

# Función para encontrar contenedor MySQL
find_mysql_container() {
    local containers=("flowlite-mysql" "flowlite-shared-mysql" "mysql")

    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
            echo "$container"
            return 0
        fi
    done

    return 1
}

# Función para detectar password
detect_password() {
    local container=$1
    local passwords=("rootpassword" "Flowlite10+" "flowlite123" "")

    for password in "${passwords[@]}"; do
        if docker exec "$container" mysql -uroot -p"$password" -e "SELECT 1" >/dev/null 2>&1; then
            echo "$password"
            return 0
        fi
    done

    return 1
}

# Verificar Docker
echo -e "${BLUE}[1/4]${NC} Verificando Docker..."
if ! check_docker; then
    exit 1
fi
echo ""

# Verificar contenedores MySQL
echo -e "${BLUE}[2/4]${NC} Buscando contenedor MySQL..."
MYSQL_CONTAINER=$(find_mysql_container)

if [ -z "$MYSQL_CONTAINER" ]; then
    echo -e "${RED}✗${NC} No se encontró ningún contenedor MySQL corriendo"
    echo ""
    echo -e "${YELLOW}Contenedores disponibles:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    echo ""
    echo -e "${YELLOW}💡 Sugerencias:${NC}"
    echo -e "   1. Inicia MySQL con: cd infrastructureservice && docker-compose up -d mysql"
    echo -e "   2. O ejecuta: ./build_app.sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} Contenedor MySQL encontrado: ${CYAN}$MYSQL_CONTAINER${NC}"
echo ""

# Detectar password
echo -e "${BLUE}[3/4]${NC} Detectando credenciales..."
DB_PASSWORD=$(detect_password "$MYSQL_CONTAINER")

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}✗${NC} No se pudieron detectar las credenciales"
    exit 1
fi

echo -e "${GREEN}✓${NC} Credenciales detectadas"
echo ""

# Verificar estructura de UserInfo
echo -e "${BLUE}[4/4]${NC} Verificando estructura de la tabla UserInfo..."
echo ""

STRUCTURE=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DESCRIBE UserInfo;" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} No se pudo obtener la estructura de UserInfo"
    echo -e "${YELLOW}💡 La tabla podría no existir o la base de datos flowlite_db no existe${NC}"
    exit 1
fi

echo -e "${CYAN}Estructura actual de UserInfo:${NC}"
echo "$STRUCTURE"
echo ""

# Verificar si existe la columna 'id'
if echo "$STRUCTURE" | grep -q "^id"; then
    echo -e "${GREEN}✓${NC} Migración APLICADA: La tabla tiene la columna 'id'"
    MIGRATION_STATUS="applied"
else
    echo -e "${RED}✗${NC} Migración NO APLICADA: Falta la columna 'id'"
    MIGRATION_STATUS="pending"
fi
echo ""

# Verificar tabla schema_migrations
echo -e "${CYAN}Migraciones registradas:${NC}"
MIGRATIONS=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "SELECT * FROM schema_migrations;" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "$MIGRATIONS"
else
    echo -e "${YELLOW}⚠️  Tabla schema_migrations no existe${NC}"
fi
echo ""

# Resumen final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      📊 RESUMEN      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  Contenedor MySQL: ${CYAN}$MYSQL_CONTAINER${NC}"
echo -e "  Base de datos: ${CYAN}flowlite_db${NC}"

if [ "$MIGRATION_STATUS" = "applied" ]; then
    echo -e "  Estado migración: ${GREEN}✓ APLICADA${NC}"
    echo ""
    echo -e "${GREEN}Todo está correcto. El endpoint /user-info/update debería funcionar.${NC}"
else
    echo -e "  Estado migración: ${RED}✗ PENDIENTE${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  La migración NO se ha aplicado.${NC}"
    echo -e "${YELLOW}Ejecuta: ${CYAN}./database/apply-migration-manually.sh${NC}"
fi

echo ""
