from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Balance:
    """
    Domain entity representing user's balance summary.
    totalBalance = incomes - expenses
    """
    totalBalance: Decimal
    incomes: Decimal
    expenses: Decimal
