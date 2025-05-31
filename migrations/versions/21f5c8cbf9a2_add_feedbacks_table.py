"""add_feedbacks_table

Revision ID: 21f5c8cbf9a2
Revises: fix_favorites_pk
Create Date: 2025-05-31 14:35:52.069172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '21f5c8cbf9a2'
down_revision: Union[str, None] = 'fix_favorites_pk'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create feedbacks table
    op.create_table('feedbacks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BIGINT(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop feedbacks table
    op.drop_table('feedbacks')
