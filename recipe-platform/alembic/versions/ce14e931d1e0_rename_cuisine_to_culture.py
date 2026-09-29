"""rename cuisine to culture

Revision ID: ce14e931d1e0
Revises: 4178a6d3f0d0
Create Date: 2026-09-26 11:55:35.071809

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ce14e931d1e0'
down_revision: Union[str, Sequence[str], None] = '4178a6d3f0d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "recipes",
        "cuisine",
        new_column_name="culture",
    )

def downgrade() -> None:
    op.alter_column(
        "recipes",
        "culture",
        new_column_name="cuisine",
    )
