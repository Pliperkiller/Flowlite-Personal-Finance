from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import BancoRepositoryPort
from ...domain.entities import Banco
from ..database.models import BancoModel


class MySQLBancoRepository(BancoRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_codigo(self, codigo: str) -> Optional[Banco]:
        result = await self.session.execute(
            select(BancoModel).where(BancoModel.codigo == codigo)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, banco: Banco) -> Banco:
        model = self._to_model(banco)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, id: int) -> Optional[Banco]:
        result = await self.session.execute(
            select(BancoModel).where(BancoModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Banco) -> BancoModel:
        return BancoModel(
            id=entity.id,
            nombre=entity.nombre,
            codigo=entity.codigo,
        )

    def _to_entity(self, model: BancoModel) -> Banco:
        return Banco(
            id=model.id,
            nombre=model.nombre,
            codigo=model.codigo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
