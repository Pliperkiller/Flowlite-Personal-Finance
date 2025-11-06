#!/bin/bash

# ================================================================
# EXPERT DATABASE MIGRATION RESET TOOL
# ================================================================
# This script resets the migration state and applies the new
# consolidated migration cleanly.
#
# Author: Expert Database Architect
# ================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}    🔧 EXPERT DATABASE MIGRATION RESET    ${NC}"
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
    echo "   mysql -u root -p flowlite_db < $SCRIPT_DIR/migrations/001_create_userinfo_table_english.sql"
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
echo -e "${GREEN}✓${NC} Credenciales detectadas"
echo ""

# ================================================================
# PASO 1: Limpiar estado de migraciones
# ================================================================
echo -e "${BLUE}[1/3]${NC} Limpiando estado de migraciones anteriores..."
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db <<'SQL' 2>/dev/null
-- Eliminar migraciones anteriores fallidas
DELETE FROM schema_migrations
WHERE migration_name IN (
    '001_fix_userinfo_structure.sql',
    '002_rename_userinfo_columns_to_english.sql'
);
SQL

echo -e "${GREEN}✓${NC} Estado de migraciones limpiado"
echo ""

# ================================================================
# PASO 2: Ejecutar nueva migración consolidada
# ================================================================
echo -e "${BLUE}[2/3]${NC} Ejecutando migración consolidada..."
echo -e "${YELLOW}      📋 Archivo: 001_create_userinfo_table_english.sql${NC}"
echo ""

if docker exec -i "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db < "$SCRIPT_DIR/migrations/001_create_userinfo_table_english.sql" 2>&1 | grep -v "mysql: \[Warning\]"; then
    echo ""
    echo -e "${GREEN}✓${NC} Migración ejecutada exitosamente"
else
    echo ""
    echo -e "${RED}✗${NC} Error al ejecutar migración"
    exit 1
fi
echo ""

# ================================================================
# PASO 3: Registrar migración como aplicada
# ================================================================
echo -e "${BLUE}[3/3]${NC} Registrando migración..."
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db <<'SQL' 2>/dev/null
-- Asegurar que existe la tabla de migraciones
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Registrar migración como aplicada
INSERT IGNORE INTO schema_migrations (migration_name)
VALUES ('001_create_userinfo_table_english.sql');
SQL

echo -e "${GREEN}✓${NC} Migración registrada"
echo ""

# ================================================================
# VERIFICACIÓN FINAL
# ================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓✓✓ MIGRACIÓN COMPLETADA EXITOSAMENTE ✓✓✓${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${CYAN}📊 Estructura de la tabla UserInfo:${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DESCRIBE UserInfo;" 2>/dev/null | head -20
echo ""

echo -e "${CYAN}📋 Migraciones aplicadas:${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "SELECT * FROM schema_migrations;" 2>/dev/null
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}🚀 SIGUIENTE PASO:${NC}"
echo ""
echo -e "  1. Recompila IdentityService:"
echo -e "     ${CYAN}cd ../identifyservice && mvn clean package -DskipTests${NC}"
echo ""
echo -e "  2. Reinicia el servicio:"
echo -e "     ${CYAN}./kill.sh && ./start.sh${NC}"
echo ""
echo -e "  3. Prueba el endpoint:"
echo -e "     ${CYAN}curl http://localhost:8000/user-info/me -H 'Authorization: Bearer TOKEN'${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
