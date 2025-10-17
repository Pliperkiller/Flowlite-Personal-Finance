"""
Script para inicializar datos básicos en la base de datos
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.models import BancoModel, CategoriaModel, UsuarioModel
import os
from passlib.context import CryptContext

# Configuración para hashear passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def init_data():
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://user:password@localhost:3306/transactions_db"
    )

    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Crear usuarios de prueba
        usuarios = [
            UsuarioModel(
                email="test1@example.com",
                nombre="Juan",
                apellido="Pérez",
                password_hash=hash_password("password123"),
                activo=True
            ),
            UsuarioModel(
                email="test2@example.com",
                nombre="María",
                apellido="González",
                password_hash=hash_password("password123"),
                activo=True
            ),
            UsuarioModel(
                email="test3@example.com",
                nombre="Carlos",
                apellido="Rodríguez",
                password_hash=hash_password("password123"),
                activo=True
            ),
            UsuarioModel(
                email="admin@example.com",
                nombre="Admin",
                apellido="Sistema",
                password_hash=hash_password("admin123"),
                activo=True
            ),
        ]

        # Crear bancos
        bancos = [
            BancoModel(nombre="Bancolombia", codigo="BANCOLOMBIA"),
            # Agregar más bancos según sea necesario
        ]

        # Crear categorías iniciales
        categorias = [
            CategoriaModel(nombre="Otro", descripcion="Categoría por defecto"),
            CategoriaModel(nombre="Alimentación", descripcion="Gastos en comida"),
            CategoriaModel(nombre="Transporte", descripcion="Gastos de transporte"),
            CategoriaModel(nombre="Servicios", descripcion="Pago de servicios"),
            CategoriaModel(nombre="Entretenimiento", descripcion="Gastos de ocio"),
            CategoriaModel(nombre="Salud", descripcion="Gastos médicos"),
            CategoriaModel(nombre="Educación", descripcion="Gastos educativos"),
            CategoriaModel(nombre="Ingresos", descripcion="Ingresos varios"),
        ]

        session.add_all(usuarios)
        session.add_all(bancos)
        session.add_all(categorias)
        await session.commit()

        print("\n" + "="*60)
        print("Datos iniciales creados exitosamente")
        print("="*60)
        print("\nUsuarios de prueba creados:")
        print("-" * 60)
        for i, usuario in enumerate(usuarios, 1):
            print(f"{i}. Email: {usuario.email}")
            print(f"   Nombre: {usuario.nombre} {usuario.apellido}")
            print(f"   Password: {'admin123' if 'admin' in usuario.email else 'password123'}")
            print(f"   ID en DB: {i}")
            print()
        print("="*60)


if __name__ == "__main__":
    asyncio.run(init_data())
