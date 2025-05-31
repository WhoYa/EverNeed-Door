"""fix favorites primary key

Revision ID: fix_favorites_pk
Revises: c2a2559e1f0f
Create Date: 2025-05-31 00:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_favorites_pk'
down_revision: Union[str, None] = 'c2a2559e1f0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add primary key constraint to favorites.id if it doesn't exist
    op.execute("ALTER TABLE favorites ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);")


def downgrade() -> None:
    # Remove primary key constraint from favorites.id
    op.execute("ALTER TABLE favorites DROP CONSTRAINT IF EXISTS favorites_pkey;")