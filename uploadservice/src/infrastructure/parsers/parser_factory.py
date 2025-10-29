from ...domain.ports import ExcelParserPort
from .bancolombia_parser import BancolombiaParser


class ParserFactory:
    """
    Factory for creating parsers according to the bank
    This allows easily adding new banks in the future
    """

    _parsers = {
        "BANCOLOMBIA": BancolombiaParser,
        # More banks can be easily added here:
        # "DAVIVIENDA": DaviviendaParser,
        # "NEQUI": NequiParser,
    }

    @classmethod
    def get_parser(cls, bank_code: str) -> ExcelParserPort:
        """
        Get the appropriate parser for a given bank code

        Args:
            bank_code: The bank code to get the parser for

        Returns:
            An instance of the appropriate parser

        Raises:
            ValueError: If no parser exists for the given bank code
        """
        parser_class = cls._parsers.get(bank_code.upper())
        if not parser_class:
            raise ValueError(
                f"No parser exists for bank {bank_code}. "
                f"Supported banks: {list(cls._parsers.keys())}"
            )
        return parser_class()

    @classmethod
    def get_supported_banks(cls) -> list:
        """Get a list of all supported bank codes"""
        return list(cls._parsers.keys())
