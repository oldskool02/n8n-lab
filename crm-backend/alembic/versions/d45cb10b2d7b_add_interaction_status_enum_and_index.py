from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'd45cb10b2d7b'
down_revision = 'ad27b9348015'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create ENUM
    interaction_status = sa.Enum('pending', 'completed', name='interaction_status')
    interaction_status.create(op.get_bind(), checkfirst=True)

    # 2. Add follow_up_date FIRST
    op.add_column(
        'interactions',
        sa.Column('follow_up_date', sa.DateTime(timezone=True), nullable=True)
    )

    # 3. Add status column
    op.add_column(
        'interactions',
        sa.Column(
            'status',
            interaction_status,
            nullable=False,
            server_default='pending'
        )
    )

    # 4. Add completed_at
    op.add_column(
        'interactions',
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 5. NOW create index (column exists)
    op.create_index(
        'idx_follow_up_status',
        'interactions',
        ['follow_up_date', 'status']
    )


def downgrade():
    op.drop_index('idx_follow_up_status', table_name='interactions')

    op.drop_column('interactions', 'completed_at')
    op.drop_column('interactions', 'status')
    op.drop_column('interactions', 'follow_up_date')

    interaction_status = sa.Enum('pending', 'completed', name='interaction_status')
    interaction_status.drop(op.get_bind(), checkfirst=True)
