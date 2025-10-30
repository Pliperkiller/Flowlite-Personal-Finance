from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from decimal import Decimal


class RawTransaction:
    """Represents an unprocessed transaction from Excel"""
    def __init__(self, date: datetime, description: str, reference: str, amount: Decimal):
        self.date = date
        self.description = description
        self.reference = reference
        self.amount = amount


class ExcelParserPort(ABC):
    @abstractmethod
    def parse(self, file_content: bytes) -> List[RawTransaction]:
        """Parse Excel file and return a list of raw transactions"""
        pass

    @abstractmethod
    def get_bank_code(self) -> str:
        """Return the bank code associated with this parser"""
        pass
