"""update userinfo schema to match Java entity

Revision ID: 005
Revises: 004
Create Date: 2025-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing UserInfo table and recreate it with the correct schema
    # This is safer than trying to alter the existing table with its constraints

    # First, drop the table
    op.drop_table('UserInfo')

    # Recreate UserInfo table with correct schema to match Java entity
    op.create_table('UserInfo',
        sa.Column('id', mysql.CHAR(36), nullable=False),
        sa.Column('user_id', mysql.CHAR(36), nullable=False),
        # Información personal básica
        sa.Column('primer_nombre', sa.String(length=100), nullable=True),
        sa.Column('segundo_nombre', sa.String(length=100), nullable=True),
        sa.Column('primer_apellido', sa.String(length=100), nullable=True),
        sa.Column('segundo_apellido', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.String(length=255), nullable=True),
        sa.Column('ciudad', sa.String(length=100), nullable=True),
        sa.Column('departamento', sa.String(length=100), nullable=True),
        sa.Column('pais', sa.String(length=100), nullable=True),
        sa.Column('fecha_nacimiento', sa.Date(), nullable=True),
        # Información de identificación
        sa.Column('numero_identificacion', sa.String(length=50), nullable=True),
        sa.Column('tipo_identificacion_code', sa.String(length=50), nullable=True),
        sa.Column('tipo_identificacion_description', sa.String(length=255), nullable=True),
        # Información adicional
        sa.Column('genero', sa.String(length=50), nullable=True),
        sa.Column('estado_civil', sa.String(length=50), nullable=True),
        sa.Column('ocupacion', sa.String(length=100), nullable=True),
        # Metadatos
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True, default=True),
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['User.id_user'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_userinfo_user_id')
    )


def downgrade() -> None:
    # Restore the old UserInfo table schema
    op.drop_table('UserInfo')

    op.create_table('UserInfo',
        sa.Column('id_user', mysql.CHAR(36), nullable=False),
        sa.Column('primerNombre', sa.String(length=100), nullable=True),
        sa.Column('segundoNombre', sa.String(length=100), nullable=True),
        sa.Column('primerApellido', sa.String(length=100), nullable=True),
        sa.Column('segundoApellido', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('direccion', sa.String(length=255), nullable=True),
        sa.Column('ciudad', sa.String(length=100), nullable=True),
        sa.Column('departamento', sa.String(length=100), nullable=True),
        sa.Column('pais', sa.String(length=100), nullable=True),
        sa.Column('numeroIdentificacion', sa.String(length=50), nullable=True),
        sa.Column('numeroIdentificacoin', sa.String(length=50), nullable=True),
        sa.Column('tipoIdentificacion', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['id_user'], ['User.id_user'], ),
        sa.PrimaryKeyConstraint('id_user')
    )
