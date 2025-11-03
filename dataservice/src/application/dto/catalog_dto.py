from pydantic import BaseModel
from typing import List


class BankDTO(BaseModel):
    """
    DTO for bank data.
    """
    id: str
    name: str

    class Config:
        from_attributes = True


class CategoryDTO(BaseModel):
    """
    DTO for category data.
    """
    id: str
    description: str

    class Config:
        from_attributes = True


class BanksResponse(BaseModel):
    """
    Response for banks endpoint.
    """
    banks: List[BankDTO]


class TransactionCategoriesResponse(BaseModel):
    """
    Response for transaction categories endpoint.
    """
    categories: List[CategoryDTO]


class InsightCategoriesResponse(BaseModel):
    """
    Response for insight categories endpoint.
    """
    categories: List[CategoryDTO]
