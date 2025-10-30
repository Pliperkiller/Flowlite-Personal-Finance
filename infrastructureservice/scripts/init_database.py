#!/usr/bin/env python3
"""
Script de Inicialización de Base de Datos - Flowlite Personal Finance

Este script inicializa la estructura de la base de datos ejecutando las migraciones
de Alembic y verifica que todas las tablas estén creadas correctamente.

Uso:
    python scripts/init_database.py

Prerequisitos:
    - MySQL debe estar corriendo (docker-compose up -d)
    - DATABASE_URL debe estar configurado en .env o como variable de entorno
"""

import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar modelos
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment():
    """Cargar variables de entorno"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Variables de entorno cargadas desde {env_file}")
    else:
        logger.warning("Archivo .env no encontrado, usando variables de entorno del sistema")


def get_database_url():
    """Obtener URL de base de datos"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL no está configurado")
        logger.info("Usando URL por defecto para desarrollo")
        database_url = "mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db"

    # Convertir aiomysql a pymysql si es necesario (para scripts síncronos)
    if 'aiomysql' in database_url:
        database_url = database_url.replace('aiomysql', 'pymysql')
        logger.info("Convertido de aiomysql a pymysql para script síncrono")

    # Ocultar contraseña en logs
    safe_url = database_url.split('@')[-1] if '@' in database_url else database_url
    logger.info(f"Conectando a: {safe_url}")

    return database_url


def verify_connection(engine):
    """Verificar conexión a la base de datos"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✓ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        logger.error(f"✗ Error conectando a base de datos: {e}")
        return False


def verify_tables(engine):
    """Verificar que todas las tablas esperadas existan"""
    expected_tables = [
        'User',
        'Role',
        'UserInfo',
        'Bank',
        'TransactionCategory',
        'TransactionBatch',
        'Transaction',
        'InsightCategory',
        'Insights',
        'alembic_version'
    ]

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    logger.info(f"\nTablas encontradas: {len(existing_tables)}")

    all_present = True
    for table in expected_tables:
        if table in existing_tables:
            logger.info(f"  ✓ {table}")
        else:
            logger.error(f"  ✗ {table} - NO ENCONTRADA")
            all_present = False

    return all_present


def get_migration_status(engine):
    """Obtener estado de las migraciones"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                logger.info(f"\nVersión de migración actual: {version[0]}")
                return version[0]
            else:
                logger.warning("\nNo se encontró versión de migración")
                return None
    except Exception as e:
        logger.warning(f"\nNo se pudo obtener versión de migración: {e}")
        return None


def run_migrations():
    """Ejecutar migraciones de Alembic"""
    import subprocess

    logger.info("\n" + "="*60)
    logger.info("EJECUTANDO MIGRACIONES DE ALEMBIC")
    logger.info("="*60)

    # Cambiar al directorio de InfrastructureService
    script_dir = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=script_dir,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(result.stdout)
        logger.info("✓ Migraciones ejecutadas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Error ejecutando migraciones:")
        logger.error(e.stderr)
        return False
    except FileNotFoundError:
        logger.error("✗ Alembic no está instalado o no está en el PATH")
        logger.error("Instala las dependencias: pip install -r requirements.txt")
        return False


def main():
    """Función principal"""
    logger.info("="*60)
    logger.info("INICIALIZACIÓN DE BASE DE DATOS - FLOWLITE")
    logger.info("="*60)

    # 1. Cargar variables de entorno
    load_environment()

    # 2. Obtener URL de base de datos
    database_url = get_database_url()

    # 3. Crear engine
    try:
        engine = create_engine(database_url, echo=False)
    except Exception as e:
        logger.error(f"Error creando engine: {e}")
        sys.exit(1)

    # 4. Verificar conexión
    if not verify_connection(engine):
        logger.error("\n No se pudo conectar a la base de datos")
        logger.info("\nVerifica que:")
        logger.info("  1. MySQL esté corriendo: docker-compose ps")
        logger.info("  2. Las credenciales en .env sean correctas")
        logger.info("  3. El puerto 3306 no esté bloqueado")
        sys.exit(1)

    # 5. Ejecutar migraciones
    logger.info("\n" + "-"*60)
    if not run_migrations():
        logger.error("\n Error ejecutando migraciones")
        sys.exit(1)

    # 6. Verificar tablas
    logger.info("\n" + "-"*60)
    logger.info("VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    logger.info("-"*60)

    if not verify_tables(engine):
        logger.error("\n Algunas tablas no fueron creadas correctamente")
        sys.exit(1)

    # 7. Obtener estado de migraciones
    get_migration_status(engine)

    # 8. Éxito
    logger.info("\n" + "="*60)
    logger.info(" BASE DE DATOS INICIALIZADA CORRECTAMENTE")
    logger.info("="*60)
    logger.info("\nPróximos pasos:")
    logger.info("  1. Poblar datos de prueba: python scripts/seed_database.py")
    logger.info("  2. Iniciar servicios:")
    logger.info("     - IdentityService (puerto 8000)")
    logger.info("     - UploadService (puerto 8001)")
    logger.info("     - InsightService")
    logger.info("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nProceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n Error inesperado: {e}", exc_info=True)
        sys.exit(1)
