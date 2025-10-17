from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from decimal import Decimal


class TransaccionRaw:
    """Representa una transacción sin procesar del Excel"""
    def __init__(self, fecha: datetime, descripcion: str, referencia: str, valor: Decimal):
        self.fecha = fecha
        self.descripcion = descripcion
        self.referencia = referencia
        self.valor = valor


class ExcelParserPort(ABC):
    @abstractmethod
    def parse(self, file_content: bytes) -> List[TransaccionRaw]:
        """Parse el archivo Excel y retorna una lista de transacciones raw"""
        pass

    @abstractmethod
    def get_banco_codigo(self) -> str:
        """Retorna el código del banco asociado a este parser"""
        pass
