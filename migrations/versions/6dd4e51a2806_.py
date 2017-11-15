"""empty message

Revision ID: 6dd4e51a2806
Revises: 12fc1d203f36
Create Date: 2017-11-09 10:36:42.092251

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6dd4e51a2806'
down_revision = '12fc1d203f36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sync_tc_to_qbo_blueprint_school')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sync_tc_to_qbo_blueprint_school',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('tc_school_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('qbo_company_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'sync_tc_to_qbo_blueprint_school_pkey')
    )
    # ### end Alembic commands ###