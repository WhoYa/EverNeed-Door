"""Add reviews, categories, and specifications tables

Revision ID: d5799a98bf9c
Revises: 6aa13d42ab40
Create Date: 2025-04-12 03:52:40.300065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5799a98bf9c'
down_revision: Union[str, None] = '6aa13d42ab40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First add nullable columns to the products table for existing records
    op.add_column('products', sa.Column('stock_quantity', sa.Integer(), nullable=True))
    op.add_column('products', sa.Column('is_in_stock', sa.Boolean(), nullable=True))
    op.add_column('products', sa.Column('discount_price', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('products', sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE products SET stock_quantity = 0 WHERE stock_quantity IS NULL")
    op.execute("UPDATE products SET is_in_stock = false WHERE is_in_stock IS NULL")
    
    # Now make the columns non-nullable with defaults for new rows
    op.alter_column('products', 'stock_quantity', nullable=False, server_default='0', existing_type=sa.Integer())
    op.alter_column('products', 'is_in_stock', nullable=False, server_default='false', existing_type=sa.Boolean())
    
    # Create categories table
    op.create_table('categories',
        sa.Column('category_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.category_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    
    # Create product_categories junction table
    op.create_table('product_categories',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('product_id', 'category_id')
    )
    
    # Create promotions table
    op.create_table('promotions',
        sa.Column('promo_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.String(length=20), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('end_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_by', sa.BIGINT(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id']),
        sa.PrimaryKeyConstraint('promo_id')
    )
    
    # Create reviews table
    op.create_table('reviews',
        sa.Column('review_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BIGINT(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('review_id')
    )
    
    # Create specifications table
    op.create_table('specifications',
        sa.Column('spec_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('spec_id'),
        sa.UniqueConstraint('product_id', 'name', name='uq_product_spec_name')
    )
    
    # Create product promotions junction table
    op.create_table('product_promotions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('promo_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['promo_id'], ['promotions.promo_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'promo_id', name='uq_product_promotion')
    )
    
    # Create index on product name
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_products_name'), table_name='products')
    
    # Drop tables
    op.drop_table('product_promotions')
    op.drop_table('specifications')
    op.drop_table('reviews')
    op.drop_table('promotions')
    op.drop_table('product_categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')
    
    # Drop columns from products table
    op.drop_column('products', 'average_rating')
    op.drop_column('products', 'discount_price')
    op.drop_column('products', 'is_in_stock')
    op.drop_column('products', 'stock_quantity')