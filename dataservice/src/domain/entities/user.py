from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    """
    Domain entity representing a user.
    """
    id_user: UUID | str
    username: str
    email: str
