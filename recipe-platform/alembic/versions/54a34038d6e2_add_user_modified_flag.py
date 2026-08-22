"""Add user modified flag

Revision ID: 54a34038d6e2
Revises: 0e8a32cde36c
Create Date: 2026-08-22 12:12:16.719308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54a34038d6e2'
down_revision: Union[str, Sequence[str], None] = '0e8a32cde36c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "recipes",
        sa.Column(
            "is_user_modified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "recipes",
        "is_user_modified",
    )
