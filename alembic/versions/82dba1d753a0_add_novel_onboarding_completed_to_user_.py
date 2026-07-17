"""add novel_onboarding_completed to user model

Revision ID: 82dba1d753a0
Revises: c13ddffea7d7
Create Date: 2026-07-17 17:25:36.755403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82dba1d753a0'
down_revision: Union[str, Sequence[str], None] = 'c13ddffea7d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('novel_onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'novel_onboarding_completed')
