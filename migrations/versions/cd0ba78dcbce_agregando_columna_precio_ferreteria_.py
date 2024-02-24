"""agregando columna precio_ferreteria_producto

Revision ID: cd0ba78dcbce
Revises: ef7b050fb2c7
Create Date: 2024-02-23 20:24:16.293856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd0ba78dcbce'
down_revision = 'ef7b050fb2c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('precio_venta_ferreteria', sa.Numeric(precision=10, scale=2), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.drop_column('precio_venta_ferreteria')

    # ### end Alembic commands ###