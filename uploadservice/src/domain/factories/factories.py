from domain.entities.entities import LoteCarga, Transaccion
from domain.enums.enums import EstadoTransaccion
from domain.vo.value_objects import ArchivoOrigen, ArchivoOrigenId, BancoId, LoteId, Money, TransaccionId, UserId
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid



class TransaccionFactory:
    """Factory para crear Transacciones"""
    
    @staticmethod
    def crear(
        user_id: UserId,
        banco_id: BancoId,
        lote_id: LoteId,
        fecha: datetime,
        descripcion: str,
        valor_cantidad: Decimal,
        referencia: Optional[str] = None,
        moneda: str = "COP"
    ) -> Transaccion:
        """
        Crea una nueva transacción con validaciones de negocio
        """
        
        if not descripcion or not descripcion.strip():
            raise ValueError("Descripción no puede estar vacía")
        
        if valor_cantidad == Decimal('0'):
            raise ValueError("El valor no puede ser cero")
        
        valor = Money(cantidad=valor_cantidad, moneda=moneda)
        
        transaccion_id = TransaccionId(str(uuid.uuid4()))
        
        return Transaccion(
            id=transaccion_id,
            user_id=user_id,
            banco_id=banco_id,
            lote_id=lote_id,
            fecha=fecha,
            descripcion=descripcion.strip(),
            valor=valor,
            referencia=referencia.strip() if referencia else None,
            estado=EstadoTransaccion.PENDIENTE
        )
    
    @staticmethod
    def crear_desde_dict(data: dict, user_id: UserId, banco_id: BancoId, lote_id: LoteId) -> Transaccion:
        """
        Crea una transacción desde un diccionario (útil para parseo de Excel)
        """
        return TransaccionFactory.crear(
            user_id=user_id,
            banco_id=banco_id,
            lote_id=lote_id,
            fecha=data['fecha'],
            descripcion=data['descripcion'],
            valor_cantidad=Decimal(str(data['valor'])),
            referencia=data.get('referencia'),
            moneda=data.get('moneda', 'COP')
        )



class LoteFactory:
    """Factory para crear Lotes"""
    
    @staticmethod
    def crear_lote_simple(
        nombre_archivo: str,
        cargado_por_user_id: 'UserId',
        total_transacciones: int,
        ruta_archivo: str,
        hash_md5: str,
        tamanio_bytes: int
    ) -> LoteCarga:
        """Crea un lote con UN solo archivo"""
        lote_id = LoteId(str(uuid.uuid4()))
        archivo_id = ArchivoOrigenId(str(uuid.uuid4()))
        
        archivo = ArchivoOrigen(
            id=archivo_id,
            nombre=nombre_archivo,
            ruta=ruta_archivo,
            hash_md5=hash_md5,
            tamanio_bytes=tamanio_bytes
        )
        
        return LoteCarga(
            id=lote_id,
            nombre_lote=nombre_archivo,
            cargado_por_user_id=cargado_por_user_id,
            total_transacciones=total_transacciones,
            archivos_origen=[archivo]
        )
    
    @staticmethod
    def crear_lote_consolidado(
        nombre_lote: str,
        cargado_por_user_id: 'UserId',
        archivos_info: List[dict]  # [{'nombre': '', 'ruta': '', 'hash': '', 'tamanio': 0}]
    ) -> LoteCarga:
        """Crea un lote consolidado con múltiples archivos"""
        lote_id = LoteId(str(uuid.uuid4()))
        
        archivos_origen = []
        total_transacciones = 0
        
        for info in archivos_info:
            archivo_id = ArchivoOrigenId(str(uuid.uuid4()))
            archivo = ArchivoOrigen(
                id=archivo_id,
                nombre=info['nombre'],
                ruta=info['ruta'],
                hash_md5=info['hash'],
                tamanio_bytes=info['tamanio']
            )
            archivos_origen.append(archivo)
            total_transacciones += info.get('cantidad_transacciones', 0)
        
        return LoteCarga(
            id=lote_id,
            nombre_lote=nombre_lote,
            cargado_por_user_id=cargado_por_user_id,
            total_transacciones=total_transacciones,
            archivos_origen=archivos_origen
        )



def crear_money_desde_string(valor: str, moneda: str = "COP") -> Money:
    """
    Helper para crear Money desde string
    """
    try:
        valor_limpio = valor.replace(',', '').replace(' ', '').strip()
        cantidad = Decimal(valor_limpio)
        return Money(cantidad=cantidad, moneda=moneda)
    except Exception as e:
        raise ValueError(f"No se pudo crear Money desde '{valor}': {str(e)}")


def normalizar_descripcion(descripcion: str) -> str:
    """
    Normaliza una descripción de transacción
    """
    if not descripcion:
        return ""
    
    import re
    descripcion_normalizada = re.sub(r'\s+', ' ', descripcion)
    
    return descripcion_normalizada.strip()