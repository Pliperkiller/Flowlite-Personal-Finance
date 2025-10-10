from domain.vo.value_objects import ArchivoOrigen, BancoId, CategoriaId, ClasificacionId, Money, UserId, TransaccionId, LoteId
from domain.exceptions.exceptions import ClasificacionException, LoteException, TransaccionException
from domain.enums.enums import EstadoLote, EstadoTransaccion 
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from decimal import Decimal

@dataclass
class Banco:
    """Entidad Banco"""
    id: BancoId
    nombre: str
    codigo: Optional[str] = None
    activo: bool = True
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Nombre de banco requerido")
    
    def desactivar(self):
        """Desactiva el banco"""
        self.activo = False
    
    def activar(self):
        """Activa el banco"""
        self.activo = True


@dataclass
class Categoria:
    """Entidad Categoría"""
    id: CategoriaId
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    icono_url: Optional[str] = None
    color: Optional[str] = None
    categoria_padre_id: Optional[CategoriaId] = None
    palabras_clave: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.codigo or not self.codigo.strip():
            raise ValueError("Código de categoría requerido")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Nombre de categoría requerido")
    
    def agregar_palabra_clave(self, palabra: str):
        """Agrega una palabra clave normalizada"""
        palabra_normalizada = palabra.lower().strip()
        if palabra_normalizada and palabra_normalizada not in self.palabras_clave:
            self.palabras_clave.append(palabra_normalizada)
    
    def tiene_palabra_clave(self, palabra: str) -> bool:
        """Verifica si la categoría tiene una palabra clave"""
        return palabra.lower().strip() in self.palabras_clave


@dataclass
class ClasificacionTransaccion:
    """Entidad Clasificación de Transacción"""
    id: ClasificacionId
    categoria_id: CategoriaId
    confianza: Decimal
    modelo_version: str
    fecha_clasificacion: datetime = field(default_factory=datetime.now)
    validada_manualmente: bool = False
    validada_por_user_id: Optional[UserId] = None
    fecha_validacion: Optional[datetime] = None
    
    def __post_init__(self):
        self._validar_confianza()
        if not self.modelo_version or not self.modelo_version.strip():
            raise ValueError("Versión del modelo requerida")
    
    def _validar_confianza(self):
        """Valida que la confianza esté entre 0 y 1"""
        if self.confianza < Decimal('0') or self.confianza > Decimal('1'):
            raise ClasificacionException("La confianza debe estar entre 0 y 1")
    
    def tiene_baja_confianza(self, umbral: Decimal = Decimal('0.7')) -> bool:
        """Verifica si la clasificación tiene baja confianza"""
        return self.confianza < umbral
    
    def validar_manualmente(self, user_id: UserId):
        """Marca la clasificación como validada manualmente"""
        if self.validada_manualmente:
            raise ClasificacionException("La clasificación ya fue validada")
        
        self.validada_manualmente = True
        self.validada_por_user_id = user_id
        self.fecha_validacion = datetime.now()


@dataclass
class Transaccion:
    """Entidad Transacción - Agregado Root"""
    id: TransaccionId
    user_id: UserId
    banco_id: BancoId
    lote_id: LoteId
    fecha: datetime
    descripcion: str
    valor: Money
    referencia: Optional[str] = None
    clasificacion: Optional[ClasificacionTransaccion] = None
    estado: EstadoTransaccion = EstadoTransaccion.PENDIENTE
    created_at: datetime = field(default_factory=datetime.now)
    mensaje_error: Optional[str] = None
    
    def __post_init__(self):
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("Descripción requerida")
        if self.valor.es_cero():
            raise ValueError("El valor no puede ser cero")
    
    def asignar_clasificacion(self, clasificacion: ClasificacionTransaccion):
        """Asigna una clasificación a la transacción"""
        if self.estado != EstadoTransaccion.PENDIENTE:
            raise TransaccionException(
                "Solo se pueden clasificar transacciones pendientes"
            )
        
        self.clasificacion = clasificacion
        self.estado = EstadoTransaccion.PROCESADA
        self.mensaje_error = None
    
    def marcar_como_error(self, mensaje_error: str):
        """Marca la transacción como error"""
        if not mensaje_error:
            raise ValueError("Mensaje de error requerido")
        
        self.estado = EstadoTransaccion.ERROR
        self.mensaje_error = mensaje_error
    
    def esta_clasificada(self) -> bool:
        """Verifica si la transacción está clasificada"""
        return self.clasificacion is not None
    
    def es_debito(self) -> bool:
        """Verifica si es un débito (valor negativo)"""
        return self.valor.es_negativo()
    
    def es_credito(self) -> bool:
        """Verifica si es un crédito (valor positivo)"""
        return self.valor.es_positivo()
    
    def clasificacion_requiere_revision(self) -> bool:
        """Verifica si la clasificación requiere revisión manual"""
        if not self.esta_clasificada():
            return False
        return self.clasificacion.tiene_baja_confianza()


