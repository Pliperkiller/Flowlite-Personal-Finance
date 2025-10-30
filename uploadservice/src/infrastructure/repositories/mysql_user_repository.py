from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ...domain.ports import UserRepositoryPort


class MySQLUserRepository(UserRepositoryPort):
    """MySQL implementation of the User repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> bool:
        """Check if the user exists in the users table (created by the auth service)"""
        result = await self.session.execute(
            text("SELECT EXISTS(SELECT 1 FROM usuarios WHERE id = :id)"),
            {"id": id}
        )
        exists = result.scalar()
        return bool(exists)
