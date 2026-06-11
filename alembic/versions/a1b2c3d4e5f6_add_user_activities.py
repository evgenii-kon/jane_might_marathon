"""add user_activities table

Revision ID: a1b2c3d4e5f6
Revises: f9c3c32aa529
Create Date: 2026-06-11 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f9c3c32aa529"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("activity_count", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_user_activity_date"),
    )
    op.create_index("ix_user_activities_user_id", "user_activities", ["user_id"], unique=False)
    op.create_index("ix_user_activities_date", "user_activities", ["date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_user_activities_date", table_name="user_activities")
    op.drop_index("ix_user_activities_user_id", table_name="user_activities")
    op.drop_table("user_activities")
