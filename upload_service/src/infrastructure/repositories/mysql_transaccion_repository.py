from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import TransaccionRepositoryPort
from ...domain.entities import Transaccion
from ..database.models import TransaccionModel


class MySQLTransaccionRepository(TransaccionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_batch(self, transacciones: List[Transaccion]) -> List[Transaccion]:
        models = [self._to_model(tx) for tx in transacciones]
        self.session.add_all(models)
        await self.session.flush()
        return [self._to_entity(model) for model in models]

    async def get_by_id(self, id: int) -> Optional[Transaccion]:
        result = await self.session.execute(
            select(TransaccionModel).where(TransaccionModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Transaccion) -> TransaccionModel:
        return TransaccionModel(
            id=entity.id,
            usuario_id=entity.usuario_id,
            banco_id=entity.banco_id,
            categoria_id=entity.categoria_id,
            lote_id=entity.lote_id,
            fecha=entity.fecha,
            descripcion=entity.descripcion,
            referencia=entity.referencia,
            valor=entity.valor,
        )

    def _to_entity(self, model: TransaccionModel) -> Transaccion:
        return Transaccion(
            id=model.id,
            usuario_id=model.usuario_id,
            banco_id=model.banco_id,
            categoria_id=model.categoria_id,
            lote_id=model.lote_id,
            fecha=model.fecha,
            descripcion=model.descripcion,
            referencia=model.referencia,
            valor=model.valor,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