@dataclass
class LoteCarga:
    """
    Entidad LoteCarga - ACTUALIZADA para soportar múltiples archivos
    """
    id: LoteId
    nombre_lote: str  # Nombre descriptivo del lote
    cargado_por_user_id: 'UserId'
    total_transacciones: int
    archivos_origen: List[ArchivoOrigen] = field(default_factory=list)  # ← NUEVO
    estado: EstadoLote = EstadoLote.PENDIENTE
    fecha_carga: datetime = field(default_factory=datetime.now)
    transacciones_procesadas: int = 0
    transacciones_con_error: int = 0
    fecha_inicio_procesamiento: Optional[datetime] = None
    fecha_fin_procesamiento: Optional[datetime] = None
    mensaje_error: Optional[str] = None
    
    def __post_init__(self):
        if not self.nombre_lote or not self.nombre_lote.strip():
            raise ValueError("Nombre de lote requerido")
        if self.total_transacciones <= 0:
            raise ValueError("Total de transacciones debe ser mayor a 0")
    
    # Métodos originales (mantenidos)
    def iniciar_procesamiento(self):
        if self.estado != EstadoLote.PENDIENTE:
            raise Exception("El lote ya fue procesado")
        self.estado = EstadoLote.PROCESANDO
        self.fecha_inicio_procesamiento = datetime.now()
    
    def registrar_transaccion_procesada(self):
        self.transacciones_procesadas += 1
        self._verificar_completitud()
    
    def registrar_transaccion_con_error(self):
        self.transacciones_con_error += 1
        self._verificar_completitud()
    
    def _verificar_completitud(self):
        procesadas_total = self.transacciones_procesadas + self.transacciones_con_error
        if procesadas_total >= self.total_transacciones:
            self._finalizar_procesamiento()
    
    def _finalizar_procesamiento(self):
        if self.transacciones_con_error == 0:
            self.estado = EstadoLote.COMPLETADO
        else:
            self.estado = EstadoLote.COMPLETADO_CON_ERRORES
        self.fecha_fin_procesamiento = datetime.now()
    
    def calcular_porcentaje_procesamiento(self) -> Decimal:
        if self.total_transacciones == 0:
            return Decimal('0')
        total_procesado = self.transacciones_procesadas + self.transacciones_con_error
        porcentaje = (Decimal(total_procesado) / Decimal(self.total_transacciones)) * Decimal('100')
        return porcentaje.quantize(Decimal('0.01'))
    
    # NUEVOS métodos para múltiples archivos
    def agregar_archivo_origen(self, archivo: ArchivoOrigen):
        """Agrega un archivo al lote"""
        if self.tiene_archivo_con_hash(archivo.hash_md5):
            raise ValueError(f"Archivo duplicado con hash {archivo.hash_md5}")
        self.archivos_origen.append(archivo)
    
    def tiene_archivo_con_hash(self, hash_md5: str) -> bool:
        """Verifica si existe un archivo con el hash dado"""
        return any(a.hash_md5 == hash_md5 for a in self.archivos_origen)
    
    def cantidad_archivos(self) -> int:
        """Cantidad de archivos en el lote"""
        return len(self.archivos_origen)
    
    def es_lote_consolidado(self) -> bool:
        """Verifica si consolida múltiples archivos"""
        return len(self.archivos_origen) > 1
    
    def tamanio_total_bytes(self) -> int:
        """Tamaño total de todos los archivos"""
        return sum(a.tamanio_bytes for a in self.archivos_origen)