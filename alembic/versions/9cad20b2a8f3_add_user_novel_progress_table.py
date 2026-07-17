"""add user_novel_progress table

Revision ID: 9cad20b2a8f3
Revises: 7682ed89825e
Create Date: 2026-07-17 20:04:40.381500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cad20b2a8f3'
down_revision: Union[str, Sequence[str], None] = '7682ed89825e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_novel_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'lesson_id', name='uq_user_novel_progress'),
    )
    op.create_index(op.f('ix_user_novel_progress_user_id'), 'user_novel_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_novel_progress_lesson_id'), 'user_novel_progress', ['lesson_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_novel_progress_lesson_id'), table_name='user_novel_progress')
    op.drop_index(op.f('ix_user_novel_progress_user_id'), table_name='user_novel_progress')
    op.drop_table('user_novel_progress')
