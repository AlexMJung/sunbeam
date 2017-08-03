"""empty message

Revision ID: 01577576887b
Revises: a3517d3bcb2a
Create Date: 2017-08-03 10:35:43.786196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01577576887b'
down_revision = 'a3517d3bcb2a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('qbo_blueprint_authentication_tokens')


def downgrade():
    raise Exception
