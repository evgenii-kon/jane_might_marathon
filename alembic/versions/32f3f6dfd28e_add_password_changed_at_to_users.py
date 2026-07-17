"""add_password_changed_at_to_users

Revision ID: 32f3f6dfd28e
Revises: 9cad20b2a8f3
Create Date: 2026-07-17 20:29:39.702299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32f3f6dfd28e'
down_revision: Union[str, Sequence[str], None] = '9cad20b2a8f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'password_changed_at')
