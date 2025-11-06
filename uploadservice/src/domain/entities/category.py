from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    """
    Category entity for transaction classification.

    Note: id_category is a string (e.g., "cat-001-retiros-efectivo")
    not a UUID, to match the database schema.
    """
    id_category: Optional[str]
    description: str
