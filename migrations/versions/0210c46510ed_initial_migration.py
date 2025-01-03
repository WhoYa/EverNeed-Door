"""Initial migration

Revision ID: 0210c46510ed
Revises: 
Create Date: 2024-11-15 07:18:15.592383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0210c46510ed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('product_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('material', sa.String(length=50), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('role', sa.String(length=10), server_default=sa.text("'user'"), nullable=False),
    sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('chats',
    sa.Column('chat_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('manager_id', sa.BIGINT(), nullable=True),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('sent_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('favorites',
    sa.Column('favorite_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('favorite_id')
    )
    op.create_table('logs',
    sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.create_table('notifications',
    sa.Column('notification_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('notification_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notifications')
    op.drop_table('logs')
    op.drop_table('favorites')
    op.drop_table('chats')
    op.drop_table('users')
    op.drop_table('products')
    # ### end Alembic commands ###
