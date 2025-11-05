from pydantic import BaseModel


class BalanceDTO(BaseModel):
    """
    DTO for balance summary.
    totalBalance = incomes - expenses
    """
    totalBalance: float
    incomes: float
    expenses: float

    class Config:
        from_attributes = True
