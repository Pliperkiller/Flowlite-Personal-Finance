# ===========================================
# SCRIPT DE GESTIÓN PARA REDIS (POWERSHELL)
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
    Write-Host "===========================================" -ForegroundColor $BLUE
    Write-Host "  GESTIÓN DE REDIS PARA FLOWLITE" -ForegroundColor $BLUE
    Write-Host "===========================================" -ForegroundColor $BLUE
    Write-Host ""
    Write-Host "Uso: .\manage-redis.ps1 [COMANDO]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  start     - Iniciar Redis"
    Write-Host "  stop      - Detener Redis"
    Write-Host "  restart   - Reiniciar Redis"
    Write-Host "  status    - Ver estado de Redis"
    Write-Host "  logs      - Ver logs de Redis"
    Write-Host "  connect   - Conectar a Redis CLI"
    Write-Host "  clean     - Limpiar datos de Redis"
    Write-Host "  help      - Mostrar esta ayuda"
    Write-Host ""
}

# Función para iniciar Redis
function Start-Redis {
    Write-Host "🚀 Iniciando Redis..." -ForegroundColor $GREEN
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis iniciado correctamente" -ForegroundColor $GREEN
        Write-Host "📍 Puerto: 6379" -ForegroundColor $BLUE
        Write-Host "📍 Host: localhost" -ForegroundColor $BLUE
    } else {
        Write-Host "❌ Error al iniciar Redis" -ForegroundColor $RED
    }
}

# Función para detener Redis
function Stop-Redis {
    Write-Host "🛑 Deteniendo Redis..." -ForegroundColor $YELLOW
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis detenido correctamente" -ForegroundColor $GREEN
    } else {
        Write-Host "❌ Error al detener Redis" -ForegroundColor $RED
    }
}

# Función para reiniciar Redis
function Restart-Redis {
    Write-Host "🔄 Reiniciando Redis..." -ForegroundColor $YELLOW
    docker-compose down
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis reiniciado correctamente" -ForegroundColor $GREEN
    } else {
        Write-Host "❌ Error al reiniciar Redis" -ForegroundColor $RED
    }
}

# Función para ver estado
function Show-Status {
    Write-Host "📊 Estado de Redis:" -ForegroundColor $BLUE
    docker-compose ps
    Write-Host ""
    Write-Host "📊 Información del contenedor:" -ForegroundColor $BLUE
    try {
        $status = docker inspect flowlite-redis --format='{{.State.Status}}' 2>$null
        if ($status) {
            Write-Host "Estado: $status" -ForegroundColor $GREEN
        } else {
            Write-Host "Contenedor no encontrado" -ForegroundColor $YELLOW
        }
    } catch {
        Write-Host "Contenedor no encontrado" -ForegroundColor $YELLOW
    }
}

# Función para ver logs
function Show-Logs {
    Write-Host "📋 Logs de Redis:" -ForegroundColor $BLUE
    docker-compose logs -f
}

# Función para conectar a Redis CLI
function Connect-Redis {
    Write-Host "🔗 Conectando a Redis CLI..." -ForegroundColor $BLUE
    docker exec -it flowlite-redis redis-cli
}

# Función para limpiar datos
function Clean-Redis {
    Write-Host "⚠️  ¿Estás seguro de que quieres limpiar todos los datos de Redis? (y/N)" -ForegroundColor $RED
    $response = Read-Host
    if ($response -match "^[Yy]$") {
        Write-Host "🧹 Limpiando datos de Redis..." -ForegroundColor $YELLOW
        docker-compose down -v
        try {
            docker volume rm redis_redis_data 2>$null
        } catch {
            # Ignorar errores si el volumen no existe
        }
        Write-Host "✅ Datos de Redis limpiados" -ForegroundColor $GREEN
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor $BLUE
    }
}

# Procesar comando
switch ($Command.ToLower()) {
    "start" {
        Start-Redis
    }
    "stop" {
        Stop-Redis
    }
    "restart" {
        Restart-Redis
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "connect" {
        Connect-Redis
    }
    "clean" {
        Clean-Redis
    }
    default {
        Show-Help
    }
}
