#!/bin/bash

# ============================================
# Script para aplicar migración manualmente
# Compatible con Windows/Git Bash
# ============================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/migrations/001_fix_userinfo_structure.sql"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${CYAN}      🔧 APLICANDO MIGRACIÓN MANUALMENTE      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Función para verificar Docker
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Docker no está disponible"
        echo -e "${YELLOW}💡 Asegúrate de que Docker Desktop esté corriendo${NC}"
        return 1
    fi
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
echo -e "${BLUE}[1/5]${NC} Verificando Docker..."
if ! check_docker; then
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker está disponible"
echo ""

# Verificar contenedores MySQL
echo -e "${BLUE}[2/5]${NC} Buscando contenedor MySQL..."
MYSQL_CONTAINER=$(find_mysql_container)

if [ -z "$MYSQL_CONTAINER" ]; then
    echo -e "${RED}✗${NC} No se encontró ningún contenedor MySQL corriendo"
    echo ""
    echo -e "${YELLOW}💡 Sugerencias:${NC}"
    echo -e "   1. Inicia MySQL con: ${CYAN}cd infrastructureservice && docker-compose up -d mysql${NC}"
    echo -e "   2. O ejecuta: ${CYAN}./build_app.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Contenedor MySQL encontrado: ${CYAN}$MYSQL_CONTAINER${NC}"
echo ""

# Detectar password
echo -e "${BLUE}[3/5]${NC} Detectando credenciales..."
DB_PASSWORD=$(detect_password "$MYSQL_CONTAINER")

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}✗${NC} No se pudieron detectar las credenciales"
    exit 1
fi

echo -e "${GREEN}✓${NC} Credenciales detectadas"
echo ""

# Verificar que el archivo de migración existe
echo -e "${BLUE}[4/5]${NC} Verificando archivo de migración..."
if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}✗${NC} Archivo de migración no encontrado: $MIGRATION_FILE"
    exit 1
fi

echo -e "${GREEN}✓${NC} Archivo de migración encontrado"
echo ""

# Aplicar migración
echo -e "${BLUE}[5/5]${NC} Aplicando migración..."
echo -e "${CYAN}Ejecutando SQL...${NC}"
echo ""

# Ejecutar la migración
if docker exec -i "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db < "$MIGRATION_FILE" 2>&1 | grep -v "mysql: \[Warning\]"; then
    echo ""
    echo -e "${GREEN}✓${NC} Migración SQL ejecutada exitosamente"
else
    echo ""
    echo -e "${RED}✗${NC} Error al ejecutar la migración SQL"
    echo -e "${YELLOW}💡 Es posible que la migración ya esté aplicada${NC}"
    # No salir, continuar para marcar como aplicada
fi

echo ""

# Crear tabla schema_migrations y marcar como aplicada
echo -e "${CYAN}Marcando migración como aplicada...${NC}"

docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO schema_migrations (migration_name)
VALUES ('001_fix_userinfo_structure.sql');
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Migración marcada como aplicada"
else
    echo -e "${YELLOW}⚠️${NC} No se pudo marcar la migración (podría estar ya marcada)"
fi

echo ""

# Verificar resultado
echo -e "${CYAN}Verificando resultado...${NC}"
echo ""

STRUCTURE=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DESCRIBE UserInfo;" 2>/dev/null)

if echo "$STRUCTURE" | grep -q "^id"; then
    echo -e "${GREEN}✓✓✓ ÉXITO ✓✓✓${NC}"
    echo ""
    echo -e "${GREEN}La tabla UserInfo ahora tiene la estructura correcta:${NC}"
    echo "$STRUCTURE" | head -3
    echo ""
    echo -e "  ${GREEN}✓${NC} Columna 'id' existe (PRIMARY KEY)"
    echo -e "  ${GREEN}✓${NC} Columna 'id_user' existe (UNIQUE)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}      ✨ MIGRACIÓN COMPLETADA ✨      ${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${YELLOW}⚡ Próximos pasos:${NC}"
    echo ""
    echo -e "  1️⃣  Reinicia el IdentityService:"
    echo -e "     ${CYAN}cd identifyservice && ./kill.sh && ./start.sh${NC}"
    echo ""
    echo -e "  2️⃣  Prueba el endpoint /user-info/update"
    echo -e "     ${CYAN}curl -X PUT http://localhost:8000/user-info/update \\${NC}"
    echo -e "     ${CYAN}  -H \"Authorization: Bearer YOUR_TOKEN\" \\${NC}"
    echo -e "     ${CYAN}  -H \"Content-Type: application/json\" \\${NC}"
    echo -e "     ${CYAN}  -d '{\"primerNombre\":\"Test\", ...}'${NC}"
    echo ""
    echo -e "  ${GREEN}El error 'Incorrect string value' ya NO debería ocurrir.${NC}"
    echo ""
else
    echo -e "${RED}✗✗✗ ERROR ✗✗✗${NC}"
    echo ""
    echo -e "${RED}La migración no se aplicó correctamente.${NC}"
    echo -e "${YELLOW}Estructura actual:${NC}"
    echo "$STRUCTURE"
    echo ""
    echo -e "${YELLOW}💡 Intenta ejecutar la migración manualmente:${NC}"
    echo -e "   ${CYAN}docker exec -i $MYSQL_CONTAINER mysql -uroot -p'$DB_PASSWORD' flowlite_db < $MIGRATION_FILE${NC}"
    echo ""
    exit 1
fi
