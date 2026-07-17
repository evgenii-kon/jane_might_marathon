"""add novel skip fields to user and novel_lines table

Revision ID: 7682ed89825e
Revises: 82dba1d753a0
Create Date: 2026-07-17 19:04:15.803433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7682ed89825e'
down_revision: Union[str, Sequence[str], None] = '82dba1d753a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('novel_skipped', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('novel_skipped_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('novel_skip_asked', sa.Boolean(), nullable=False, server_default='false'))

    op.create_table(
        'novel_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('character', sa.String(length=50), nullable=True),
        sa.Column('speaker', sa.String(length=100), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_novel_lines_lesson_id'), 'novel_lines', ['lesson_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_novel_lines_lesson_id'), table_name='novel_lines')
    op.drop_table('novel_lines')

    op.drop_column('users', 'novel_skip_asked')
    op.drop_column('users', 'novel_skipped_at')
    op.drop_column('users', 'novel_skipped')
