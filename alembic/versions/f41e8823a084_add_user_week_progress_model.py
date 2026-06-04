"""add user_week_progress model

Revision ID: f41e8823a084
Revises: e2e74f665c91
Create Date: 2026-05-15 18:26:27.642415

"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f41e8823a084"
down_revision: Union[str, Sequence[str], None] = "e2e74f665c91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_week_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('week_id', sa.Integer(), sa.ForeignKey('weeks.id'), nullable=True),
        sa.Column('opens_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_week_progress')
