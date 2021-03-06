"""empty message

Revision ID: 53d38cf80599
Revises: d2aa9022cdc7
Create Date: 2017-09-19 13:53:09.697571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53d38cf80599'
down_revision = 'd2aa9022cdc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tuition_blueprint_recurring_payment', sa.Column('amount', sa.Numeric(precision=8, scale=2), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tuition_blueprint_recurring_payment', 'amount')
    # ### end Alembic commands ###
