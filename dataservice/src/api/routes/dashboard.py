from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from ...application.dto import DashboardDTO, UserDTO, BalanceDTO, TransactionDTO, RecommendationDTO
from ...domain.ports import DashboardRepositoryPort
from ..dependencies import get_current_user, get_dashboard_repository

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardDTO)
async def get_dashboard(
    current_user: UUID = Depends(get_current_user),
    dashboard_repo: DashboardRepositoryPort = Depends(get_dashboard_repository),
):
    """
    Get dashboard data for the authenticated user.

    Returns:
    - User information (username, email)
    - Balance summary (total balance, incomes, expenses)
    - Last 3 transactions
    - Top 2 recommendations by relevance

    Requires authentication via Bearer token.
    """
    try:
        # Get dashboard data from repository
        dashboard = await dashboard_repo.get_dashboard_by_user(user_id=current_user)

        # Convert user to DTO
        user_dto = UserDTO(
            userName=dashboard.user.username,
            email=dashboard.user.email,
        )

        # Convert balance to DTO
        balance_dto = BalanceDTO(
            totalBalance=float(dashboard.balance.totalBalance),
            incomes=float(dashboard.balance.incomes),
            expenses=float(dashboard.balance.expenses),
        )

        # Convert transactions to DTOs
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
            for t in dashboard.transactions
        ]

        # Convert recommendations to DTOs
        recommendation_dtos = [
            RecommendationDTO(
                id=str(r.id_insight),
                type=r.category_type or "general",
                title=r.title,
                description=r.text,
                relevance=r.relevance,
            )
            for r in dashboard.recommendations
        ]

        # Build and return dashboard DTO
        return DashboardDTO(
            userInfo=user_dto,
            balance=balance_dto,
            transactions=transaction_dtos,
            recommendations=recommendation_dtos,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
