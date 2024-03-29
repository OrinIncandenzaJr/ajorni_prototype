"""post to itinerary

Revision ID: adc21dabac02
Revises: dd2b66b638b0
Create Date: 2019-06-10 08:33:50.447200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adc21dabac02'
down_revision = 'dd2b66b638b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('itinerary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_itinerary_timestamp'), 'itinerary', ['timestamp'], unique=False)
    op.drop_index('ix_post_timestamp', table_name='post')
    op.drop_table('post')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('body', sa.VARCHAR(length=140), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_post_timestamp', 'post', ['timestamp'], unique=False)
    op.drop_index(op.f('ix_itinerary_timestamp'), table_name='itinerary')
    op.drop_table('itinerary')
    # ### end Alembic commands ###
