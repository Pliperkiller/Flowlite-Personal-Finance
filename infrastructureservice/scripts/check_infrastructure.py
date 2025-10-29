#!/usr/bin/env python3
"""
Script de Verificación de Infraestructura - Flowlite Personal Finance

Este script verifica que todos los servicios de infraestructura estén funcionando
correctamente y sean accesibles:
- MySQL: Conexión y consultas básicas
- RabbitMQ: AMQP y Management API

Uso:
    python scripts/check_infrastructure.py

    # Con más detalles
    python scripts/check_infrastructure.py --verbose

    # Solo un servicio específico
    python scripts/check_infrastructure.py --service mysql
    python scripts/check_infrastructure.py --service rabbitmq
"""

import os
import sys
from pathlib import Path
import argparse
import time
from typing import Dict, Tuple

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """Colores ANSI para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_header(text: str):
    """Imprimir encabezado con formato"""
    logger.info(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    logger.info(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    logger.info(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def print_section(text: str):
    """Imprimir sección con formato"""
    logger.info(f"\n{Colors.BOLD}{text}{Colors.RESET}")
    logger.info(f"{'-'*60}")


def print_success(text: str):
    """Imprimir mensaje de éxito"""
    logger.info(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_error(text: str):
    """Imprimir mensaje de error"""
    logger.error(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_warning(text: str):
    """Imprimir mensaje de advertencia"""
    logger.warning(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_info(text: str):
    """Imprimir información"""
    logger.info(f"  {text}")


def load_environment() -> Dict[str, str]:
    """Cargar variables de entorno"""
    env_file = Path(__file__).parent.parent / '.env'

    if env_file.exists():
        load_dotenv(env_file)
        print_success(f"Variables de entorno cargadas desde {env_file}")
    else:
        print_warning("Archivo .env no encontrado, usando valores por defecto")

    # Cargar variables con valores por defecto
    config = {
        'MYSQL_HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'MYSQL_PORT': os.getenv('MYSQL_PORT', '3306'),
        'MYSQL_USER': os.getenv('MYSQL_USER', 'flowlite_user'),
        'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', 'flowlite_password'),
        'MYSQL_DATABASE': os.getenv('MYSQL_DATABASE', 'flowlite_db'),
        'RABBITMQ_HOST': os.getenv('RABBITMQ_HOST', 'localhost'),
        'RABBITMQ_PORT': os.getenv('RABBITMQ_PORT', '5672'),
        'RABBITMQ_USER': os.getenv('RABBITMQ_USER', 'admin'),
        'RABBITMQ_PASSWORD': os.getenv('RABBITMQ_PASSWORD', 'admin'),
        'RABBITMQ_MANAGEMENT_PORT': os.getenv('RABBITMQ_MANAGEMENT_PORT', '15672'),
        'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
        'REDIS_PORT': os.getenv('REDIS_PORT', '6379'),
        'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', 'flowlite_redis_pass_2024'),
        'REDIS_DB': os.getenv('REDIS_DB', '0'),
    }

    return config


def check_docker_containers() -> bool:
    """Verificar que los contenedores Docker estén corriendo"""
    import subprocess

    print_section("Verificando Contenedores Docker")

    try:
        # Verificar que Docker esté disponible
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print_info(f"Docker: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Docker no está instalado o no está disponible")
        return False

    try:
        # Verificar contenedores con docker-compose
        result = subprocess.run(
            ['docker-compose', 'ps'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            check=False
        )

        output = result.stdout

        # Verificar flowlite-mysql
        if 'flowlite-mysql' in output:
            if 'Up' in output or 'running' in output.lower():
                print_success("Contenedor MySQL (flowlite-mysql) está corriendo")
            else:
                print_error("Contenedor MySQL existe pero no está corriendo")
                return False
        else:
            print_error("Contenedor MySQL (flowlite-mysql) no encontrado")
            return False

        # Verificar flowlite-rabbitmq
        if 'flowlite-rabbitmq' in output:
            if 'Up' in output or 'running' in output.lower():
                print_success("Contenedor RabbitMQ (flowlite-rabbitmq) está corriendo")
            else:
                print_error("Contenedor RabbitMQ existe pero no está corriendo")
                return False
        else:
            print_error("Contenedor RabbitMQ (flowlite-rabbitmq) no encontrado")
            return False

        # Verificar flowlite-redis
        if 'flowlite-redis' in output:
            if 'Up' in output or 'running' in output.lower():
                print_success("Contenedor Redis (flowlite-redis) está corriendo")
            else:
                print_error("Contenedor Redis existe pero no está corriendo")
                return False
        else:
            print_error("Contenedor Redis (flowlite-redis) no encontrado")
            return False

        return True

    except Exception as e:
        print_error(f"Error verificando contenedores: {e}")
        print_warning("Ejecuta: docker-compose up -d")
        return False


def check_mysql_connection(config: Dict[str, str], verbose: bool = False) -> Tuple[bool, Dict]:
    """Verificar conexión a MySQL"""
    print_section("Verificando MySQL")

    results = {
        'connection': False,
        'query': False,
        'tables': False,
        'migrations': False
    }

    # Usar pymysql (síncrono) para scripts
    database_url = (
        f"mysql+pymysql://{config['MYSQL_USER']}:{config['MYSQL_PASSWORD']}"
        f"@{config['MYSQL_HOST']}:{config['MYSQL_PORT']}/{config['MYSQL_DATABASE']}"
    )

    safe_url = f"{config['MYSQL_USER']}@{config['MYSQL_HOST']}:{config['MYSQL_PORT']}/{config['MYSQL_DATABASE']}"
    print_info(f"Conectando a: {safe_url}")

    try:
        # 1. Probar conexión
        engine = create_engine(database_url, echo=False, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print_success("Conexión a MySQL exitosa")
        results['connection'] = True

        # 2. Probar consultas básicas
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print_success(f"MySQL versión: {version}")
            results['query'] = True

        # 3. Verificar tablas existentes
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print_success(f"Base de datos tiene {len(tables)} tablas")
                results['tables'] = True

                expected_tables = [
                    'User', 'Role', 'UserInfo', 'Bank', 'TransactionCategory',
                    'TransactionBatch', 'Transaction', 'InsightCategory',
                    'Insights', 'alembic_version'
                ]

                missing_tables = [t for t in expected_tables if t not in tables]

                if verbose:
                    print_info("Tablas encontradas:")
                    for table in sorted(tables):
                        marker = "✓" if table in expected_tables else "?"
                        print_info(f"  {marker} {table}")

                if missing_tables:
                    print_warning(f"Faltan {len(missing_tables)} tablas esperadas")
                    if verbose:
                        for table in missing_tables:
                            print_info(f"  ✗ {table}")
                    print_warning("Ejecuta: python scripts/init_database.py")
                else:
                    print_success("Todas las tablas esperadas están presentes")
            else:
                print_warning("Base de datos está vacía")
                print_warning("Ejecuta: python scripts/init_database.py")

        # 4. Verificar versión de migraciones
        if 'alembic_version' in tables:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.fetchone()
                if version:
                    print_success(f"Migración actual: {version[0]}")
                    results['migrations'] = True
                else:
                    print_warning("No se encontró versión de migración")
        else:
            print_warning("Tabla alembic_version no existe")

        # 5. Contar registros en tablas clave
        if verbose and results['tables']:
            print_info("\nConteo de registros:")
            key_tables = ['User', 'Bank', 'Transaction', 'Insights']
            with engine.connect() as conn:
                for table in key_tables:
                    if table in tables:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        print_info(f"  {table}: {count} registros")

        return True, results

    except Exception as e:
        print_error(f"Error conectando a MySQL: {str(e)}")
        print_info("\nVerifica:")
        print_info("  1. MySQL está corriendo: docker-compose ps")
        print_info("  2. Credenciales en .env son correctas")
        print_info("  3. Puerto 3306 no está bloqueado")
        return False, results


def check_rabbitmq_connection(config: Dict[str, str], verbose: bool = False) -> Tuple[bool, Dict]:
    """Verificar conexión a RabbitMQ"""
    print_section("Verificando RabbitMQ")

    results = {
        'amqp': False,
        'management': False,
        'queues': False
    }

    # 1. Verificar conexión AMQP
    try:
        import pika

        print_info(f"Conectando AMQP a: {config['RABBITMQ_HOST']}:{config['RABBITMQ_PORT']}")

        credentials = pika.PlainCredentials(
            config['RABBITMQ_USER'],
            config['RABBITMQ_PASSWORD']
        )

        parameters = pika.ConnectionParameters(
            host=config['RABBITMQ_HOST'],
            port=int(config['RABBITMQ_PORT']),
            credentials=credentials,
            connection_attempts=3,
            retry_delay=2,
            socket_timeout=5
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        print_success("Conexión AMQP a RabbitMQ exitosa")
        results['amqp'] = True

        # Verificar cola batch_processed
        try:
            method = channel.queue_declare(queue='batch_processed', passive=True)
            print_success(f"Cola 'batch_processed' existe ({method.method.message_count} mensajes)")
            results['queues'] = True
        except Exception:
            print_warning("Cola 'batch_processed' no existe (se creará al usar)")
            results['queues'] = True  # No es crítico

        connection.close()

    except ImportError:
        print_warning("pika no instalado (pip install pika)")
        print_info("Verificación AMQP omitida")
    except Exception as e:
        print_error(f"Error conectando AMQP: {str(e)}")
        print_info("\nVerifica:")
        print_info("  1. RabbitMQ está corriendo: docker-compose ps")
        print_info("  2. Credenciales en .env son correctas")
        print_info("  3. Puerto 5672 no está bloqueado")
        return False, results

    # 2. Verificar Management API
    try:
        import requests

        management_url = f"http://{config['RABBITMQ_HOST']}:{config['RABBITMQ_MANAGEMENT_PORT']}/api/overview"
        print_info(f"Verificando Management API: {management_url}")

        response = requests.get(
            management_url,
            auth=(config['RABBITMQ_USER'], config['RABBITMQ_PASSWORD']),
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Management API accesible")
            results['management'] = True

            if verbose:
                print_info(f"  RabbitMQ versión: {data.get('rabbitmq_version', 'unknown')}")
                print_info(f"  Erlang versión: {data.get('erlang_version', 'unknown')}")

                # Obtener información de colas
                queues_url = f"http://{config['RABBITMQ_HOST']}:{config['RABBITMQ_MANAGEMENT_PORT']}/api/queues"
                queues_response = requests.get(
                    queues_url,
                    auth=(config['RABBITMQ_USER'], config['RABBITMQ_PASSWORD']),
                    timeout=5
                )

                if queues_response.status_code == 200:
                    queues = queues_response.json()
                    if queues:
                        print_info(f"\nColas configuradas: {len(queues)}")
                        for queue in queues:
                            name = queue.get('name', 'unknown')
                            messages = queue.get('messages', 0)
                            print_info(f"  • {name}: {messages} mensajes")
                    else:
                        print_info("\nNo hay colas configuradas aún")

            print_info(f"\nManagement UI: http://{config['RABBITMQ_HOST']}:{config['RABBITMQ_MANAGEMENT_PORT']}")

        else:
            print_error(f"Management API retornó código {response.status_code}")

    except ImportError:
        print_warning("requests no instalado (pip install requests)")
        print_info("Verificación Management API omitida")
    except Exception as e:
        print_error(f"Error verificando Management API: {str(e)}")
        print_info(f"Management UI: http://{config['RABBITMQ_HOST']}:{config['RABBITMQ_MANAGEMENT_PORT']}")

    return results['amqp'] or results['management'], results


def check_redis_connection(config: Dict[str, str], verbose: bool = False) -> Tuple[bool, Dict]:
    """Verificar conexión a Redis"""
    print_section("Verificando Redis")

    results = {
        'connection': False,
        'ping': False,
        'info': False
    }

    try:
        import redis

        print_info(f"Conectando a: {config['REDIS_HOST']}:{config['REDIS_PORT']}")

        # Conectar a Redis
        redis_client = redis.Redis(
            host=config['REDIS_HOST'],
            port=int(config['REDIS_PORT']),
            password=config['REDIS_PASSWORD'],
            db=int(config['REDIS_DB']),
            decode_responses=True,
            socket_connect_timeout=5
        )

        # 1. Verificar conexión con PING
        response = redis_client.ping()
        if response:
            print_success("Conexión a Redis exitosa")
            results['connection'] = True
            results['ping'] = True

            # 2. Obtener información del servidor
            if verbose:
                info = redis_client.info()
                print_success(f"Redis versión: {info.get('redis_version', 'unknown')}")
                print_info(f"  Modo: {info.get('redis_mode', 'standalone')}")
                print_info(f"  Uptime: {info.get('uptime_in_days', 0)} días")
                print_info(f"  Clientes conectados: {info.get('connected_clients', 0)}")
                print_info(f"  Memoria usada: {info.get('used_memory_human', 'N/A')}")
                print_info(f"  Keys en DB {config['REDIS_DB']}: {redis_client.dbsize()}")
                results['info'] = True
            else:
                info = redis_client.info('server')
                print_success(f"Redis versión: {info.get('redis_version', 'unknown')}")
                results['info'] = True

            # 3. Verificar operaciones básicas
            try:
                test_key = '__flowlite_health_check__'
                redis_client.set(test_key, 'ok', ex=5)  # expira en 5 segundos
                value = redis_client.get(test_key)
                redis_client.delete(test_key)
                if value == 'ok':
                    print_success("Operaciones de lectura/escritura funcionan")
            except Exception as e:
                print_warning(f"Operaciones básicas fallaron: {e}")

        redis_client.close()

    except ImportError:
        print_warning("redis-py no instalado (pip install redis)")
        print_info("Verificación de Redis omitida")
        return False, results
    except redis.AuthenticationError:
        print_error("Error de autenticación en Redis")
        print_info("\nVerifica:")
        print_info(f"  1. Password en .env: REDIS_PASSWORD={config['REDIS_PASSWORD']}")
        print_info("  2. Redis está configurado con requirepass")
        return False, results
    except redis.ConnectionError as e:
        print_error(f"Error conectando a Redis: {str(e)}")
        print_info("\nVerifica:")
        print_info("  1. Redis está corriendo: docker-compose ps")
        print_info("  2. Puerto 6379 no está bloqueado")
        print_info("  3. Credenciales en .env son correctas")
        return False, results
    except Exception as e:
        print_error(f"Error inesperado con Redis: {str(e)}")
        return False, results

    return results['connection'], results


def print_summary(all_results: Dict):
    """Imprimir resumen final"""
    print_header("RESUMEN DE VERIFICACIÓN")

    # Contar checks exitosos
    total_checks = 0
    passed_checks = 0

    for service, checks in all_results.items():
        if isinstance(checks, dict):
            for check, result in checks.items():
                total_checks += 1
                if result:
                    passed_checks += 1

    # Calcular porcentaje
    if total_checks > 0:
        percentage = (passed_checks / total_checks) * 100
    else:
        percentage = 0

    # Imprimir resumen por servicio
    for service, checks in all_results.items():
        print_info(f"\n{service.upper()}:")
        if isinstance(checks, dict):
            for check, result in checks.items():
                status = f"{Colors.GREEN}✓{Colors.RESET}" if result else f"{Colors.RED}✗{Colors.RESET}"
                print_info(f"  {status} {check}")
        else:
            status = f"{Colors.GREEN}✓{Colors.RESET}" if checks else f"{Colors.RED}✗{Colors.RESET}"
            print_info(f"  {status} Disponible")

    # Estado general
    print_info(f"\n{Colors.BOLD}Estado General:{Colors.RESET}")
    print_info(f"  Checks pasados: {passed_checks}/{total_checks} ({percentage:.0f}%)")

    if percentage == 100:
        print_success("\n✓ Toda la infraestructura está funcionando correctamente")
        return True
    elif percentage >= 75:
        print_warning(f"\n⚠ Infraestructura parcialmente funcional ({percentage:.0f}%)")
        return False
    else:
        print_error(f"\n✗ Problemas críticos en la infraestructura ({percentage:.0f}%)")
        return False


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Verificar infraestructura de Flowlite'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada'
    )
    parser.add_argument(
        '--service', '-s',
        choices=['mysql', 'rabbitmq', 'redis', 'docker'],
        help='Verificar solo un servicio específico'
    )
    args = parser.parse_args()

    print_header("VERIFICACIÓN DE INFRAESTRUCTURA - FLOWLITE")

    # Cargar configuración
    config = load_environment()

    all_results = {}

    # Verificar Docker containers
    if not args.service or args.service == 'docker':
        docker_ok = check_docker_containers()
        all_results['docker'] = docker_ok

        if not docker_ok:
            print_error("\n✗ Contenedores Docker no están disponibles")
            print_info("\nInicia la infraestructura:")
            print_info("  cd InfrastructureService")
            print_info("  docker-compose up -d")
            sys.exit(1)

    # Verificar MySQL
    if not args.service or args.service == 'mysql':
        mysql_ok, mysql_results = check_mysql_connection(config, args.verbose)
        all_results['mysql'] = mysql_results

    # Verificar RabbitMQ
    if not args.service or args.service == 'rabbitmq':
        rabbitmq_ok, rabbitmq_results = check_rabbitmq_connection(config, args.verbose)
        all_results['rabbitmq'] = rabbitmq_results

    # Verificar Redis
    if not args.service or args.service == 'redis':
        redis_ok, redis_results = check_redis_connection(config, args.verbose)
        all_results['redis'] = redis_results

    # Imprimir resumen
    all_ok = print_summary(all_results)

    # Próximos pasos
    if all_ok:
        print_info("\n" + "="*60)
        print_info("PRÓXIMOS PASOS:")
        print_info("="*60)
        print_info("\n1. Iniciar servicios:")
        print_info("   - IdentityService: uvicorn src.main:app --port 8000")
        print_info("   - UploadService: uvicorn src.main:app --port 8001")
        print_info("   - InsightService: python main.py")
        print_info("\n2. Poblar datos de prueba (opcional):")
        print_info("   python scripts/seed_database.py")
        print_info("")
        sys.exit(0)
    else:
        print_info("\n" + "="*60)
        print_info("ACCIONES REQUERIDAS:")
        print_info("="*60)
        print_info("\n1. Revisa los errores arriba")
        print_info("2. Ejecuta los comandos sugeridos")
        print_info("3. Vuelve a verificar: python scripts/check_infrastructure.py")
        print_info("")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nVerificación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
