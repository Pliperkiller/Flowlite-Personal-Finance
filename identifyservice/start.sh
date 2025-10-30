#!/bin/bash

# Script para iniciar IdentityService con configuración del .env

echo "🚀 Iniciando IdentityService..."

# Cargar variables de entorno desde .env
if [ -f .env ]; then
    echo "✓ Cargando variables de entorno desde .env"
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠ Archivo .env no encontrado, usando valores por defecto"
fi


# Configurar Java según sistema operativo
UNAME_OUT="$(uname -s)"
if [[ "$UNAME_OUT" == "Darwin" ]]; then
    # macOS (Homebrew)
    export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
    export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
elif [[ "$UNAME_OUT" == "Linux" ]]; then
    # Linux/WSL: buscar OpenJDK 17
    if [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
        export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
        export PATH="$JAVA_HOME/bin:$PATH"
    fi
fi

# Verificar que Java esté instalado
if ! command -v java &> /dev/null; then
    echo "❌ Error: Java 17 no está instalado"
    echo "Ejecuta: brew install openjdk@17"
    exit 1
fi

echo "✓ Java version: $(java -version 2>&1 | head -1)"
echo "✓ Server port: ${SERVER_PORT:-8000}"
echo "✓ Database: ${SPRING_DATASOURCE_URL:-jdbc:mysql://localhost:3306/flowlite_db}"
echo "✓ Redis: ${SPRING_DATA_REDIS_HOST:-localhost}:${SPRING_DATA_REDIS_PORT:-6379}"
echo ""

# Iniciar el servicio
echo "Iniciando servicio en http://localhost:${SERVER_PORT:-8000}"
echo "Swagger UI: http://localhost:${SERVER_PORT:-8000}/swagger-ui.html"
echo ""
echo "Presiona Ctrl+C para detener el servicio"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

gradle bootRun
