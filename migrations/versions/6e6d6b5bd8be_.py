"""empty message

Revision ID: 6e6d6b5bd8be
Revises: ed8fc7aebf25
Create Date: 2017-09-06 11:14:46.394266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e6d6b5bd8be'
down_revision = 'ed8fc7aebf25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('authorize_qbo_blueprint_authentication_tokens', sa.Column('refresh_token', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('authorize_qbo_blueprint_authentication_tokens', 'refresh_token')
    # ### end Alembic commands ###