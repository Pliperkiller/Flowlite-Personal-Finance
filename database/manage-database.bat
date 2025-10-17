@echo off
REM ===========================================
REM SCRIPT DE GESTIÓN DE BASE DE DATOS COMPARTIDA (BATCH)
REM ===========================================

setlocal enabledelayedexpansion

REM Verificar si se proporcionó un comando
if "%~1"=="" set "%~1=help"

REM Procesar comando
if /i "%1"=="start-db" goto :start_database
if /i "%1"=="stop-db" goto :stop_database
if /i "%1"=="restart-db" goto :restart_database
if /i "%1"=="start-app" goto :start_application
if /i "%1"=="stop-app" goto :stop_application
if /i "%1"=="restart-app" goto :restart_application
if /i "%1"=="start-all" goto :start_all
if /i "%1"=="stop-all" goto :stop_all
if /i "%1"=="status" goto :show_status
if /i "%1"=="logs-db" goto :show_database_logs
if /i "%1"=="logs-app" goto :show_application_logs
if /i "%1"=="clean" goto :clean_all
if /i "%1"=="help" goto :show_help
goto :show_help

:show_help
echo === GESTIÓN DE BASE DE DATOS COMPARTIDA ===
echo.
echo Uso: manage-database.bat [COMANDO]
echo.
echo Comandos disponibles:
echo   start-db     - Iniciar base de datos compartida
echo   stop-db      - Detener base de datos compartida
echo   restart-db   - Reiniciar base de datos compartida
echo   start-app    - Iniciar aplicación (requiere DB activa)
echo   stop-app     - Detener aplicación
echo   restart-app  - Reiniciar aplicación
echo   start-all    - Iniciar base de datos y aplicación
echo   stop-all     - Detener todo
echo   status       - Ver estado de todos los servicios
echo   logs-db      - Ver logs de la base de datos
echo   logs-app     - Ver logs de la aplicación
echo   clean        - Limpiar volúmenes y contenedores
echo   help         - Mostrar esta ayuda
echo.
goto :end

:start_database
echo Iniciando base de datos compartida...
docker-compose -f docker-compose.database.yml up -d
if %errorlevel% equ 0 (
    echo Base de datos iniciada correctamente
    echo phpMyAdmin disponible en: http://localhost:8081
) else (
    echo ❌ Error al iniciar la base de datos
    exit /b 1
)
goto :end

:stop_database
echo Deteniendo base de datos compartida...
docker-compose -f docker-compose.database.yml down
if %errorlevel% equ 0 (
    echo Base de datos detenida
) else (
    echo ❌ Error al detener la base de datos
    exit /b 1
)
goto :end

:restart_database
call :stop_database
call :start_database
goto :end

:start_application
echo Iniciando aplicación...
echo Nota: Ejecuta este comando desde la carpeta del servicio
echo Ejemplo: cd ../identifyservice && docker-compose up -d
goto :end

:stop_application
echo Deteniendo aplicación...
echo Nota: Ejecuta este comando desde la carpeta del servicio
echo Ejemplo: cd ../identifyservice && docker-compose down
goto :end

:restart_application
call :stop_application
call :start_application
goto :end

:start_all
call :start_database
timeout /t 10 /nobreak >nul
call :start_application
goto :end

:stop_all
call :stop_application
call :stop_database
goto :end

:show_status
echo === ESTADO DE BASE DE DATOS ===
docker-compose -f docker-compose.database.yml ps
echo.
echo === ESTADO DE APLICACIONES ===
echo Para ver el estado de las aplicaciones, ejecuta desde cada carpeta de servicio:
echo cd ../identifyservice && docker-compose ps
goto :end

:show_database_logs
echo 📋 Logs de Base de Datos:
docker-compose -f docker-compose.database.yml logs -f
goto :end

:show_application_logs
echo Para ver logs de aplicaciones, ejecuta desde cada carpeta de servicio:
echo cd ../identifyservice && docker-compose logs -f
goto :end

:clean_all
echo ⚠️  ADVERTENCIA: Esto eliminará todos los datos de la base de datos
set /p response=¿Estás seguro? (y/N):
if /i "%response%"=="y" (
    echo Limpiando contenedores y volúmenes...
    docker-compose down -v
    docker-compose -f docker-compose.database.yml down -v
    docker system prune -f
    echo Limpieza completada
) else (
    echo Operación cancelada
)
goto :end

:end
