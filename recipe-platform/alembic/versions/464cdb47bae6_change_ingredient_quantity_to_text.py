"""Change ingredient quantity to text

Revision ID: 464cdb47bae6
Revises: 54a34038d6e2
Create Date: 2026-08-23 10:52:27.626506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '464cdb47bae6'
down_revision: Union[str, Sequence[str], None] = '54a34038d6e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "recipe_ingredients",
        "quantity",
        existing_type=sa.Numeric(precision=10, scale=3),
        type_=sa.String(length=50),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "recipe_ingredients",
        "quantity",
        existing_type=sa.String(length=50),
        type_=sa.Numeric(precision=10, scale=3),
        existing_nullable=False,
    )
