"""Make User.password field nullable for external authentication

Revision ID: 004
Revises: 003
Create Date: 2025-10-31 12:00:00.000000

This migration changes the User.password column to be nullable, allowing
users to authenticate through external providers (OAuth, SSO, etc.) without
requiring a local password.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Change User.password column to be nullable.

    This allows users to authenticate through external providers without
    requiring a local password stored in the database.
    """
    # Modify the password column to allow NULL values
    op.alter_column('User', 'password',
                    existing_type=sa.String(length=255),
                    nullable=True,
                    existing_nullable=False)


def downgrade() -> None:
    """
    Revert User.password column to be non-nullable.

    WARNING: This will fail if there are any users with NULL passwords.
    You may need to update those records before running this downgrade.
    """
    # Revert the password column to not allow NULL values
    op.alter_column('User', 'password',
                    existing_type=sa.String(length=255),
                    nullable=False,
                    existing_nullable=True)
