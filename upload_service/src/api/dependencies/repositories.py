from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from ...infrastructure.database import get_database, get_session_factory
from ...infrastructure.repositories import (
    MySQLTransaccionRepository,
    MySQLBancoRepository,
    MySQLCategoriaRepository,
    MySQLLoteTransaccionRepository,
    MySQLUsuarioRepository,
)


async def get_transaccion_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLTransaccionRepository:
    return MySQLTransaccionRepository(db)


async def get_banco_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLBancoRepository:
    return MySQLBancoRepository(db)


async def get_categoria_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLCategoriaRepository:
    return MySQLCategoriaRepository(db)


async def get_lote_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLLoteTransaccionRepository:
    return MySQLLoteTransaccionRepository(db)


async def get_usuario_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLUsuarioRepository:
    return MySQLUsuarioRepository(db)


def get_db_session_factory() -> sessionmaker:
    """
    Dependency para obtener el session factory.
    Útil para tareas background que necesitan crear sus propias sesiones.
    """
    return get_session_factory()
