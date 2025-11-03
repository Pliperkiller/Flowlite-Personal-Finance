from fastapi import APIRouter, Depends

from ...application.dto import (
    BankDTO,
    CategoryDTO,
    BanksResponse,
    TransactionCategoriesResponse,
    InsightCategoriesResponse,
)
from ...domain.ports import BankRepositoryPort, CategoryRepositoryPort
from ..dependencies import get_bank_repository, get_category_repository

router = APIRouter(tags=["Catalogs"])


@router.get("/banks", response_model=BanksResponse)
async def get_banks(
    bank_repo: BankRepositoryPort = Depends(get_bank_repository),
):
    """
    Get all available banks.

    No authentication required.
    """
    banks = await bank_repo.get_all_banks()

    bank_dtos = [
        BankDTO(
            id=str(b.id_bank),
            name=b.bank_name,
        )
        for b in banks
    ]

    return BanksResponse(banks=bank_dtos)


@router.get("/transaction-categories", response_model=TransactionCategoriesResponse)
async def get_transaction_categories(
    category_repo: CategoryRepositoryPort = Depends(get_category_repository),
):
    """
    Get all available transaction categories.

    No authentication required.
    """
    categories = await category_repo.get_all_transaction_categories()

    category_dtos = [
        CategoryDTO(
            id=str(c.id_category),
            description=c.description,
        )
        for c in categories
    ]

    return TransactionCategoriesResponse(categories=category_dtos)


@router.get("/insight-categories", response_model=InsightCategoriesResponse)
async def get_insight_categories(
    category_repo: CategoryRepositoryPort = Depends(get_category_repository),
):
    """
    Get all available insight/recommendation categories.

    No authentication required.
    """
    categories = await category_repo.get_all_insight_categories()

    category_dtos = [
        CategoryDTO(
            id=str(c.id_category),
            description=c.description,
        )
        for c in categories
    ]

    return InsightCategoriesResponse(categories=category_dtos)
