from ...domain.ports import ExcelParserPort
from .bancolombia_parser import BancolombiaParser


class ParserFactory:
    """
    Factory para crear parsers de acuerdo al banco
    Esto permite agregar fácilmente nuevos bancos en el futuro
    """

    _parsers = {
        "BANCOLOMBIA": BancolombiaParser,
        # Aquí se pueden agregar más bancos fácilmente:
        # "DAVIVIENDA": DaviviendaParser,
        # "NEQUI": NequiParser,
    }

    @classmethod
    def get_parser(cls, banco_codigo: str) -> ExcelParserPort:
        parser_class = cls._parsers.get(banco_codigo.upper())
        if not parser_class:
            raise ValueError(
                f"No existe parser para el banco {banco_codigo}. "
                f"Bancos soportados: {list(cls._parsers.keys())}"
            )
        return parser_class()

    @classmethod
    def get_supported_banks(cls) -> list:
        return list(cls._parsers.keys())
