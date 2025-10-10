class DomainException(Exception):
    """Excepción base del dominio"""
    pass


class TransaccionException(DomainException):
    """Excepción específica de Transacción"""
    pass


class LoteException(DomainException):
    """Excepción específica de Lote"""
    pass


class ClasificacionException(DomainException):
    """Excepción específica de Clasificación"""
    pass