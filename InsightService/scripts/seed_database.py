#!/usr/bin/env python3
"""
Seed script to populate database with test data
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import random

from src.infrastructure.config.settings import get_settings
from src.infrastructure.config.logging_config import setup_logging
from src.infrastructure.config.database import DatabaseConfig
from src.infrastructure.database.models import (
    UserModel,
    TransactionCategoryModel,
    BankModel,
    TransactionBatchModel,
    TransactionModel,
    InsightCategoryModel
)

logger = logging.getLogger(__name__)


def seed_database():
    """Populate database with test data"""
    
    settings = get_settings()
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("🌱 Seeding database with test data")
    logger.info("=" * 60)
    
    db_config = DatabaseConfig(database_url=settings.database_url)
    
    with db_config.get_session() as session:
        
        # 1. Create test user
        logger.info("Creating test user...")
        user_id = uuid4()
        user = UserModel(
            id_user=user_id,
            username="test_user",
            email="test@example.com",
            password="hashed_password",
            role="user",
            active=True
        )
        session.add(user)
        
        # 2. Create transaction categories
        logger.info("Creating transaction categories...")
        categories = {
            "Restaurantes": TransactionCategoryModel(
                id_category=uuid4(),
                description="Restaurantes"
            ),
            "Transporte": TransactionCategoryModel(
                id_category=uuid4(),
                description="Transporte"
            ),
            "Entretenimiento": TransactionCategoryModel(
                id_category=uuid4(),
                description="Entretenimiento"
            ),
            "Supermercado": TransactionCategoryModel(
                id_category=uuid4(),
                description="Supermercado"
            ),
            "Salud": TransactionCategoryModel(
                id_category=uuid4(),
                description="Salud"
            ),
            "Salario": TransactionCategoryModel(
                id_category=uuid4(),
                description="Salario"
            ),
            "Servicios": TransactionCategoryModel(
                id_category=uuid4(),
                description="Servicios Públicos"
            )
        }
        
        for category in categories.values():
            session.add(category)
        
        # 3. Create insight categories
        logger.info("Creating insight categories...")
        insight_categories = {
            "savings": InsightCategoryModel(
                id_category=uuid4(),
                description="Ahorro"
            ),
            "spending": InsightCategoryModel(
                id_category=uuid4(),
                description="Gastos"
            ),
            "investment": InsightCategoryModel(
                id_category=uuid4(),
                description="Inversión"
            ),
            "debt": InsightCategoryModel(
                id_category=uuid4(),
                description="Deuda"
            ),
            "budget": InsightCategoryModel(
                id_category=uuid4(),
                description="Presupuesto"
            )
        }
        
        for category in insight_categories.values():
            session.add(category)
        
        # 4. Create bank
        logger.info("Creating test bank...")
        bank = BankModel(
            id_bank=uuid4(),
            bank_name="Banco de Prueba"
        )
        session.add(bank)
        
        # 5. Create transaction batch
        logger.info("Creating transaction batch...")
        batch_id = uuid4()
        batch = TransactionBatchModel(
            id_batch=batch_id,
            process_status="Processed",
            start_date=datetime.utcnow() - timedelta(hours=1),
            end_date=datetime.utcnow(),
            batch_size=0  # Will be updated
        )
        session.add(batch)
        
        # 6. Create transactions
        logger.info("Creating test transactions...")
        
        transactions_data = [
            # Income
            ("Salario", "Salario mensual", 5000000, "income", 1),
            
            # Expenses - Restaurants (high spending)
            ("Restaurantes", "Almuerzo McDonald's", 25000, "expense", 8),
            ("Restaurantes", "Cena restaurante", 80000, "expense", 4),
            ("Restaurantes", "Domicilio pizza", 35000, "expense", 6),
            
            # Transportation
            ("Transporte", "Uber al trabajo", 15000, "expense", 20),
            ("Transporte", "Gasolina", 120000, "expense", 4),
            
            # Entertainment
            ("Entretenimiento", "Netflix", 45000, "expense", 1),
            ("Entretenimiento", "Cine", 35000, "expense", 3),
            ("Entretenimiento", "Bar", 80000, "expense", 4),
            
            # Groceries
            ("Supermercado", "Mercado semanal", 250000, "expense", 4),
            ("Supermercado", "Compras menores", 30000, "expense", 8),
            
            # Health
            ("Salud", "Farmacia", 60000, "expense", 2),
            ("Salud", "Consulta médica", 120000, "expense", 1),
            
            # Utilities
            ("Servicios", "Luz", 180000, "expense", 1),
            ("Servicios", "Agua", 80000, "expense", 1),
            ("Servicios", "Internet", 90000, "expense", 1),
        ]
        
        transaction_count = 0
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for cat_name, trans_name, amount, trans_type, count in transactions_data:
            category = categories[cat_name]
            
            for i in range(count):
                transaction = TransactionModel(
                    id_transaction=uuid4(),
                    id_user=user_id,
                    id_category=category.id_category,
                    id_bank=bank.id_bank,
                    id_batch=batch_id,
                    transaction_name=trans_name,
                    value=amount + random.randint(-5000, 5000),  # Add some variation
                    transaction_date=base_date + timedelta(days=random.randint(0, 29)),
                    transaction_type=trans_type
                )
                session.add(transaction)
                transaction_count += 1
        
        # Update batch size
        batch.batch_size = transaction_count
        
        session.commit()
        
        logger.info("=" * 60)
        logger.info("Database seeded successfully!")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Batch ID: {batch_id}")
        logger.info(f"   Transactions created: {transaction_count}")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Test the service with:")
        logger.info(f'   python scripts/send_test_message.py {user_id} {batch_id}')
        logger.info("=" * 60)
        
        return user_id, batch_id


if __name__ == "__main__":
    seed_database()
