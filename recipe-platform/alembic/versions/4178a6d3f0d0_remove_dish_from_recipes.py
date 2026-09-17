"""remove dish from recipes

Revision ID: 4178a6d3f0d0
Revises: 6c60963ed624
Create Date: 2026-09-16 13:44:41.877923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4178a6d3f0d0'
down_revision: Union[str, Sequence[str], None] = '6c60963ed624'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('recipes', 'dish')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "recipes",
        sa.Column("dish", sa.String(length=200), nullable=True),
    )
