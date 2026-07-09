"""add_payment_tables

Revision ID: c13ddffea7d7
Revises: 1d4ed764890c
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c13ddffea7d7'
down_revision: Union[str, Sequence[str], None] = '1d4ed764890c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


plans_table = sa.table(
    "plans",
    sa.column("slug", sa.String),
    sa.column("name", sa.String),
    sa.column("price_kopecks", sa.Integer),
    sa.column("duration_days", sa.Integer),
    sa.column("features", postgresql.JSON),
    sa.column("is_active", sa.Boolean),
    sa.column("order", sa.Integer),
    sa.column("badge", sa.String),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_kopecks", sa.Integer(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("features", postgresql.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("badge", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"]
    )
    op.create_index(
        op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"]
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tinkoff_payment_id", sa.String(length=50), nullable=True),
        sa.Column("order_id", sa.String(length=100), nullable=False),
        sa.Column("amount_kopecks", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("payment_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tinkoff_payment_id"),
        sa.UniqueConstraint("order_id"),
    )
    op.create_index(
        op.f("ix_payments_subscription_id"), "payments", ["subscription_id"]
    )
    op.create_index(
        op.f("ix_payments_user_id"), "payments", ["user_id"]
    )

    op.bulk_insert(
        plans_table,
        [
            {
                "slug": "basic",
                "name": "Базовый",
                "price_kopecks": 199000,
                "duration_days": 90,
                "features": ["lessons", "exercises"],
                "is_active": True,
                "order": 1,
                "badge": None,
            },
            {
                "slug": "pro",
                "name": "Продвинутый",
                "price_kopecks": 349000,
                "duration_days": 90,
                "features": ["lessons", "exercises", "word_trainer", "grammar", "reading"],
                "is_active": True,
                "order": 2,
                "badge": "Популярный",
            },
            {
                "slug": "vip",
                "name": "VIP",
                "price_kopecks": 499000,
                "duration_days": 180,
                "features": ["lessons", "exercises", "word_trainer", "grammar", "reading", "idioms"],
                "is_active": True,
                "order": 3,
                "badge": None,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_subscription_id"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_subscriptions_plan_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_table("plans")
