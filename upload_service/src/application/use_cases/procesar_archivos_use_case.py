from typing import List
import asyncio
from decimal import Decimal
from ...domain.ports import (
    TransaccionRepositoryPort,
    BancoRepositoryPort,
    CategoriaRepositoryPort,
    LoteTransaccionRepositoryPort,
    ExcelParserPort,
    ClasificadorPort,
)
from ...domain.entities import Transaccion, LoteTransaccion
from ...domain.entities.lote_transaccion import EstadoLote


class ProcesarArchivosUseCase:
    def __init__(
        self,
        transaccion_repo: TransaccionRepositoryPort,
        banco_repo: BancoRepositoryPort,
        categoria_repo: CategoriaRepositoryPort,
        lote_repo: LoteTransaccionRepositoryPort,
        clasificador: ClasificadorPort,
    ):
        self.transaccion_repo = transaccion_repo
        self.banco_repo = banco_repo
        self.categoria_repo = categoria_repo
        self.lote_repo = lote_repo
        self.clasificador = clasificador

    async def execute(
        self,
        archivos_content: List[bytes],
        parser: ExcelParserPort,
        usuario_id: int,
    ) -> int:
        """
        Procesa los archivos de Excel y retorna el ID del lote
        """
        # 1. Obtener el banco
        banco_codigo = parser.get_banco_codigo()
        banco = await self.banco_repo.get_by_codigo(banco_codigo)
        if not banco:
            raise ValueError(f"Banco con código {banco_codigo} no encontrado")

        # 2. Parsear todos los archivos
        todas_transacciones_raw = []
        for file_content in archivos_content:
            transacciones_raw = parser.parse(file_content)
            todas_transacciones_raw.extend(transacciones_raw)

        # 3. Crear el lote
        lote = LoteTransaccion(
            id=None,
            usuario_id=usuario_id,
            banco_id=banco.id,
            estado=EstadoLote.PENDIENTE,
            total_registros=len(todas_transacciones_raw),
            registros_procesados=0,
        )
        lote = await self.lote_repo.save(lote)

        # 4. Procesar en background (en una aplicación real usarías Celery o similar)
        asyncio.create_task(
            self._procesar_transacciones_async(
                todas_transacciones_raw, lote, usuario_id, banco.id
            )
        )

        return lote.id

    async def _procesar_transacciones_async(
        self, transacciones_raw, lote: LoteTransaccion, usuario_id: int, banco_id: int
    ):
        """Procesa las transacciones en lotes de 500"""
        try:
            lote.estado = EstadoLote.PROCESANDO
            await self.lote_repo.update(lote)

            BATCH_SIZE = 500
            for i in range(0, len(transacciones_raw), BATCH_SIZE):
                batch = transacciones_raw[i : i + BATCH_SIZE]

                # Clasificar y crear transacciones
                transacciones = []
                for tx_raw in batch:
                    # Clasificar
                    nombre_categoria = await self.clasificador.clasificar(
                        tx_raw.descripcion
                    )

                    # Obtener o crear categoría
                    categoria = await self.categoria_repo.get_by_nombre(
                        nombre_categoria
                    )
                    if not categoria:
                        from ...domain.entities import Categoria

                        categoria = await self.categoria_repo.save(
                            Categoria(id=None, nombre=nombre_categoria)
                        )

                    # Crear transacción
                    transaccion = Transaccion(
                        id=None,
                        usuario_id=usuario_id,
                        banco_id=banco_id,
                        categoria_id=categoria.id,
                        lote_id=lote.id,
                        fecha=tx_raw.fecha,
                        descripcion=tx_raw.descripcion,
                        referencia=tx_raw.referencia,
                        valor=tx_raw.valor,
                    )
                    transacciones.append(transaccion)

                # Guardar batch
                await self.transaccion_repo.save_batch(transacciones)

                # Actualizar progreso del lote
                lote.registros_procesados += len(batch)
                await self.lote_repo.update(lote)

            # Marcar como completado
            lote.estado = EstadoLote.COMPLETADO
            await self.lote_repo.update(lote)

        except Exception as e:
            lote.estado = EstadoLote.ERROR
            await self.lote_repo.update(lote)
            raise e
