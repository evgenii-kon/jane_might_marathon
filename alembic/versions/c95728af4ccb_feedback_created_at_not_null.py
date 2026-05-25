"""feedback created_at not null

Revision ID: c95728af4ccb
Revises: 4be51a4c71ca
Create Date: 2026-05-25 08:54:00.878183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c95728af4ccb'
down_revision: Union[str, Sequence[str], None] = '4be51a4c71ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE feedback SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    
    op.alter_column('feedback', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=False,
                    server_default=sa.func.now())


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('feedback', 'created_at',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=True,
                    server_default=None)


