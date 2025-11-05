from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ...infrastructure.database import get_db
from ...infrastructure.repositories import (
    TransactionRepository,
    InsightRepository,
    BankRepository,
    CategoryRepository,
    DashboardRepository,
)


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    """Dependency to get transaction repository."""
    return TransactionRepository(db)


def get_insight_repository(db: AsyncSession = Depends(get_db)) -> InsightRepository:
    """Dependency to get insight repository."""
    return InsightRepository(db)


def get_bank_repository(db: AsyncSession = Depends(get_db)) -> BankRepository:
    """Dependency to get bank repository."""
    return BankRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    """Dependency to get category repository."""
    return CategoryRepository(db)


def get_dashboard_repository(db: AsyncSession = Depends(get_db)) -> DashboardRepository:
    """Dependency to get dashboard repository."""
    return DashboardRepository(db)
