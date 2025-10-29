from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Category:
    id_category: Optional[UUID]
    description: str
