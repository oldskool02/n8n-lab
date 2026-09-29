"""remove culture from recipes

Revision ID: 7b9c2d4e1a6f
Revises: ce14e931d1e0
Create Date: 2026-09-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7b9c2d4e1a6f"
down_revision: Union[str, Sequence[str], None] = "ce14e931d1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("recipes", "culture")


def downgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("culture", sa.String(), nullable=True),
    )