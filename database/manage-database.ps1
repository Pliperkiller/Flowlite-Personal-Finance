# ===========================================
# SCRIPT DE GESTIÓN DE BASE DE DATOS COMPARTIDA (POWERSHELL)
# ===========================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Colores para output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"

# Función para mostrar ayuda
function Show-Help {
    Write-Host "=== GESTIÓN DE BASE DE DATOS COMPARTIDA ===" -ForegroundColor $BLUE
    Write-Host ""
    Write-Host "Uso: .\manage-database.ps1 [COMANDO]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  start-db     - Iniciar base de datos compartida"
    Write-Host "  stop-db      - Detener base de datos compartida"
    Write-Host "  restart-db   - Reiniciar base de datos compartida"
    Write-Host "  start-app    - Iniciar aplicación (requiere DB activa)"
    Write-Host "  stop-app     - Detener aplicación"
    Write-Host "  restart-app  - Reiniciar aplicación"
    Write-Host "  start-all    - Iniciar base de datos y aplicación"
    Write-Host "  stop-all     - Detener todo"
    Write-Host "  status       - Ver estado de todos los servicios"
    Write-Host "  logs-db      - Ver logs de la base de datos"
    Write-Host "  logs-app     - Ver logs de la aplicación"
    Write-Host "  clean        - Limpiar volúmenes y contenedores"
    Write-Host "  help         - Mostrar esta ayuda"
    Write-Host ""
}

# Función para iniciar base de datos
function Start-Database {
    Write-Host "Iniciando base de datos compartida..." -ForegroundColor $YELLOW
    if (docker-compose -f docker-compose.database.yml up -d) {
        Write-Host "Base de datos iniciada correctamente" -ForegroundColor $GREEN
        Write-Host "phpMyAdmin disponible en: http://localhost:8081" -ForegroundColor $BLUE
    } else {
        Write-Host "❌ Error al iniciar la base de datos" -ForegroundColor $RED
        exit 1
    }
}

# Función para detener base de datos
function Stop-Database {
    Write-Host "Deteniendo base de datos compartida..." -ForegroundColor $YELLOW
    if (docker-compose -f docker-compose.database.yml down) {
        Write-Host "Base de datos detenida" -ForegroundColor $GREEN
    } else {
        Write-Host "❌ Error al detener la base de datos" -ForegroundColor $RED
        exit 1
    }
}

# Función para iniciar aplicación
function Start-Application {
    Write-Host "Iniciando aplicación..." -ForegroundColor $YELLOW
    Write-Host "Nota: Ejecuta este comando desde la carpeta del servicio" -ForegroundColor $BLUE
    Write-Host "Ejemplo: cd ../identifyservice && docker-compose up -d" -ForegroundColor $BLUE
}

# Función para detener aplicación
function Stop-Application {
    Write-Host "Deteniendo aplicación..." -ForegroundColor $YELLOW
    Write-Host "Nota: Ejecuta este comando desde la carpeta del servicio" -ForegroundColor $BLUE
    Write-Host "Ejemplo: cd ../identifyservice && docker-compose down" -ForegroundColor $BLUE
}

# Función para ver estado
function Show-Status {
    Write-Host "=== ESTADO DE BASE DE DATOS ===" -ForegroundColor $BLUE
    docker-compose -f docker-compose.database.yml ps
    Write-Host ""
    Write-Host "=== ESTADO DE APLICACIONES ===" -ForegroundColor $BLUE
    Write-Host "Para ver el estado de las aplicaciones, ejecuta desde cada carpeta de servicio:" -ForegroundColor $YELLOW
    Write-Host "cd ../identifyservice && docker-compose ps" -ForegroundColor $BLUE
}

# Función para ver logs de base de datos
function Show-DatabaseLogs {
    Write-Host "📋 Logs de Base de Datos:" -ForegroundColor $BLUE
    docker-compose -f docker-compose.database.yml logs -f
}

# Función para ver logs de aplicación
function Show-ApplicationLogs {
    Write-Host "Para ver logs de aplicaciones, ejecuta desde cada carpeta de servicio:" -ForegroundColor $BLUE
    Write-Host "cd ../identifyservice && docker-compose logs -f" -ForegroundColor $BLUE
}

# Función para limpiar
function Clean-All {
    Write-Host "⚠️  ADVERTENCIA: Esto eliminará todos los datos de la base de datos" -ForegroundColor $RED
    $response = Read-Host "¿Estás seguro? (y/N)"
    if ($response -match "^[Yy]$") {
        Write-Host "Limpiando contenedores y volúmenes..." -ForegroundColor $YELLOW
        docker-compose down -v
        docker-compose -f docker-compose.database.yml down -v
        docker system prune -f
        Write-Host "Limpieza completada" -ForegroundColor $GREEN
    } else {
        Write-Host "Operación cancelada" -ForegroundColor $YELLOW
    }
}

# Procesar comando
switch ($Command.ToLower()) {
    "start-db" {
        Start-Database
    }
    "stop-db" {
        Stop-Database
    }
    "restart-db" {
        Stop-Database
        Start-Database
    }
    "start-app" {
        Start-Application
    }
    "stop-app" {
        Stop-Application
    }
    "restart-app" {
        Stop-Application
        Start-Application
    }
    "start-all" {
        Start-Database
        Start-Sleep -Seconds 10
        Start-Application
    }
    "stop-all" {
        Stop-Application
        Stop-Database
    }
    "status" {
        Show-Status
    }
    "logs-db" {
        Show-DatabaseLogs
    }
    "logs-app" {
        Show-ApplicationLogs
    }
    "clean" {
        Clean-All
    }
    default {
        Show-Help
    }
}
