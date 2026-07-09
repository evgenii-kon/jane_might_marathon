"""universal_exercise_types

Revision ID: 078409b22a89
Revises: 4e0f3379df50
Create Date: 2026-07-09 10:18:38.591374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '078409b22a89'
down_revision: Union[str, Sequence[str], None] = '4e0f3379df50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("exercises", sa.Column("type", sa.String(length=50), nullable=True))
    op.add_column("exercises", sa.Column("config", sa.JSON(), nullable=True))

    # Backfill existing rows into the new "quiz" config shape.
    # correct_answer was 1-based in the old schema, config["correct"] is 0-based.
    op.execute(
        """
        UPDATE exercises
        SET type = 'quiz',
            config = json_build_object(
                'word_id', NULL,
                'options', json_build_array(option_1, option_2, option_3, option_4),
                'correct', correct_answer - 1
            )
        """
    )

    op.alter_column("exercises", "type", nullable=False)
    op.alter_column("exercises", "config", nullable=False)
    op.alter_column("exercises", "question_text", nullable=True)

    op.drop_column("exercises", "question_description")
    op.drop_column("exercises", "option_1")
    op.drop_column("exercises", "option_2")
    op.drop_column("exercises", "option_3")
    op.drop_column("exercises", "option_4")
    op.drop_column("exercises", "correct_answer")

    op.alter_column("exercises", "lesson_id", nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("exercises", sa.Column("question_description", sa.String(length=255), nullable=True))
    op.add_column("exercises", sa.Column("option_1", sa.String(length=255), nullable=True))
    op.add_column("exercises", sa.Column("option_2", sa.String(length=255), nullable=True))
    op.add_column("exercises", sa.Column("option_3", sa.String(length=255), nullable=True))
    op.add_column("exercises", sa.Column("option_4", sa.String(length=255), nullable=True))
    op.add_column("exercises", sa.Column("correct_answer", sa.Integer(), nullable=True))

    # Best-effort restore for "quiz" rows only — other exercise types have no
    # equivalent representation in the old fixed-4-option schema.
    op.execute(
        """
        UPDATE exercises
        SET question_description = COALESCE(question_text, ''),
            option_1 = config->'options'->>0,
            option_2 = config->'options'->>1,
            option_3 = config->'options'->>2,
            option_4 = config->'options'->>3,
            correct_answer = (config->>'correct')::int + 1
        WHERE type = 'quiz'
        """
    )

    op.execute("DELETE FROM exercises WHERE type != 'quiz'")
    op.execute("UPDATE exercises SET question_description = '' WHERE question_description IS NULL")
    op.execute("UPDATE exercises SET option_1 = '' WHERE option_1 IS NULL")
    op.execute("UPDATE exercises SET option_2 = '' WHERE option_2 IS NULL")
    op.execute("UPDATE exercises SET option_3 = '' WHERE option_3 IS NULL")
    op.execute("UPDATE exercises SET option_4 = '' WHERE option_4 IS NULL")
    op.execute("UPDATE exercises SET correct_answer = 1 WHERE correct_answer IS NULL")
    op.execute("UPDATE exercises SET lesson_id = (SELECT id FROM lessons ORDER BY id LIMIT 1) WHERE lesson_id IS NULL")

    op.execute("UPDATE exercises SET question_text = '' WHERE question_text IS NULL")
    op.alter_column("exercises", "question_text", nullable=False)
    op.alter_column("exercises", "lesson_id", nullable=False)
    op.alter_column("exercises", "question_description", nullable=False)
    op.alter_column("exercises", "option_1", nullable=False)
    op.alter_column("exercises", "option_2", nullable=False)
    op.alter_column("exercises", "option_3", nullable=False)
    op.alter_column("exercises", "option_4", nullable=False)
    op.alter_column("exercises", "correct_answer", nullable=False)

    op.drop_column("exercises", "config")
    op.drop_column("exercises", "type")
