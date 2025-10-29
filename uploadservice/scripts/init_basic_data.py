"""
Script para inicializar datos básicos en la base de datos compartida.

Este script crea:
- Bancos soportados
- Categorías de transacciones

NOTA: Los usuarios NO se crean aquí. Los usuarios son gestionados por el IdentityService.
"""
import asyncio
import sys
import os
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import BankModel, CategoryModel


async def init_basic_data():
    """Initialize banks and categories in the database"""

    # Get database URL from environment
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://root:root@localhost:3306/flowlite_db"
    )

    print(f"\nConnecting to database: {DATABASE_URL.split('@')[1]}")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Check if data already exists
            from sqlalchemy import select

            result = await session.execute(select(BankModel))
            existing_banks = result.scalars().all()

            if existing_banks:
                print(f"\n⚠️  Found {len(existing_banks)} existing banks.")
                overwrite = input("Do you want to add more data? (y/n): ")
                if overwrite.lower() != 'y':
                    print("Cancelled.")
                    return

            # Create banks
            banks = [
                BankModel(
                    id_bank=str(uuid4()),
                    bank_name="Bancolombia"
                ),
                BankModel(
                    id_bank=str(uuid4()),
                    bank_name="Davivienda"
                ),
                BankModel(
                    id_bank=str(uuid4()),
                    bank_name="Banco de Bogotá"
                ),
                # Add more banks as needed
            ]

            # Create initial categories
            categories = [
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Otros"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Alimentación"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Transporte"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Servicios"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Entretenimiento"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Salud"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Educación"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Ingresos"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Vivienda"
                ),
                CategoryModel(
                    id_category=str(uuid4()),
                    description="Ropa y Accesorios"
                ),
            ]

            session.add_all(banks)
            session.add_all(categories)
            await session.commit()

            print("\n" + "="*70)
            print("✅ DATOS BÁSICOS CREADOS EXITOSAMENTE")
            print("="*70)

            print("\n📊 Bancos creados:")
            print("-" * 70)
            for i, bank in enumerate(banks, 1):
                print(f"{i}. {bank.bank_name}")
                print(f"   ID: {bank.id_bank}")

            print("\n📁 Categorías creadas:")
            print("-" * 70)
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category.description}")
                print(f"   ID: {category.id_category}")

            print("\n" + "="*70)
            print("ℹ️  NOTA IMPORTANTE:")
            print("="*70)
            print("Los USUARIOS no se crean aquí.")
            print("Los usuarios son gestionados por el IdentityService.")
            print("Para crear usuarios, usa el IdentityService en:")
            print("  POST http://localhost:8000/auth/register")
            print("="*70 + "\n")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 INICIALIZACIÓN DE DATOS BÁSICOS - UPLOAD SERVICE")
    print("="*70)

    asyncio.run(init_basic_data())
