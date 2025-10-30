from dataclasses import dataclass
from typing import Optional


@dataclass
class Bank:
    id_bank: Optional[str]
    bank_name: str
