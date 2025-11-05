#!/bin/bash
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Flowlite - Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Verificar que Docker esté corriendo
print_info "Verificando Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi
print_success "Docker está corriendo"

# 2. Detener contenedores existentes
print_info "Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true
print_success "Contenedores detenidos"

# 3. Limpiar imágenes antiguas del proyecto
print_warning "Limpiando imágenes antiguas de infrastructureservice..."
docker images | grep infrastructureservice-db-init | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
print_success "Imágenes antiguas eliminadas"

# 4. Limpiar volúmenes huérfanos (opcional pero recomendado)
print_info "Limpiando volúmenes huérfanos..."
docker volume prune -f > /dev/null 2>&1 || true
print_success "Volúmenes limpiados"

# 5. Reconstruir la imagen db-init desde cero (sin caché)
print_info "Reconstruyendo imagen db-init desde cero (esto puede tomar unos minutos)..."
docker-compose build --no-cache db-init
print_success "Imagen db-init reconstruida"

# 6. Levantar todos los servicios
print_info "Levantando servicios..."
docker-compose up -d
print_success "Servicios iniciados"

# 7. Esperar a que db-init termine
print_info "Esperando a que la inicialización de la base de datos termine..."
sleep 5

# Esperar hasta que el contenedor db-init termine (máximo 60 segundos)
TIMEOUT=60
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    STATUS=$(docker inspect -f '{{.State.Status}}' flowlite-db-init 2>/dev/null || echo "not-found")
    if [ "$STATUS" = "exited" ]; then
        EXIT_CODE=$(docker inspect -f '{{.State.ExitCode}}' flowlite-db-init)
        if [ "$EXIT_CODE" = "0" ]; then
            print_success "Base de datos inicializada correctamente"
            break
        else
            print_error "La inicialización de la base de datos falló"
            echo ""
            print_info "Logs del contenedor db-init:"
            docker logs flowlite-db-init
            exit 1
        fi
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    print_warning "Timeout esperando la inicialización. Verifica los logs con: docker logs flowlite-db-init"
fi

# 8. Verificar que las categorías ML estén correctamente cargadas
print_info "Verificando categorías en la base de datos..."
sleep 3

CATEGORY_COUNT=$(docker exec flowlite-mysql mysql -u flowlite_user -pflowlite_password flowlite_db -se "SELECT COUNT(*) FROM TransactionCategory;" 2>/dev/null || echo "0")

if [ "$CATEGORY_COUNT" = "11" ]; then
    print_success "Categorías ML cargadas correctamente (11 categorías encontradas)"

    # Verificar que sean las categorías correctas (con underscores)
    HAS_ML_CATEGORIES=$(docker exec flowlite-mysql mysql -u flowlite_user -pflowlite_password flowlite_db -se "SELECT COUNT(*) FROM TransactionCategory WHERE description LIKE '%\_%';" 2>/dev/null || echo "0")

    if [ "$HAS_ML_CATEGORIES" -ge "10" ]; then
        print_success "Categorías con formato ML (underscores) detectadas"
    else
        print_warning "Las categorías pueden no tener el formato correcto para ML"
        print_info "Ejecuta: docker exec flowlite-mysql mysql -u flowlite_user -pflowlite_password flowlite_db -e 'SELECT description FROM TransactionCategory;'"
    fi
else
    print_warning "Se encontraron $CATEGORY_COUNT categorías (se esperaban 11)"
    print_info "Puede que la base de datos no se haya inicializado correctamente"
fi

# 9. Mostrar estado de los contenedores
echo ""
print_info "Estado de los contenedores:"
docker-compose ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup completado exitosamente${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "Servicios disponibles:"
echo "  - MySQL: localhost:3306"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ: localhost:5672 (Management: http://localhost:15672)"
echo ""
print_info "Usuarios de prueba:"
echo "  - Email: juan.perez@example.com"
echo "  - Password: password123"
echo ""
print_info "Próximos pasos:"
echo "  1. Iniciar IdentityService: cd ../identifyservice && uvicorn src.main:app --port 8000"
echo "  2. Iniciar UploadService: cd ../uploadservice && uvicorn src.main:app --port 8001"
echo "  3. Iniciar InsightService: cd ../InsightService && python main.py"
echo ""
print_info "Para ver logs: docker-compose logs -f"
print_info "Para detener: docker-compose down"
echo ""
