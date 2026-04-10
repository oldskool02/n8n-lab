"""add follow up fields

Revision ID: d98b5a7adac4
Revises: 7ee4b910820c
Create Date: 2026-03-25 08:03:27.915448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd98b5a7adac4'
down_revision: Union[str, Sequence[str], None] = '7ee4b910820c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create enum if not exists
    interaction_status = postgresql.ENUM(
        'pending',
        'in_progress',
        'late',
        'completed',
        name='interaction_status'
    )
    interaction_status.create(op.get_bind(), checkfirst=True)

    # Alter column to use enum
    op.alter_column(
        'interactions',
        'status',
        type_=interaction_status,
        existing_type=sa.TEXT(),
        nullable=True
    )

    # Index
    op.drop_index(op.f('idx_follow_up_status'), table_name='interactions')
    op.create_index(
        'idx_follow_up_status',
        'interactions',
        ['follow_up_date'],
        unique=False,
        postgresql_where=sa.text("status = 'pending'")
    )

def downgrade():
    op.drop_index('idx_follow_up_status', table_name='interactions')

    op.alter_column(
        'interactions',
        'status',
        type_=sa.TEXT(),
        existing_type=postgresql.ENUM(name='interaction_status'),
    )

    postgresql.ENUM(name='interaction_status').drop(op.get_bind(), checkfirst=True)