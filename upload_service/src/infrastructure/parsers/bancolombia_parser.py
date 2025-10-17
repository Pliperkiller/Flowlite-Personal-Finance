from typing import List
import pandas as pd
from io import BytesIO
from decimal import Decimal
from ...domain.ports.excel_parser_port import ExcelParserPort, TransaccionRaw


class BancolombiaParser(ExcelParserPort):
    BANCO_CODIGO = "BANCOLOMBIA"

    def parse(self, file_content: bytes) -> List[TransaccionRaw]:
        """
        Parsea archivos de Excel de Bancolombia
        Formato esperado: Fecha, Descripción, Referencia, Valor
        """
        df = pd.read_excel(BytesIO(file_content))

        # Validar columnas esperadas
        expected_columns = ["Fecha", "Descripción", "Referencia", "Valor"]
        if not all(col in df.columns for col in expected_columns):
            raise ValueError(
                f"El archivo no tiene el formato esperado de Bancolombia. "
                f"Columnas esperadas: {expected_columns}"
            )

        transacciones = []
        for _, row in df.iterrows():
            transaccion = TransaccionRaw(
                fecha=pd.to_datetime(row["Fecha"]),
                descripcion=str(row["Descripción"]),
                referencia=str(row["Referencia"]) if pd.notna(row["Referencia"]) else None,
                valor=Decimal(str(row["Valor"])),
            )
            transacciones.append(transaccion)

        return transacciones

    def get_banco_codigo(self) -> str:
        return self.BANCO_CODIGO
