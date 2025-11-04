from pydantic import BaseModel
from typing import List
from .user_dto import UserDTO
from .balance_dto import BalanceDTO
from .transaction_dto import TransactionDTO
from .insight_dto import RecommendationDTO


class DashboardDTO(BaseModel):
    """
    DTO for dashboard data.
    Contains user info, balance summary, recent transactions, and top recommendations.
    """
    userInfo: UserDTO
    balance: BalanceDTO
    transactions: List[TransactionDTO]
    recommendations: List[RecommendationDTO]

    class Config:
        from_attributes = True
