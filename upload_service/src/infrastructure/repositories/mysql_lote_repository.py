from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import LoteTransaccionRepositoryPort
from ...domain.entities import LoteTransaccion
from ...domain.entities.lote_transaccion import EstadoLote
from ..database.models import LoteTransaccionModel


class MySQLLoteTransaccionRepository(LoteTransaccionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, lote: LoteTransaccion) -> LoteTransaccion:
        model = self._to_model(lote)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, id: int) -> Optional[LoteTransaccion]:
        result = await self.session.execute(
            select(LoteTransaccionModel).where(LoteTransaccionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, lote: LoteTransaccion) -> LoteTransaccion:
        result = await self.session.execute(
            select(LoteTransaccionModel).where(LoteTransaccionModel.id == lote.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.estado = lote.estado.value
            model.registros_procesados = lote.registros_procesados
            await self.session.flush()
            await self.session.refresh(model)
            return self._to_entity(model)
        return lote

    def _to_model(self, entity: LoteTransaccion) -> LoteTransaccionModel:
        return LoteTransaccionModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            banco_id=entity.banco_id,
            estado=entity.estado.value,
            total_registros=entity.total_registros,
            registros_procesados=entity.registros_procesados,
        )

    def _to_entity(self, model: LoteTransaccionModel) -> LoteTransaccion:
        return LoteTransaccion(
            id=model.id,
            usuario_id=model.usuario_id,
            banco_id=model.banco_id,
            estado=EstadoLote(model.estado),
            total_registros=model.total_registros,
            registros_procesados=model.registros_procesados,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
