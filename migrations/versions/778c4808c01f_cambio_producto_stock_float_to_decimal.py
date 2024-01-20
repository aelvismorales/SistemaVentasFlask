"""cambio Producto stock float to Decimal

Revision ID: 778c4808c01f
Revises: 729af6d55beb
Create Date: 2024-01-18 22:40:19.253427

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '778c4808c01f'
down_revision = '729af6d55beb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.alter_column('stock',
               existing_type=mysql.FLOAT(),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.alter_column('stock',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=mysql.FLOAT(),
               nullable=True)

    # ### end Alembic commands ###
