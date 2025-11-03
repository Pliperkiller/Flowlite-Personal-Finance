from fastapi import APIRouter, Depends, Query
from uuid import UUID
from math import ceil
import os
from ...application.dto import TransactionDTO, TransactionsPaginatedResponse
from ...domain.ports import TransactionRepositoryPort
from ..dependencies import get_current_user, get_transaction_repository

DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 10))

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionsPaginatedResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    current_user: UUID = Depends(get_current_user),
    transaction_repo: TransactionRepositoryPort = Depends(get_transaction_repository),
):
    page_size = DEFAULT_PAGE_SIZE
    transactions, total_count = await transaction_repo.get_transactions_by_user(
        user_id=current_user,
        page=page,
        page_size=page_size,
    )
    total_pages = ceil(total_count / page_size) if total_count > 0 else 0
    transaction_dtos = [
        TransactionDTO(
            id=str(t.id_transaction),
            name=t.transaction_name,
            value=float(t.value),
            date=t.transaction_date.isoformat(),
            type=t.transaction_type,
            category=t.category_description or "",
            bank=t.bank_name,
        )
        for t in transactions
    ]
    return TransactionsPaginatedResponse(
        transactions=transaction_dtos,
        page=page,
        pageSize=page_size,
        totalPages=total_pages,
        totalTransactions=total_count,
    )
