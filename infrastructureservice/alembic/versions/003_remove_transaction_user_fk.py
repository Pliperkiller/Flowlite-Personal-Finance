"""Remove foreign key constraint from Transaction.id_user

Revision ID: 003
Revises: 002
Create Date: 2025-10-31 00:00:00.000000

This migration removes the foreign key constraint from Transaction.id_user
to allow microservices independence. The UploadService will validate user
existence through the IdentityService API rather than database constraints.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove the foreign key constraint from Transaction.id_user.

    This allows the UploadService to operate independently from the User table,
    following microservices best practices where services validate references
    through APIs rather than database constraints.
    """
    # Drop the foreign key constraint
    # MySQL auto-generates the constraint name, typically 'Transaction_ibfk_N'
    # We need to find and drop it
    op.drop_constraint('Transaction_ibfk_4', 'Transaction', type_='foreignkey')


def downgrade() -> None:
    """
    Re-add the foreign key constraint to Transaction.id_user.
    """
    # Re-add the foreign key constraint
    op.create_foreign_key(
        'Transaction_ibfk_4',
        'Transaction', 'User',
        ['id_user'], ['id_user']
    )
