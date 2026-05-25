"""change_to_timestamptz

Revision ID: 4be51a4c71ca
Revises: 815285deb500
Create Date: 2026-05-24 17:08:44.813384

"""
from alembic import op
import sqlalchemy as sa

revision = '4be51a4c71ca'
down_revision = '815285deb500'
branch_labels = None
depends_on = None

def upgrade():
    # feedback
    op.alter_column('feedback', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(timezone=False),
                    existing_nullable=True)

    # user_word_progress
    op.alter_column('user_word_progress', 'last_reviewed_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(timezone=False),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'next_review_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(timezone=False),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'created_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(timezone=False),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'updated_at',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime(timezone=False),
                    existing_nullable=True)

def downgrade():
    # откат
    op.alter_column('feedback', 'created_at',
                    type_=sa.DateTime(timezone=False),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=True)

    op.alter_column('user_word_progress', 'last_reviewed_at',
                    type_=sa.DateTime(timezone=False),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'next_review_at',
                    type_=sa.DateTime(timezone=False),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'created_at',
                    type_=sa.DateTime(timezone=False),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=True)
    op.alter_column('user_word_progress', 'updated_at',
                    type_=sa.DateTime(timezone=False),
                    existing_type=sa.DateTime(timezone=True),
                    existing_nullable=True)