from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...domain.ports import CategoriaRepositoryPort
from ...domain.entities import Categoria
from ..database.models import CategoriaModel


class MySQLCategoriaRepository(CategoriaRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_nombre(self, nombre: str) -> Optional[Categoria]:
        result = await self.session.execute(
            select(CategoriaModel).where(CategoriaModel.nombre == nombre)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, categoria: Categoria) -> Categoria:
        model = self._to_model(categoria)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, id: int) -> Optional[Categoria]:
        result = await self.session.execute(
            select(CategoriaModel).where(CategoriaModel.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    def _to_model(self, entity: Categoria) -> CategoriaModel:
        return CategoriaModel(
            id=entity.id,
            nombre=entity.nombre,
            descripcion=entity.descripcion,
        )

    def _to_entity(self, model: CategoriaModel) -> Categoria:
        return Categoria(
            id=model.id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
