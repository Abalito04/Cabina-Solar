"""empresa_id en cliente y producto

Revision ID: fac5246bfc6d
Revises: 9137138e72fa
Create Date: 2026-04-30 19:26:04.859297

"""
from alembic import op
import sqlalchemy as sa

revision = 'fac5246bfc6d'
down_revision = '9137138e72fa'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.add_column(sa.Column('empresa_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_cliente_empresa', 'empresa', ['empresa_id'], ['id'])

    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('empresa_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_producto_empresa', 'empresa', ['empresa_id'], ['id'])


def downgrade():
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.drop_constraint('fk_producto_empresa', type_='foreignkey')
        batch_op.drop_column('empresa_id')

    with op.batch_alter_table('cliente', schema=None) as batch_op:
        batch_op.drop_constraint('fk_cliente_empresa', type_='foreignkey')
        batch_op.drop_column('empresa_id')
