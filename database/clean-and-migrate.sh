#!/bin/bash

# ============================================
# Script para limpiar y aplicar migración desde cero
# Útil cuando hay datos incompatibles en UserInfo
# ============================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="$SCRIPT_DIR/migrations/001_fix_userinfo_structure.sql"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}      ⚠️  LIMPIEZA Y MIGRACIÓN DESDE CERO      ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará todos los datos de UserInfo${NC}"
echo ""

# Función para verificar Docker
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Docker no está disponible"
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
if ! check_docker; then
    exit 1
fi

# Encontrar contenedor
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

# Mostrar datos actuales
echo -e "${YELLOW}Datos actuales en UserInfo:${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "SELECT COUNT(*) as total_registros FROM UserInfo;" 2>/dev/null || echo "No se pudo consultar"
echo ""

# Confirmar
read -p "¿Estás seguro de que quieres eliminar todos los datos? (escribe 'SI' en mayúsculas): " -r
echo
if [[ ! $REPLY == "SI" ]]; then
    echo -e "${YELLOW}Operación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Limpiando y recreando tabla UserInfo...${NC}"
echo ""

# Script SQL simplificado
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db <<'EOSQL'
-- Eliminar tabla existente
DROP TABLE IF EXISTS UserInfo;

-- Crear tabla con estructura correcta
CREATE TABLE UserInfo (
    -- ID único de la información personal (clave primaria)
    id BINARY(16) NOT NULL PRIMARY KEY,

    -- Referencia al usuario (clave foránea)
    id_user BINARY(16) NOT NULL UNIQUE,

    -- Información personal básica
    primerNombre VARCHAR(50),
    segundoNombre VARCHAR(50),
    primerApellido VARCHAR(50),
    segundoApellido VARCHAR(50),
    telefono VARCHAR(15),
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    pais VARCHAR(100),
    fechaNacimiento DATE,

    -- Información de identificación
    numeroIdentificacion VARCHAR(20) UNIQUE,
    tipoIdentificacion VARCHAR(10),

    -- Información adicional
    genero VARCHAR(20),
    estadoCivil VARCHAR(30),
    ocupacion VARCHAR(100),

    -- Metadatos
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,

    -- Índices para mejorar el rendimiento
    INDEX idx_id_user (id_user),
    INDEX idx_numeroIdentificacion (numeroIdentificacion),
    INDEX idx_telefono (telefono)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
EOSQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Tabla UserInfo recreada correctamente"
else
    echo -e "${RED}✗${NC} Error al recrear la tabla"
    exit 1
fi

echo ""

# Marcar migración como aplicada
echo -e "${BLUE}Marcando migración como aplicada...${NC}"
docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO schema_migrations (migration_name)
VALUES ('001_fix_userinfo_structure.sql');
" 2>/dev/null

echo -e "${GREEN}✓${NC} Migración marcada como aplicada"
echo ""

# Verificar resultado
echo -e "${CYAN}Verificando estructura final...${NC}"
STRUCTURE=$(docker exec "$MYSQL_CONTAINER" mysql -uroot -p"$DB_PASSWORD" flowlite_db -e "DESCRIBE UserInfo;" 2>/dev/null)

if echo "$STRUCTURE" | grep -q "^id.*BINARY"; then
    echo ""
    echo -e "${GREEN}✓✓✓ ÉXITO ✓✓✓${NC}"
    echo ""
    echo -e "${GREEN}Estructura correcta:${NC}"
    echo "$STRUCTURE" | head -3
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
    echo ""
    echo -e "  ${GREEN}El error ya NO debería ocurrir.${NC}"
    echo ""
else
    echo -e "${RED}✗${NC} Algo salió mal"
    exit 1
fi
