@echo off
REM ===========================================
REM SCRIPT DE GESTIÓN DE MAILHOG (WINDOWS)
REM ===========================================

setlocal enabledelayedexpansion

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help

if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="clean" goto :clean
if "%1"=="web" goto :web
if "%1"=="check" goto :check

echo Comando no reconocido: %1
goto :help

:help
echo === GESTIÓN DE MAILHOG ===
echo.
echo Uso: %0 [comando]
echo.
echo Comandos disponibles:
echo   start     - Iniciar MailHog
echo   stop      - Detener MailHog
echo   restart   - Reiniciar MailHog
echo   status    - Ver estado de MailHog
echo   logs      - Ver logs de MailHog
echo   clean     - Limpiar datos de MailHog
echo   web       - Abrir interfaz web de MailHog
echo   help      - Mostrar esta ayuda
echo.
echo Ejemplos:
echo   %0 start
echo   %0 logs
echo   %0 web
goto :end

:start
echo Iniciando MailHog...
docker network create flowlite-network 2>nul
docker-compose up -d
echo MailHog iniciado correctamente
echo SMTP Server: localhost:1025
echo Web UI: http://localhost:8025
goto :end

:stop
echo Deteniendo MailHog...
docker-compose down
echo MailHog detenido
goto :end

:restart
echo Reiniciando MailHog...
call :stop
call :start
goto :end

:status
echo Estado de MailHog:
docker-compose ps
goto :end

:logs
echo Logs de MailHog:
docker-compose logs -f
goto :end

:clean
echo ¿Estás seguro de que quieres limpiar todos los datos de MailHog? (y/N)
set /p response=
if /i "%response%"=="y" (
    echo Limpiando datos de MailHog...
    docker-compose down -v
    docker volume rm mailhog_mailhog_data 2>nul
    echo Datos limpiados
) else (
    echo Operación cancelada
)
goto :end

:web
echo Abriendo interfaz web de MailHog...
start http://localhost:8025
goto :end

:check
echo Verificando configuración...
netstat -an | findstr :1025 >nul
if %errorlevel%==0 (
    echo ✓ Puerto 1025 disponible
) else (
    echo ⚠ Puerto 1025 en uso
)
netstat -an | findstr :8025 >nul
if %errorlevel%==0 (
    echo ✓ Puerto 8025 disponible
) else (
    echo ⚠ Puerto 8025 en uso
)
goto :end

:end
