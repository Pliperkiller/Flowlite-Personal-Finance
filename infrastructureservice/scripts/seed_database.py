#!/usr/bin/env python3
"""
Script de Población de Base de Datos - Flowlite Personal Finance

Este script puebla la base de datos con datos de prueba para los tres servicios:
- IdentityService: Usuarios, roles, información de usuario
- UploadService: Bancos, categorías de transacciones, lotes y transacciones
- InsightService: Categorías de insights e insights de ejemplo

Uso:
    python scripts/seed_database.py

    # Limpiar y repoblar
    python scripts/seed_database.py --clean

Prerequisitos:
    - Base de datos inicializada (python scripts/init_database.py)
    - MySQL corriendo
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import argparse

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Importar modelos
from models import (
    Base, User, Role, UserInfo, Bank, TransactionCategory,
    TransactionBatch, Transaction, FileUploadHistory, InsightCategory, Insights
)

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

    database_url = os.getenv('DATABASE_URL',
                            "mysql+pymysql://flowlite_user:flowlite_password@localhost:3306/flowlite_db")

    # Convertir aiomysql a pymysql si es necesario (para scripts síncronos)
    if 'aiomysql' in database_url:
        database_url = database_url.replace('aiomysql', 'pymysql')

    return database_url


def create_session(database_url):
    """Crear sesión de base de datos"""
    engine = create_engine(database_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def clean_database(session, engine):
    """Limpiar todos los datos (CUIDADO: elimina todo)"""
    logger.warning("LIMPIANDO BASE DE DATOS - Se eliminarán todos los datos")

    try:
        # Desactivar foreign key checks temporalmente
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            conn.commit()

        # Eliminar datos en orden inverso de dependencias
        session.query(Insights).delete()
        session.query(Transaction).delete()
        session.query(FileUploadHistory).delete()
        session.query(TransactionBatch).delete()
        session.query(UserInfo).delete()
        session.query(User).delete()
        session.query(Role).delete()
        session.query(Bank).delete()
        session.query(TransactionCategory).delete()
        session.query(InsightCategory).delete()

        session.commit()

        # Reactivar foreign key checks
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            conn.commit()

        logger.info("✓ Base de datos limpiada")
    except Exception as e:
        session.rollback()
        logger.error(f"Error limpiando base de datos: {e}")
        raise


def seed_roles(session):
    """Poblar roles (IdentityService)"""
    logger.info("\n📋 Poblando Roles...")

    roles_data = [
        {"id_role": "role-001-admin", "role_name": "ADMIN"},
        {"id_role": "role-002-user", "role_name": "USER"},
        {"id_role": "role-003-premium", "role_name": "PREMIUM_USER"},
    ]

    roles = []
    for data in roles_data:
        role = Role(**data)
        roles.append(role)
        logger.info(f"  + {data['role_name']}")

    session.add_all(roles)
    session.commit()
    logger.info(f"✓ {len(roles)} roles creados")
    return roles


def seed_users(session):
    """Poblar usuarios (IdentityService)"""
    logger.info("\n👥 Poblando Usuarios...")

    # Nota: En producción, las contraseñas deben estar hasheadas
    # Aquí usamos texto plano solo para testing
    users_data = [
        {
            "id_user": "user-001-juan-perez",
            "username": "juan.perez",
            "email": "juan.perez@example.com",
            "password": "password123",  # En producción: hash
            "role": "USER",
            "active": True
        },
        {
            "id_user": "user-002-maria-lopez",
            "username": "maria.lopez",
            "email": "maria.lopez@example.com",
            "password": "password123",
            "role": "PREMIUM_USER",
            "active": True
        },
        {
            "id_user": "user-003-admin",
            "username": "admin",
            "email": "admin@flowlite.com",
            "password": "admin123",
            "role": "ADMIN",
            "active": True
        },
        {
            "id_user": "user-004-pedro-gomez",
            "username": "pedro.gomez",
            "email": "pedro.gomez@example.com",
            "password": "password123",
            "role": "USER",
            "active": False  # Usuario inactivo para testing
        }
    ]

    users = []
    for data in users_data:
        user = User(**data)
        users.append(user)
        status = "✓" if data["active"] else "✗"
        logger.info(f"  {status} {data['email']} ({data['role']})")

    session.add_all(users)
    session.commit()
    logger.info(f"✓ {len(users)} usuarios creados")
    return users


def seed_user_info(session, users):
    """Poblar información adicional de usuarios (IdentityService)"""
    logger.info("\n📝 Poblando Información de Usuarios...")

    user_info_data = [
        {
            "id_user": "user-001-juan-perez",
            "primerNombre": "Juan",
            "segundoNombre": "Carlos",
            "primerApellido": "Pérez",
            "segundoApellido": "Martínez",
            "telefono": "+57 300 123 4567",
            "direccion": "Calle 123 #45-67",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "pais": "Colombia",
            "numeroIdentificacion": "1234567890",
            "tipoIdentificacion": "CC"
        },
        {
            "id_user": "user-002-maria-lopez",
            "primerNombre": "María",
            "segundoNombre": "Fernanda",
            "primerApellido": "López",
            "segundoApellido": "García",
            "telefono": "+57 310 987 6543",
            "direccion": "Carrera 45 #12-34",
            "ciudad": "Medellín",
            "departamento": "Antioquia",
            "pais": "Colombia",
            "numeroIdentificacion": "9876543210",
            "tipoIdentificacion": "CC"
        },
        {
            "id_user": "user-003-admin",
            "primerNombre": "Admin",
            "primerApellido": "Flowlite",
            "telefono": "+57 320 000 0000",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "numeroIdentificacion": "0000000000",
            "tipoIdentificacion": "NIT"
        }
    ]

    user_infos = []
    for data in user_info_data:
        user_info = UserInfo(**data)
        user_infos.append(user_info)
        logger.info(f"  + {data.get('primerNombre')} {data.get('primerApellido')}")

    session.add_all(user_infos)
    session.commit()
    logger.info(f"✓ {len(user_infos)} registros de información creados")


def seed_banks(session):
    """Poblar bancos (UploadService)"""
    logger.info("\n🏦 Poblando Bancos...")

    banks_data = [
        {"id_bank": "bank-001-bancolombia", "bank_name": "Bancolombia"},
        {"id_bank": "bank-002-davivienda", "bank_name": "Davivienda"},
        {"id_bank": "bank-003-bogota", "bank_name": "Banco de Bogotá"},
        {"id_bank": "bank-004-bbva", "bank_name": "BBVA Colombia"},
        {"id_bank": "bank-005-nequi", "bank_name": "Nequi"},
    ]

    banks = []
    for data in banks_data:
        bank = Bank(**data)
        banks.append(bank)
        logger.info(f"  + {data['bank_name']}")

    session.add_all(banks)
    session.commit()
    logger.info(f"✓ {len(banks)} bancos creados")
    return banks


def seed_transaction_categories(session):
    """
    Poblar categorías de transacciones (UploadService)

    IMPORTANTE: Estas categorías deben coincidir EXACTAMENTE con las
    categorías que predice el modelo ML (Logistic Regression + TF-IDF).
    Los nombres incluyen underscores y deben mantenerse tal cual.
    """
    logger.info("\n📂 Poblando Categorías de Transacciones (ML Model)...")

    categories_data = [
        {
            "id_category": "cat-001-retiros-efectivo",
            "description": "Retiros_Efectivo"
        },
        {
            "id_category": "cat-002-alimentacion-restaurantes",
            "description": "Alimentacion_Restaurantes"
        },
        {
            "id_category": "cat-003-supermercados-hogar",
            "description": "Supermercados_Hogar"
        },
        {
            "id_category": "cat-004-combustible-transporte",
            "description": "Combustible_Transporte"
        },
        {
            "id_category": "cat-005-entretenimiento",
            "description": "Entretenimiento"
        },
        {
            "id_category": "cat-006-servicios-publicos",
            "description": "Servicios_Publicos"
        },
        {
            "id_category": "cat-007-vivienda-arriendo",
            "description": "Vivienda_Arriendo"
        },
        {
            "id_category": "cat-008-salud-cuidado-personal",
            "description": "Salud_Cuidado_Personal"
        },
        {
            "id_category": "cat-009-educacion",
            "description": "Educacion"
        },
        {
            "id_category": "cat-010-obligaciones-financieras",
            "description": "Obligaciones_Financieras"
        },
        {
            "id_category": "cat-011-transferencias-ingresos",
            "description": "Transferencias_Ingresos"
        },
    ]

    categories = []
    for data in categories_data:
        category = TransactionCategory(**data)
        categories.append(category)
        logger.info(f"  + {data['description']}")

    session.add_all(categories)
    session.commit()
    logger.info(f"✓ {len(categories)} categorías ML creadas")
    return categories


def seed_transaction_batches(session):
    """Poblar lotes de transacciones (UploadService)"""
    logger.info("\n📦 Poblando Lotes de Transacciones...")

    batches_data = [
        {
            "id_batch": "batch-001-completed",
            "process_status": "completed",
            "start_date": datetime.now() - timedelta(days=7),
            "end_date": datetime.now() - timedelta(days=7, hours=-1),
            "batch_size": 50
        },
        {
            "id_batch": "batch-002-completed",
            "process_status": "completed",
            "start_date": datetime.now() - timedelta(days=3),
            "end_date": datetime.now() - timedelta(days=3, hours=-2),
            "batch_size": 75
        },
        {
            "id_batch": "batch-003-processing",
            "process_status": "processing",
            "start_date": datetime.now() - timedelta(hours=2),
            "end_date": None,
            "batch_size": 30
        }
    ]

    batches = []
    for data in batches_data:
        batch = TransactionBatch(**data)
        batches.append(batch)
        logger.info(f"  + Lote {data['id_batch']} - {data['process_status']}")

    session.add_all(batches)
    session.commit()
    logger.info(f"✓ {len(batches)} lotes creados")
    return batches


def seed_transactions(session):
    """
    Poblar transacciones (UploadService)

    Las categorías ahora coinciden con las predicciones del modelo ML.
    """
    logger.info("\n💳 Poblando Transacciones...")

    # Transacciones de Juan Pérez
    transactions_juan = [
        # Mes pasado - Gastos
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-003-supermercados-hogar",  # Supermercados_Hogar
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-001-completed",
            "transaction_name": "COMPRA EXITO",
            "value": Decimal("-85000.00"),
            "transaction_date": datetime.now() - timedelta(days=25),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-004-combustible-transporte",  # Combustible_Transporte
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-001-completed",
            "transaction_name": "UBER",
            "value": Decimal("-25000.00"),
            "transaction_date": datetime.now() - timedelta(days=24),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-006-servicios-publicos",  # Servicios_Publicos
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-001-completed",
            "transaction_name": "PAGO ENERGIA EPM",
            "value": Decimal("-150000.00"),
            "transaction_date": datetime.now() - timedelta(days=23),
            "transaction_type": "expense"
        },
        # Mes pasado - Ingreso
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-011-transferencias-ingresos",  # Transferencias_Ingresos
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-001-completed",
            "transaction_name": "PAGO NOMINA EMPRESA ABC",
            "value": Decimal("3500000.00"),
            "transaction_date": datetime.now() - timedelta(days=30),
            "transaction_type": "income"
        },
        # Esta semana
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-005-entretenimiento",  # Entretenimiento
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-002-completed",
            "transaction_name": "NETFLIX",
            "value": Decimal("-45000.00"),
            "transaction_date": datetime.now() - timedelta(days=2),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-002-alimentacion-restaurantes",  # Alimentacion_Restaurantes
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-002-completed",
            "transaction_name": "RESTAURANTE LA ESTANCIA",
            "value": Decimal("-120000.00"),
            "transaction_date": datetime.now() - timedelta(days=1),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "cat-001-retiros-efectivo",  # Retiros_Efectivo
            "id_bank": "bank-001-bancolombia",
            "id_batch": "batch-002-completed",
            "transaction_name": "RETIRO CAJERO BANCOLOMBIA",
            "value": Decimal("-200000.00"),
            "transaction_date": datetime.now() - timedelta(days=3),
            "transaction_type": "expense"
        }
    ]

    # Transacciones de María López
    transactions_maria = [
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-011-transferencias-ingresos",  # Transferencias_Ingresos
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-001-completed",
            "transaction_name": "TRANSFERENCIA FREELANCE",
            "value": Decimal("2800000.00"),
            "transaction_date": datetime.now() - timedelta(days=28),
            "transaction_type": "income"
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-007-vivienda-arriendo",  # Vivienda_Arriendo
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-001-completed",
            "transaction_name": "PAGO ARRIENDO",
            "value": Decimal("-1200000.00"),
            "transaction_date": datetime.now() - timedelta(days=27),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-009-educacion",  # Educacion
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-002-completed",
            "transaction_name": "CURSO ONLINE UDEMY",
            "value": Decimal("-89000.00"),
            "transaction_date": datetime.now() - timedelta(days=5),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-003-supermercados-hogar",  # Supermercados_Hogar
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-002-completed",
            "transaction_name": "COMPRA DOLLARCITY",
            "value": Decimal("-45000.00"),
            "transaction_date": datetime.now() - timedelta(days=4),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-008-salud-cuidado-personal",  # Salud_Cuidado_Personal
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-002-completed",
            "transaction_name": "FARMACIA DROGUERIA COLSUBSIDIO",
            "value": Decimal("-68000.00"),
            "transaction_date": datetime.now() - timedelta(days=3),
            "transaction_type": "expense"
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "cat-010-obligaciones-financieras",  # Obligaciones_Financieras
            "id_bank": "bank-002-davivienda",
            "id_batch": "batch-002-completed",
            "transaction_name": "PAGO TARJETA DE CREDITO",
            "value": Decimal("-450000.00"),
            "transaction_date": datetime.now() - timedelta(days=2),
            "transaction_type": "expense"
        }
    ]

    all_transactions = transactions_juan + transactions_maria

    transactions = []
    for data in all_transactions:
        transaction = Transaction(**data)
        transactions.append(transaction)

    session.add_all(transactions)
    session.commit()

    logger.info(f"  + {len(transactions_juan)} transacciones para Juan Pérez")
    logger.info(f"  + {len(transactions_maria)} transacciones para María López")
    logger.info(f"✓ {len(transactions)} transacciones creadas")
    return transactions


def seed_insight_categories(session):
    """Poblar categorías de insights (InsightService)"""
    logger.info("\n💡 Poblando Categorías de Insights...")

    categories_data = [
        {"id_category": "ins-cat-001-ahorro", "description": "Ahorro"},
        {"id_category": "ins-cat-002-presupuesto", "description": "Presupuesto"},
        {"id_category": "ins-cat-003-gastos", "description": "Análisis de Gastos"},
        {"id_category": "ins-cat-004-ingresos", "description": "Análisis de Ingresos"},
        {"id_category": "ins-cat-005-tendencias", "description": "Tendencias"},
        {"id_category": "ins-cat-006-alertas", "description": "Alertas"},
    ]

    categories = []
    for data in categories_data:
        category = InsightCategory(**data)
        categories.append(category)
        logger.info(f"  + {data['description']}")

    session.add_all(categories)
    session.commit()
    logger.info(f"✓ {len(categories)} categorías de insights creadas")
    return categories


def seed_insights(session):
    """Poblar insights de ejemplo (InsightService)"""
    logger.info("\n🔍 Poblando Insights...")

    insights_data = [
        {
            "id_user": "user-001-juan-perez",
            "id_category": "ins-cat-003-gastos",
            "title": "Alto gasto en alimentación este mes",
            "text": "Has gastado $205,000 en alimentación este mes, un 30% más que el mes anterior. Considera reducir las comidas fuera de casa para ahorrar.",
            "relevance": 8,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "ins-cat-001-ahorro",
            "title": "Oportunidad de ahorro en transporte",
            "text": "Has gastado $25,000 en Uber este mes. Considera usar transporte público o compartir viajes para reducir estos gastos en un 50%.",
            "relevance": 7,
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "id_user": "user-001-juan-perez",
            "id_category": "ins-cat-002-presupuesto",
            "title": "Presupuesto mensual bien equilibrado",
            "text": "Tus gastos representan el 15% de tus ingresos mensuales. ¡Excelente trabajo manteniendo un presupuesto saludable!",
            "relevance": 9,
            "created_at": datetime.now() - timedelta(hours=12)
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "ins-cat-003-gastos",
            "title": "Gasto considerable en vivienda",
            "text": "El arriendo representa el 43% de tus ingresos. Se recomienda que no supere el 30% para mantener finanzas saludables.",
            "relevance": 9,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "id_user": "user-002-maria-lopez",
            "id_category": "ins-cat-005-tendencias",
            "title": "Inversión en educación detectada",
            "text": "Has invertido $89,000 en educación este mes. Esta es una excelente inversión en tu desarrollo profesional.",
            "relevance": 6,
            "created_at": datetime.now() - timedelta(days=1)
        }
    ]

    insights = []
    for data in insights_data:
        insight = Insights(**data)
        insights.append(insight)

    session.add_all(insights)
    session.commit()

    logger.info(f"  + {len([i for i in insights_data if i['id_user'] == 'user-001-juan-perez'])} insights para Juan Pérez")
    logger.info(f"  + {len([i for i in insights_data if i['id_user'] == 'user-002-maria-lopez'])} insights para María López")
    logger.info(f"✓ {len(insights)} insights creados")


def print_summary(session):
    """Imprimir resumen de datos creados"""
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE DATOS CREADOS")
    logger.info("="*60)

    counts = {
        "Roles": session.query(Role).count(),
        "Usuarios": session.query(User).count(),
        "Información de Usuarios": session.query(UserInfo).count(),
        "Bancos": session.query(Bank).count(),
        "Categorías de Transacciones": session.query(TransactionCategory).count(),
        "Lotes de Transacciones": session.query(TransactionBatch).count(),
        "Transacciones": session.query(Transaction).count(),
        "Historial de Archivos": session.query(FileUploadHistory).count(),
        "Categorías de Insights": session.query(InsightCategory).count(),
        "Insights": session.query(Insights).count(),
    }

    for entity, count in counts.items():
        logger.info(f"  {entity}: {count}")

    logger.info("\n" + "="*60)
    logger.info("USUARIOS DE PRUEBA")
    logger.info("="*60)

    users = session.query(User).filter(User.active == True).all()
    for user in users:
        logger.info(f"\n  Email: {user.email}")
        logger.info(f"  Username: {user.username}")
        logger.info(f"  Password: password123 (plaintext para testing)")
        logger.info(f"  Role: {user.role}")
        logger.info(f"  ID: {user.id_user}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Poblar base de datos con datos de prueba')
    parser.add_argument('--clean', action='store_true',
                       help='Limpiar base de datos antes de poblar')
    args = parser.parse_args()

    logger.info("="*60)
    logger.info("POBLACIÓN DE BASE DE DATOS - FLOWLITE")
    logger.info("="*60)

    # Mostrar versión del seed si está disponible (cuando se ejecuta en Docker)
    seed_version = os.getenv('SEED_VERSION', 'unknown')
    if seed_version != 'unknown':
        logger.info(f"Seed Version: {seed_version}")
        logger.info("="*60)

    # 1. Cargar configuración
    database_url = load_environment()

    # 2. Crear sesión
    try:
        session, engine = create_session(database_url)
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        logger.info("\nVerifica que:")
        logger.info("  1. MySQL esté corriendo: docker-compose ps")
        logger.info("  2. La base de datos esté inicializada: python scripts/init_database.py")
        sys.exit(1)

    try:
        # 3. Limpiar si se especificó
        if args.clean:
            clean_database(session, engine)

        # 4. Poblar datos
        logger.info("\n" + "="*60)
        logger.info("INICIANDO POBLACIÓN DE DATOS")
        logger.info("="*60)

        seed_roles(session)
        users = seed_users(session)
        seed_user_info(session, users)
        banks = seed_banks(session)
        categories = seed_transaction_categories(session)
        batches = seed_transaction_batches(session)
        transactions = seed_transactions(session)
        insight_categories = seed_insight_categories(session)
        seed_insights(session)

        # 5. Mostrar resumen
        print_summary(session)

        # 6. Validar que las categorías ML fueron creadas correctamente
        logger.info("\n" + "="*60)
        logger.info("VALIDACIÓN DE CATEGORÍAS ML")
        logger.info("="*60)

        category_count = session.query(TransactionCategory).count()
        expected_count = 11

        if category_count == expected_count:
            logger.info(f"✓ Número de categorías correcto: {category_count}/{expected_count}")

            # Verificar que tengan el formato ML (con underscores)
            ml_categories = session.query(TransactionCategory).filter(
                TransactionCategory.description.like('%\_%')
            ).count()

            if ml_categories >= 10:
                logger.info(f"✓ Categorías con formato ML detectadas: {ml_categories}")
            else:
                logger.warning(f"⚠ Solo {ml_categories} categorías tienen formato ML (se esperaban ≥10)")
                logger.warning("  Las categorías pueden no ser compatibles con el clasificador ML")
        else:
            logger.error(f"✗ Número de categorías incorrecto: {category_count}/{expected_count}")
            logger.error("  Por favor, revisa el archivo seed_database.py")

        logger.info("\n" + "="*60)
        logger.info("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        logger.info("="*60)
        logger.info("\nPróximos pasos:")
        logger.info("  1. Iniciar IdentityService: uvicorn src.main:app --port 8000")
        logger.info("  2. Iniciar UploadService: uvicorn src.main:app --port 8001")
        logger.info("  3. Iniciar InsightService: python main.py")
        logger.info("\nPuedes hacer login con:")
        logger.info("  Email: juan.perez@example.com")
        logger.info("  Password: password123")
        logger.info("\n")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error poblando base de datos: {e}", exc_info=True)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nProceso interrumpido por el usuario")
        sys.exit(0)
