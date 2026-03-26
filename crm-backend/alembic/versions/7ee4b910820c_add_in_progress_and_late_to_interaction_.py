"""add in_progress and late to interaction_status

Revision ID: 7ee4b910820c
Revises: d45cb10b2d7b
Create Date: 2026-03-24 14:37:35.558667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ee4b910820c'
down_revision: Union[str, Sequence[str], None] = 'd45cb10b2d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE interaction_status ADD VALUE 'in_progress';")
    op.execute("ALTER TYPE interaction_status ADD VALUE 'late';")

def downgrade():
    pass  # enum removal is complex, skip for now