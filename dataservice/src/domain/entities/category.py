from dataclasses import dataclass


@dataclass
class TransactionCategory:
    """
    Domain entity representing a transaction category.
    """
    id_category: str
    description: str


@dataclass
class InsightCategory:
    """
    Domain entity representing an insight category.
    """
    id_category: str
    description: str
