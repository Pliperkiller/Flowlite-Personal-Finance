from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID
from decimal import Decimal

from ...domain.ports import DashboardRepositoryPort
from ...domain.entities import Dashboard, User, Balance, Transaction as TransactionEntity, Insight as InsightEntity
from ..database.models import User as UserModel, UserInfo, Transaction, TransactionCategory, Bank, Insights, InsightCategory


class DashboardRepository(DashboardRepositoryPort):
    """
    Repository for dashboard operations using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_by_user(self, user_id: UUID) -> Dashboard:
        """
        Get complete dashboard data for a user.
        """
        # 1. Get user information
        user_query = (
            select(UserModel)
            .where(UserModel.id_user == str(user_id))
        )
        user_result = await self.session.execute(user_query)
        user_model = user_result.scalar_one_or_none()

        if not user_model:
            raise ValueError(f"User not found: {user_id}")

        user = User(
            id_user=UUID(str(user_model.id_user).strip()),
            username=user_model.username,
            email=user_model.email,
        )

        # 2. Calculate balance (total incomes and expenses)
        balance_query = (
            select(
                func.sum(
                    case(
                        (Transaction.transaction_type == "income", Transaction.value),
                        else_=0
                    )
                ).label("total_incomes"),
                func.sum(
                    case(
                        (Transaction.transaction_type == "expense", Transaction.value),
                        else_=0
                    )
                ).label("total_expenses"),
            )
            .where(Transaction.id_user == str(user_id))
        )
        balance_result = await self.session.execute(balance_query)
        balance_row = balance_result.one()

        total_incomes = Decimal(str(balance_row.total_incomes or 0))
        total_expenses = Decimal(str(balance_row.total_expenses or 0))
        total_balance = total_incomes - total_expenses

        balance = Balance(
            totalBalance=total_balance,
            incomes=total_incomes,
            expenses=total_expenses,
        )

        # 3. Get last 3 transactions
        transactions_query = (
            select(Transaction)
            .options(joinedload(Transaction.category), joinedload(Transaction.bank))
            .where(Transaction.id_user == str(user_id))
            .order_by(Transaction.transaction_date.desc())
            .limit(3)
        )
        transactions_result = await self.session.execute(transactions_query)
        transactions_models = transactions_result.scalars().unique().all()

        transactions = []
        for t in transactions_models:
            try:
                # Parse id_bank
                id_bank_value = None
                if t.id_bank:
                    bank_str = str(t.id_bank).strip()
                    try:
                        id_bank_value = UUID(bank_str)
                    except ValueError:
                        id_bank_value = bank_str

                # Parse id_batch
                id_batch_value = None
                if t.id_batch:
                    try:
                        id_batch_value = UUID(str(t.id_batch).strip())
                    except ValueError:
                        id_batch_value = str(t.id_batch).strip()

                transactions.append(
                    TransactionEntity(
                        id_transaction=UUID(str(t.id_transaction).strip()),
                        id_user=UUID(str(t.id_user).strip()),
                        id_category=UUID(str(t.id_category).strip()),
                        id_bank=id_bank_value,
                        id_batch=id_batch_value,
                        transaction_name=t.transaction_name,
                        value=t.value,
                        transaction_date=t.transaction_date,
                        transaction_type=t.transaction_type,
                        category_description=t.category.description if t.category else None,
                        bank_name=t.bank.bank_name if t.bank else None,
                    )
                )
            except (ValueError, AttributeError) as e:
                print(f"Warning: Skipping transaction with invalid data: {t.id_transaction} - {e}")
                continue

        # 4. Get top 2 recommendations by relevance (higher relevance number = higher priority)
        insights_query = (
            select(Insights)
            .options(joinedload(Insights.category))
            .where(Insights.id_user == str(user_id))
            .order_by(Insights.relevance.desc())
            .limit(2)
        )
        insights_result = await self.session.execute(insights_query)
        insights_models = insights_result.scalars().unique().all()

        recommendations = []
        for i in insights_models:
            try:
                # Parse id_user
                id_user_value = None
                if i.id_user:
                    user_str = str(i.id_user).strip()
                    try:
                        id_user_value = UUID(user_str)
                    except ValueError:
                        id_user_value = user_str

                # Parse id_category
                id_category_value = None
                if i.id_category:
                    category_str = str(i.id_category).strip()
                    try:
                        id_category_value = UUID(category_str)
                    except ValueError:
                        id_category_value = category_str

                recommendations.append(
                    InsightEntity(
                        id_insight=UUID(str(i.id_insight).strip()),
                        id_user=id_user_value,
                        id_category=id_category_value,
                        title=i.title,
                        text=i.text,
                        relevance=i.relevance,
                        created_at=i.created_at,
                        category_type=i.category.description if i.category else None,
                    )
                )
            except (ValueError, AttributeError) as e:
                print(f"Warning: Skipping insight with invalid data: {i.id_insight} - {e}")
                continue

        # 5. Build and return dashboard
        return Dashboard(
            user=user,
            balance=balance,
            transactions=transactions,
            recommendations=recommendations,
        )
