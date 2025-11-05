from dataclasses import dataclass
from typing import List
from .user import User
from .balance import Balance
from .transaction import Transaction
from .insight import Insight


@dataclass
class Dashboard:
    """
    Domain entity representing the dashboard data for a user.
    """
    user: User
    balance: Balance
    transactions: List[Transaction]
    recommendations: List[Insight]
