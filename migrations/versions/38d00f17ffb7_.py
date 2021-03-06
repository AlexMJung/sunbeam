"""empty message

Revision ID: 38d00f17ffb7
Revises: 01577576887b
Create Date: 2017-08-03 10:41:52.260450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38d00f17ffb7'
down_revision = '01577576887b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authorize_qbo_blueprint_authentication_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('company_id', sa.BigInteger(), nullable=True),
    sa.Column('oauth_token', sa.String(length=120), nullable=True),
    sa.Column('oauth_token_secret', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('authorize_qbo_blueprint_authentication_tokens')
    # ### end Alembic commands ###
