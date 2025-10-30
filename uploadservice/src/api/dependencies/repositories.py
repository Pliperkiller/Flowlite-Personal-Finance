from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from ...infrastructure.database import get_database, get_session_factory
from ...infrastructure.repositories import (
    MySQLTransactionRepository,
    MySQLBankRepository,
    MySQLCategoryRepository,
    MySQLTransactionBatchRepository,
    MySQLUserRepository,
)


async def get_transaction_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLTransactionRepository:
    """
    Dependency for getting the transaction repository.

    Args:
        db: Database session

    Returns:
        MySQLTransactionRepository: Transaction repository instance
    """
    return MySQLTransactionRepository(db)


async def get_bank_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLBankRepository:
    """
    Dependency for getting the bank repository.

    Args:
        db: Database session

    Returns:
        MySQLBankRepository: Bank repository instance
    """
    return MySQLBankRepository(db)


async def get_category_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLCategoryRepository:
    """
    Dependency for getting the category repository.

    Args:
        db: Database session

    Returns:
        MySQLCategoryRepository: Category repository instance
    """
    return MySQLCategoryRepository(db)


async def get_batch_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLTransactionBatchRepository:
    """
    Dependency for getting the transaction batch repository.

    Args:
        db: Database session

    Returns:
        MySQLTransactionBatchRepository: Transaction batch repository instance
    """
    return MySQLTransactionBatchRepository(db)


async def get_user_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLUserRepository:
    """
    Dependency for getting the user repository.

    Args:
        db: Database session

    Returns:
        MySQLUserRepository: User repository instance
    """
    return MySQLUserRepository(db)


def get_db_session_factory() -> sessionmaker:
    """
    Dependency for getting the session factory.
    Useful for background tasks that need to create their own sessions.

    Returns:
        sessionmaker: Database session factory
    """
    return get_session_factory()
