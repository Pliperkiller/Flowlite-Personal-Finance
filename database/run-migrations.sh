#!/bin/bash

# ============================================
# Script para ejecutar migraciones de base de datos
# ============================================

# No usar set -e para poder manejar errores manualmente
set +e

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
DB_PASSWORD="${DB_PASSWORD:-}"

# Variables globales para almacenar el método de conexión detectado
MYSQL_CONTAINER=""
MYSQL_CONNECTION_METHOD=""

# Función para detectar el contenedor MySQL
detect_mysql_container() {
    echo -e "${YELLOW}🔍 Detectando contenedor MySQL...${NC}"

    # Verificar si Docker está disponible
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker no está disponible${NC}"
        return 1
    fi

    # Intentar detectar diferentes nombres de contenedores MySQL
    local containers=("flowlite-mysql" "flowlite-shared-mysql" "mysql")

    for container in "${containers[@]}"; do
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
            MYSQL_CONTAINER="$container"
            echo -e "${GREEN}✓${NC} Contenedor MySQL detectado: $MYSQL_CONTAINER"
            return 0
        fi
    done

    echo -e "${YELLOW}⚠️  No se detectó contenedor Docker MySQL corriendo${NC}"
    return 1
}

# Función para detectar credenciales correctas
detect_mysql_credentials() {
    local container=$1

    # Intentar diferentes combinaciones de credenciales comunes
    local passwords=("rootpassword" "Flowlite10+" "flowlite123" "")

    for password in "${passwords[@]}"; do
        if [ -n "$password" ]; then
            echo -e "${YELLOW}   Probando credenciales...${NC}" >&2
        fi
        if docker exec "$container" mysql -u"$DB_USER" -p"$password" -e "SELECT 1" >/dev/null 2>&1; then
            DB_PASSWORD="$password"
            echo -e "${GREEN}✓${NC} Credenciales MySQL detectadas correctamente"
            return 0
        fi
    done

    echo -e "${YELLOW}⚠️  No se pudieron detectar credenciales automáticamente${NC}"
    return 1
}

# Función para ejecutar comando MySQL (abstrae Docker vs conexión directa)
mysql_exec() {
    local sql_command="$1"
    local input_file="$2"

    if [ "$MYSQL_CONNECTION_METHOD" = "docker" ]; then
        if [ -n "$input_file" ]; then
            # Ejecutar desde archivo
            docker exec -i "$MYSQL_CONTAINER" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$input_file" 2>&1 | grep -v "mysql: \[Warning\]"
        else
            # Ejecutar comando directo
            docker exec "$MYSQL_CONTAINER" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "$sql_command" 2>/dev/null
        fi
    elif [ "$MYSQL_CONNECTION_METHOD" = "direct" ]; then
        if [ -n "$input_file" ]; then
            mysql -h"$DB_HOST" -u"$DB_USER" -p"${DB_PASSWORD}" "$DB_NAME" < "$input_file" 2>&1 | grep -v "mysql: \[Warning\]"
        else
            mysql -h"$DB_HOST" -u"$DB_USER" -p"${DB_PASSWORD}" "$DB_NAME" -e "$sql_command" 2>/dev/null
        fi
    else
        echo -e "${RED}✗${NC} Método de conexión no configurado"
        return 1
    fi
}

# Función para obtener un valor de MySQL
mysql_query() {
    local sql_command="$1"

    if [ "$MYSQL_CONNECTION_METHOD" = "docker" ]; then
        docker exec "$MYSQL_CONTAINER" mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -se "$sql_command" 2>/dev/null
    elif [ "$MYSQL_CONNECTION_METHOD" = "direct" ]; then
        mysql -h"$DB_HOST" -u"$DB_USER" -p"${DB_PASSWORD}" "$DB_NAME" -se "$sql_command" 2>/dev/null
    else
        return 1
    fi
}

# Función para verificar si MySQL está disponible
check_mysql_available() {
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Verificando disponibilidad de MySQL...${NC}"

    # Primero detectar el contenedor Docker
    if detect_mysql_container; then
        # Detectar credenciales correctas
        if ! detect_mysql_credentials "$MYSQL_CONTAINER"; then
            echo -e "${RED}✗${NC} No se pudieron detectar las credenciales correctas"
            echo -e "${YELLOW}💡 Configura DB_PASSWORD manualmente:${NC}"
            echo -e "   export DB_PASSWORD='tu_password'"
            echo -e "   ./run-migrations.sh"
            return 1
        fi

        MYSQL_CONNECTION_METHOD="docker"

        # Esperar a que MySQL esté completamente listo
        while [ $attempt -lt $max_attempts ]; do
            if docker exec "$MYSQL_CONTAINER" mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} MySQL está disponible (vía Docker)"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 2
        done

        echo -e "${RED}✗${NC} MySQL no respondió después de $max_attempts intentos"
        return 1
    fi

    # Si no hay Docker, intentar conexión directa
    if command -v mysql >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Intentando conexión MySQL directa (sin Docker)...${NC}"
        MYSQL_CONNECTION_METHOD="direct"

        while [ $attempt -lt $max_attempts ]; do
            if mysql -h"$DB_HOST" -u"$DB_USER" -p"${DB_PASSWORD}" -e "SELECT 1" >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} MySQL está disponible (conexión directa)"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 2
        done

        echo -e "${RED}✗${NC} No se puede conectar a MySQL (intentos: $max_attempts)"
        return 1
    fi

    # No hay Docker ni mysql client
    echo -e "${RED}✗${NC} No se puede conectar a MySQL"
    echo ""
    echo -e "${YELLOW}💡 Sugerencias:${NC}"
    echo -e "   ${BLUE}Opción 1:${NC} Inicia MySQL con Docker:"
    echo -e "      cd infrastructureservice && docker-compose up -d mysql"
    echo ""
    echo -e "   ${BLUE}Opción 2:${NC} Ejecuta las migraciones manualmente:"
    echo -e "      mysql -u root -p flowlite_db < database/migrations/001_fix_userinfo_structure.sql"
    echo ""
    echo -e "   ${BLUE}Opción 3:${NC} Salta las migraciones por ahora:"
    echo -e "      Las migraciones se ejecutarán en el próximo inicio"
    echo ""
    return 1
}

# Función para verificar si una migración ya fue ejecutada
is_migration_applied() {
    local migration_name=$1

    # Crear tabla de migraciones si no existe
    mysql_exec "
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    " ""

    # Verificar si la migración ya fue aplicada
    local count=$(mysql_query "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = '$migration_name'")

    if [ "$count" = "1" ]; then
        return 0  # Ya fue aplicada
    else
        return 1  # No ha sido aplicada
    fi
}

# Función para marcar una migración como aplicada
mark_migration_applied() {
    local migration_name=$1
    mysql_exec "INSERT INTO schema_migrations (migration_name) VALUES ('$migration_name')" ""
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
    if mysql_exec "" "$migration_file"; then
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
    echo "  DB_PASSWORD - Contraseña de MySQL (auto-detectada)"
    echo ""
    echo "El script detecta automáticamente:"
    echo "  • Contenedor Docker MySQL (flowlite-mysql, flowlite-shared-mysql, etc.)"
    echo "  • Credenciales correctas (prueba passwords comunes)"
    echo "  • Conexión directa si Docker no está disponible"
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
