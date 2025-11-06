#!/bin/bash

# Script para inspeccionar el estado actual de UserInfo

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      🔍 INSPECCIONANDO TABLA UserInfo      ${NC}"
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

# Detectar contenedor
MYSQL_CONTAINER=$(find_mysql_container)
if [ -z "$MYSQL_CONTAINER" ]; then
    echo -e "${RED}✗${NC} No se encontró contenedor MySQL"
    exit 1
fi

# Detectar password
DB_PASSWORD=$(detect_password "$MYSQL_CONTAINER")
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}✗${NC} No se detectaron credenciales"
    exit 1
fi

echo -e "${GREEN}✓${NC} Contenedor: ${CYAN}$MYSQL_CONTAINER${NC}"
echo ""

# Verificar si la tabla existe
echo -e "${YELLOW}1. Verificando existencia de tabla UserInfo...${NC}"
TABLE_EXISTS=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -se "SHOW TABLES LIKE 'UserInfo';" 2>/dev/null)

if [ -z "$TABLE_EXISTS" ]; then
    echo -e "${RED}✗${NC} La tabla UserInfo NO existe"
    exit 0
else
    echo -e "${GREEN}✓${NC} La tabla UserInfo existe"
fi
echo ""

# Mostrar estructura de la tabla
echo -e "${YELLOW}2. Estructura actual de la tabla:${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DESCRIBE UserInfo;" 2>/dev/null
echo ""

# Contar registros
echo -e "${YELLOW}3. Cantidad de registros:${NC}"
COUNT=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -se "SELECT COUNT(*) FROM UserInfo;" 2>/dev/null)
echo -e "   Total registros: ${CYAN}$COUNT${NC}"
echo ""

# Mostrar tipos de datos de las columnas clave
echo -e "${YELLOW}4. Verificando tipos de datos de columnas UUID:${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'flowlite_db'
  AND TABLE_NAME = 'UserInfo'
  AND COLUMN_NAME IN ('id', 'id_user', 'user_id')
ORDER BY ORDINAL_POSITION;" 2>/dev/null
echo ""

# Mostrar ejemplo de datos (primeros 2 registros)
if [ "$COUNT" -gt 0 ]; then
    echo -e "${YELLOW}5. Muestra de datos (primeros 2 registros):${NC}"
    docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "
    SELECT
        id,
        id_user,
        primerNombre,
        primerApellido,
        createdAt
    FROM UserInfo
    LIMIT 2;" 2>/dev/null || echo -e "${YELLOW}   (No se pudieron leer los datos)${NC}"
    echo ""
fi

# Verificar migraciones aplicadas
echo -e "${YELLOW}6. Migraciones aplicadas:${NC}"
MIGRATIONS_TABLE=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -se "SHOW TABLES LIKE 'schema_migrations';" 2>/dev/null)

if [ -n "$MIGRATIONS_TABLE" ]; then
    docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "SELECT * FROM schema_migrations;" 2>/dev/null
else
    echo -e "${YELLOW}   Tabla schema_migrations no existe${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ INSPECCIÓN COMPLETADA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
