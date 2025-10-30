from typing import List
import pandas as pd
from io import BytesIO
from decimal import Decimal
from ...domain.ports.excel_parser_port import ExcelParserPort, RawTransaction


class BancolombiaParser(ExcelParserPort):
    """Parser for Bancolombia Excel files"""

    BANK_CODE = "BANCOLOMBIA"

    def parse(self, file_content: bytes) -> List[RawTransaction]:
        """
        Parse Bancolombia Excel files
        Expected format: Fecha (Date), Descripción (Description), Referencia (Reference), Valor (Amount)

        Args:
            file_content: The Excel file content as bytes

        Returns:
            List of raw transactions

        Raises:
            ValueError: If the file doesn't have the expected format
        """
        df = pd.read_excel(BytesIO(file_content))

        # Validate expected columns
        expected_columns = ["Fecha", "Descripción", "Referencia", "Valor"]
        if not all(col in df.columns for col in expected_columns):
            raise ValueError(
                f"File does not have the expected Bancolombia format. "
                f"Expected columns: {expected_columns}"
            )

        transactions = []
        for _, row in df.iterrows():
            transaction = RawTransaction(
                date=pd.to_datetime(row["Fecha"]),
                description=str(row["Descripción"]),
                reference=str(row["Referencia"]) if pd.notna(row["Referencia"]) else None,
                amount=Decimal(str(row["Valor"])),
            )
            transactions.append(transaction)

        return transactions

    def get_bank_code(self) -> str:
        """Get the bank code for this parser"""
        return self.BANK_CODE
