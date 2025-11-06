#!/bin/bash

# ============================================
# Script para ejecutar migraciones de base de datos
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="$SCRIPT_DIR/migrations"

# Configuración de base de datos (usar variables de entorno o valores por defecto)
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-flowlite_db}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-flowlite123}"

# Función para verificar si MySQL está disponible
check_mysql_available() {
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Verificando disponibilidad de MySQL...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if docker exec flowlite-mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} MySQL está disponible"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    echo -e "${RED}✗${NC} MySQL no está disponible después de $max_attempts intentos"
    return 1
}

# Función para verificar si una migración ya fue ejecutada
is_migration_applied() {
    local migration_name=$1

    # Crear tabla de migraciones si no existe
    docker exec flowlite-mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    " 2>/dev/null

    # Verificar si la migración ya fue aplicada
    local count=$(docker exec flowlite-mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -se "
        SELECT COUNT(*) FROM schema_migrations WHERE migration_name = '$migration_name';
    " 2>/dev/null)

    if [ "$count" = "1" ]; then
        return 0  # Ya fue aplicada
    else
        return 1  # No ha sido aplicada
    fi
}

# Función para marcar una migración como aplicada
mark_migration_applied() {
    local migration_name=$1

    docker exec flowlite-mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        INSERT INTO schema_migrations (migration_name) VALUES ('$migration_name');
    " 2>/dev/null
}

# Función para ejecutar una migración
run_migration() {
    local migration_file=$1
    local migration_name=$(basename "$migration_file")

    echo -e "${CYAN}📄 Procesando migración: $migration_name${NC}"

    if is_migration_applied "$migration_name"; then
        echo -e "${YELLOW}⏭  Migración ya aplicada, saltando...${NC}"
        return 0
    fi

    echo -e "${BLUE}⚙️  Ejecutando migración...${NC}"

    # Ejecutar la migración
    if docker exec -i flowlite-mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$migration_file" 2>&1 | grep -v "mysql: \[Warning\]"; then
        # Marcar como aplicada
        mark_migration_applied "$migration_name"
        echo -e "${GREEN}✓${NC} Migración aplicada exitosamente"
        return 0
    else
        echo -e "${RED}✗${NC} Error al ejecutar migración"
        return 1
    fi
}

# Función para listar migraciones disponibles
list_migrations() {
    echo -e "${CYAN}📋 Migraciones disponibles:${NC}"
    echo ""

    for migration_file in "$MIGRATIONS_DIR"/*.sql; do
        if [ -f "$migration_file" ]; then
            local migration_name=$(basename "$migration_file")

            if is_migration_applied "$migration_name"; then
                echo -e "  ${GREEN}✓${NC} $migration_name (aplicada)"
            else
                echo -e "  ${YELLOW}○${NC} $migration_name (pendiente)"
            fi
        fi
    done
    echo ""
}

# Función para ejecutar todas las migraciones pendientes
run_all_migrations() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}      🔄 EJECUTANDO MIGRACIONES DE BASE DE DATOS      ${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Verificar que MySQL esté disponible
    if ! check_mysql_available; then
        echo -e "${RED}✗${NC} No se puede conectar a MySQL"
        exit 1
    fi

    # Verificar que el directorio de migraciones exista
    if [ ! -d "$MIGRATIONS_DIR" ]; then
        echo -e "${RED}✗${NC} Directorio de migraciones no encontrado: $MIGRATIONS_DIR"
        exit 1
    fi

    # Contar migraciones
    local migration_count=$(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | wc -l)

    if [ "$migration_count" -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No se encontraron migraciones${NC}"
        return 0
    fi

    echo -e "${BLUE}📊 Encontradas $migration_count migraciones${NC}"
    echo ""

    # Ejecutar migraciones en orden alfabético
    local applied=0
    local skipped=0
    local failed=0

    for migration_file in "$MIGRATIONS_DIR"/*.sql; do
        if [ -f "$migration_file" ]; then
            if run_migration "$migration_file"; then
                if is_migration_applied "$(basename "$migration_file")"; then
                    applied=$((applied + 1))
                else
                    skipped=$((skipped + 1))
                fi
            else
                failed=$((failed + 1))
                echo -e "${RED}✗${NC} Error en migración: $(basename "$migration_file")"
                exit 1
            fi
            echo ""
        fi
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}✓ MIGRACIONES COMPLETADAS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "  ${GREEN}✓${NC} Aplicadas: $applied"
    echo -e "  ${YELLOW}⏭${NC}  Saltadas:  $skipped"
    echo -e "  ${RED}✗${NC} Fallidas:  $failed"
    echo ""
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}=== GESTOR DE MIGRACIONES DE BASE DE DATOS ===${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  run      - Ejecutar todas las migraciones pendientes (por defecto)"
    echo "  list     - Listar todas las migraciones y su estado"
    echo "  help     - Mostrar esta ayuda"
    echo ""
    echo "Variables de entorno:"
    echo "  DB_HOST     - Host de MySQL (default: 127.0.0.1)"
    echo "  DB_PORT     - Puerto de MySQL (default: 3306)"
    echo "  DB_NAME     - Nombre de la base de datos (default: flowlite_db)"
    echo "  DB_USER     - Usuario de MySQL (default: root)"
    echo "  DB_PASSWORD - Contraseña de MySQL (default: flowlite123)"
    echo ""
}

# Procesar comando
case "${1:-run}" in
    run)
        run_all_migrations
        ;;
    list)
        check_mysql_available
        list_migrations
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}✗${NC} Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac
