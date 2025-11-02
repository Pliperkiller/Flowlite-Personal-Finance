from dataclasses import dataclass


@dataclass
class Bank:
    """
    Domain entity representing a bank.
    """
    id_bank: str
    bank_name: str
