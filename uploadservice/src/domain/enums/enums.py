from enum import Enum


class EstadoTransaccion(str, Enum):
    """Estados de una Transacción"""
    PENDIENTE = "PENDIENTE"
    PROCESADA = "PROCESADA"
    ERROR = "ERROR"


class EstadoLote(str, Enum):
    """Estados de un Lote de Carga"""
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    COMPLETADO_CON_ERRORES = "COMPLETADO_CON_ERRORES"
    FALLIDO = "FALLIDO"