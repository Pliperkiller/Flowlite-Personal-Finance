from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ...domain.ports import UsuarioRepositoryPort


class MySQLUsuarioRepository(UsuarioRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> bool:
        """Verifica si el usuario existe en la tabla usuarios (creada por el servicio de auth)"""
        result = await self.session.execute(
            text("SELECT EXISTS(SELECT 1 FROM usuarios WHERE id = :id)"),
            {"id": id}
        )
        exists = result.scalar()
        return bool(exists)
