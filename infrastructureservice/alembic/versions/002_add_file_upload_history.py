"""Add FileUploadHistory table for duplicate file detection

Revision ID: 002
Revises: 001
Create Date: 2025-10-30 00:00:00.000000

This migration adds the FileUploadHistory table to track uploaded files
and prevent duplicate processing based on file content hash (SHA256).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the FileUploadHistory table.

    This table tracks uploaded files to prevent duplicate processing by:
    - Storing SHA256 hash of file content
    - Linking to the user who uploaded it
    - Linking to the TransactionBatch created from it
    - Providing fast duplicate detection via composite index on (id_user, file_hash)
    """
    op.create_table('FileUploadHistory',
        sa.Column('id_file', mysql.CHAR(36), nullable=False),
        sa.Column('id_user', mysql.CHAR(36), nullable=False),
        sa.Column('file_hash', mysql.CHAR(64), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('bank_code', sa.String(length=50), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('id_batch', mysql.CHAR(36), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_batch'], ['TransactionBatch.id_batch'], ),
        sa.PrimaryKeyConstraint('id_file')
    )

    # Create indexes for efficient querying
    # Individual indexes
    op.create_index('ix_FileUploadHistory_id_user', 'FileUploadHistory', ['id_user'])
    op.create_index('ix_FileUploadHistory_file_hash', 'FileUploadHistory', ['file_hash'])

    # Composite index for fast duplicate detection (user + hash combination)
    op.create_index('idx_user_hash', 'FileUploadHistory', ['id_user', 'file_hash'])


def downgrade() -> None:
    """
    Drop the FileUploadHistory table and its indexes.
    """
    # Drop indexes first
    op.drop_index('idx_user_hash', table_name='FileUploadHistory')
    op.drop_index('ix_FileUploadHistory_file_hash', table_name='FileUploadHistory')
    op.drop_index('ix_FileUploadHistory_id_user', table_name='FileUploadHistory')

    # Drop table
    op.drop_table('FileUploadHistory')
