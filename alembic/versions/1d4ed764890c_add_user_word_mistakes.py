"""add_user_word_mistakes

Revision ID: 1d4ed764890c
Revises: 078409b22a89
Create Date: 2026-07-09 11:14:40.132870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d4ed764890c'
down_revision: Union[str, Sequence[str], None] = '078409b22a89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_word_mistakes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("word_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["word_id"], ["words.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "word_id", name="uq_user_word_mistake"),
    )
    op.create_index(
        op.f("ix_user_word_mistakes_user_id"), "user_word_mistakes", ["user_id"]
    )
    op.create_index(
        op.f("ix_user_word_mistakes_word_id"), "user_word_mistakes", ["word_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_word_mistakes_word_id"), table_name="user_word_mistakes")
    op.drop_index(op.f("ix_user_word_mistakes_user_id"), table_name="user_word_mistakes")
    op.drop_table("user_word_mistakes")
