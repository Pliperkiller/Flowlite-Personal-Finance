#!/bin/bash

# ================================================================
# SCRIPT SIMPLE: Eliminar tabla UserInfo
# ================================================================
# Hibernate la recreará automáticamente con los nombres correctos
# ================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}    🗑️  ELIMINAR TABLA UserInfo (Hibernate la recreará)    ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Función para detectar contenedor MySQL
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
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}✗${NC} Docker no está disponible"
    echo ""
    echo -e "${YELLOW}💡 Ejecuta manualmente:${NC}"
    echo "   mysql -u root -p flowlite_db -e 'DROP TABLE IF EXISTS UserInfo;'"
    exit 1
fi

# Detectar contenedor
MYSQL_CONTAINER=$(find_mysql_container)
if [ -z "$MYSQL_CONTAINER" ]; then
    echo -e "${RED}✗${NC} No se encontró contenedor MySQL"
    echo ""
    echo -e "${YELLOW}💡 Inicia MySQL primero:${NC}"
    echo "   cd ../InfrastructureService && docker-compose up -d mysql"
    exit 1
fi

# Detectar password
DB_PASSWORD=$(detect_password "$MYSQL_CONTAINER")
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}✗${NC} No se detectaron credenciales"
    exit 1
fi

echo -e "${GREEN}✓${NC} Contenedor MySQL: ${CYAN}$MYSQL_CONTAINER${NC}"
echo ""

# Eliminar tabla
echo -e "${YELLOW}⚠️  Eliminando tabla UserInfo...${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DROP TABLE IF EXISTS UserInfo;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Tabla UserInfo eliminada"
else
    echo -e "${RED}✗${NC} Error al eliminar tabla"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ TABLA ELIMINADA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}🚀 Próximos pasos:${NC}"
echo ""
echo -e "  1. Reinicia IdentityService:"
echo -e "     ${CYAN}cd ../identifyservice${NC}"
echo -e "     ${CYAN}./kill.sh && ./start.sh${NC}"
echo ""
echo -e "  2. Hibernate recreará automáticamente la tabla con:"
echo -e "     • Nombres de columnas en inglés ✅"
echo -e "     • UUIDs como BINARY(16) ✅"
echo -e "     • Estructura correcta ✅"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
