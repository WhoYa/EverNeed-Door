"""ver 1.1

Revision ID: 23e806adf8c0
Revises: d5799a98bf9c
Create Date: 2025-05-03 03:08:53.311528

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '23e806adf8c0'
down_revision: Union[str, None] = 'd5799a98bf9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('admin_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('admin_id'),
        sa.UniqueConstraint('user_id', name='uq_admin_users_user_id')
    )

    # Create adminlogs table
    op.create_table(
        'adminlogs',
        sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.admin_id']),
        sa.PrimaryKeyConstraint('log_id')
    )

    # Create productstatistics table
    op.create_table(
        'productstatistics',
        sa.Column('stat_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('stat_type', sa.String(length=20), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.PrimaryKeyConstraint('stat_id')
    )
    # Functional unique index on daily stats
    op.create_index(
        'uq_product_stat_daily',
        'productstatistics',
        ['product_id', 'stat_type', sa.text('date(date)')],
        unique=True
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('sub_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BIGINT(), nullable=False),
        sa.Column('subscription_type', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('sub_id'),
        sa.UniqueConstraint('user_id', 'subscription_type', name='uq_user_subscription_type')
    )

    # Create productpromotions table with renamed unique constraint
    op.create_table(
        'productpromotions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('promo_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.ForeignKeyConstraint(['promo_id'], ['promotions.promo_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'promo_id', name='uq_productpromotions_prod_promo')
    )

    # Drop old table if exists
    op.drop_table('product_promotions')


def downgrade() -> None:
    # Recreate old product_promotions table
    op.create_table(
        'product_promotions',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.INTEGER(), nullable=False),
        sa.Column('promo_id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], name='product_promotions_product_id_fkey', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['promo_id'], ['promotions.promo_id'], name='product_promotions_promo_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='product_promotions_pkey'),
        sa.UniqueConstraint('product_id', 'promo_id', name='uq_product_promotion')
    )
    op.drop_table('productpromotions')
    op.drop_table('subscriptions')
    op.drop_table('productstatistics')
    op.drop_table('adminlogs')
    op.drop_table('admin_users')
