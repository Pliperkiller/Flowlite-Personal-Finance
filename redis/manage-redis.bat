@echo off
REM ===========================================
REM SCRIPT DE GESTIÓN PARA REDIS (BATCH)
REM ===========================================

setlocal enabledelayedexpansion

REM Verificar si se proporcionó un comando
if "%~1"=="" set "%~1=help"

REM Procesar comando
if /i "%1"=="start" goto :start_redis
if /i "%1"=="stop" goto :stop_redis
if /i "%1"=="restart" goto :restart_redis
if /i "%1"=="status" goto :show_status
if /i "%1"=="logs" goto :show_logs
if /i "%1"=="connect" goto :connect_redis
if /i "%1"=="clean" goto :clean_redis
if /i "%1"=="help" goto :show_help
goto :show_help

:show_help
echo ===========================================
echo   GESTIÓN DE REDIS PARA FLOWLITE
echo ===========================================
echo.
echo Uso: manage-redis.bat [COMANDO]
echo.
echo Comandos disponibles:
echo   start     - Iniciar Redis
echo   stop      - Detener Redis
echo   restart   - Reiniciar Redis
echo   status    - Ver estado de Redis
echo   logs      - Ver logs de Redis
echo   connect   - Conectar a Redis CLI
echo   clean     - Limpiar datos de Redis
echo   help      - Mostrar esta ayuda
echo.
goto :end

:start_redis
echo 🚀 Iniciando Redis...
docker-compose up -d
if %errorlevel% equ 0 (
    echo ✅ Redis iniciado correctamente
    echo 📍 Puerto: 6379
    echo 📍 Host: localhost
) else (
    echo ❌ Error al iniciar Redis
)
goto :end

:stop_redis
echo 🛑 Deteniendo Redis...
docker-compose down
if %errorlevel% equ 0 (
    echo ✅ Redis detenido correctamente
) else (
    echo ❌ Error al detener Redis
)
goto :end

:restart_redis
echo 🔄 Reiniciando Redis...
docker-compose down
docker-compose up -d
if %errorlevel% equ 0 (
    echo ✅ Redis reiniciado correctamente
) else (
    echo ❌ Error al reiniciar Redis
)
goto :end

:show_status
echo 📊 Estado de Redis:
docker-compose ps
echo.
echo 📊 Información del contenedor:
docker inspect flowlite-redis --format={{.State.Status}} 2>nul
if %errorlevel% neq 0 (
    echo Contenedor no encontrado
)
goto :end

:show_logs
echo 📋 Logs de Redis:
docker-compose logs -f
goto :end

:connect_redis
echo 🔗 Conectando a Redis CLI...
docker exec -it flowlite-redis redis-cli
goto :end

:clean_redis
echo ⚠️  ¿Estás seguro de que quieres limpiar todos los datos de Redis? (y/N)
set /p response=
if /i "%response%"=="y" (
    echo 🧹 Limpiando datos de Redis...
    docker-compose down -v
    docker volume rm redis_redis_data 2>nul
    echo ✅ Datos de Redis limpiados
) else (
    echo ❌ Operación cancelada
)
goto :end

:end
