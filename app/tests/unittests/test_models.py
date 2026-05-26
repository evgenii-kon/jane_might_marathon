"""
Async тесты моделей SQLAlchemy.
Проверяем, что ORM-объекты корректно создаются, сохраняются
и enforcing-ограничения (unique, FK) работают.
"""

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.week import Week
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.models.user_lesson_progress import UserLessonProgress
from app.models.user_exercise_progress import UserExerciseProgress
from app.models.user_week_progress import UserWeekProgress
from app.models.user_word_progress import UserWordProgress
from app.models.word import Word


# ---------------------------------------------------------------------------
# Вспомогательные хелперы
# ---------------------------------------------------------------------------

async def _make_user(session, email="u@test.com", name="User", pw="hash") -> User:
    user = User(email=email, name=name, password_hash=pw)
    session.add(user)
    await session.flush()
    return user


async def _make_week(session, slug="wk", number=99) -> Week:
    week = Week(
        slug=slug,
        short_description="short desc",
        long_description="long description here",
        number=number,
        target_words_count=10,
        target_exercises_count=5,
    )
    session.add(week)
    await session.flush()
    return week


async def _make_lesson(session, week_id, name="Lesson", order=1) -> Lesson:
    lesson = Lesson(
        name=name,
        week_id=week_id,
        order_in_week=order,
        content_html="<p>content</p>",
    )
    session.add(lesson)
    await session.flush()
    return lesson


# ---------------------------------------------------------------------------
# TestUserModel
# ---------------------------------------------------------------------------

class TestUserModel:

    async def test_create_user_basic(self, db_session):
        user = User(email="basic@test.com", name="Basic User", password_hash="hash123")
        db_session.add(user)
        await db_session.flush()

        result = await db_session.execute(
            select(User).where(User.email == "basic@test.com")
        )
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id is not None
        assert found.name == "Basic User"

    async def test_user_email_unique_constraint(self, db_session):
        user1 = User(email="dup@test.com", name="U1", password_hash="h1")
        user2 = User(email="dup@test.com", name="U2", password_hash="h2")
        db_session.add(user1)
        await db_session.flush()
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_user_optional_telegram(self, db_session):
        user = User(email="tg@test.com", name="TG User", password_hash="h", telegram="@handle")
        db_session.add(user)
        await db_session.flush()

        result = await db_session.execute(select(User).where(User.id == user.id))
        found = result.scalar_one()
        assert found.telegram == "@handle"

    async def test_user_telegram_nullable(self, db_session):
        user = User(email="notg@test.com", name="No TG", password_hash="h")
        db_session.add(user)
        await db_session.flush()
        assert user.telegram is None

    async def test_user_is_admin_default_false(self, db_session):
        user = User(email="admin@test.com", name="Admin", password_hash="h")
        db_session.add(user)
        await db_session.flush()
        assert user.is_admin is False

    async def test_user_created_at_auto(self, db_session):
        """created_at выставляется сервером автоматически."""
        user = User(email="time@test.com", name="Time", password_hash="h")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        # После commit + refresh created_at должен быть заполнен
        assert user.created_at is not None


# ---------------------------------------------------------------------------
# TestWeekModel
# ---------------------------------------------------------------------------

class TestWeekModel:

    async def test_create_week(self, db_session):
        week = await _make_week(db_session, slug="wk-model-1", number=50)
        assert week.id is not None
        assert week.slug == "wk-model-1"
        assert week.number == 50

    async def test_week_slug_unique(self, db_session):
        await _make_week(db_session, slug="same-slug", number=51)
        with pytest.raises(IntegrityError):
            await _make_week(db_session, slug="same-slug", number=52)

    async def test_week_number_unique(self, db_session):
        await _make_week(db_session, slug="wk-n1", number=53)
        with pytest.raises(IntegrityError):
            await _make_week(db_session, slug="wk-n2", number=53)


# ---------------------------------------------------------------------------
# TestLessonModel
# ---------------------------------------------------------------------------

class TestLessonModel:

    async def test_create_lesson(self, db_session):
        week = await _make_week(db_session, slug="lesson-wk", number=60)
        lesson = await _make_lesson(db_session, week.id, name="Model Lesson")
        assert lesson.id is not None
        assert lesson.week_id == week.id

    async def test_lesson_name_unique(self, db_session):
        week = await _make_week(db_session, slug="ln-wk", number=61)
        await _make_lesson(db_session, week.id, name="Unique Lesson Name")
        with pytest.raises(IntegrityError):
            await _make_lesson(db_session, week.id, name="Unique Lesson Name", order=2)


# ---------------------------------------------------------------------------
# TestExerciseModel
# ---------------------------------------------------------------------------

class TestExerciseModel:

    async def test_create_exercise(self, db_session):
        week = await _make_week(db_session, slug="ex-wk", number=62)
        lesson = await _make_lesson(db_session, week.id, name="Ex Lesson")
        exercise = Exercise(
            lesson_id=lesson.id,
            question_description="Pick the right one",
            question_text="apple",
            option_1="яблоко",
            option_2="апельсин",
            option_3="банан",
            option_4="груша",
            correct_answer=1,
            explanation="apple = яблоко",
            order_in_lesson=1,
        )
        db_session.add(exercise)
        await db_session.flush()
        assert exercise.id is not None
        assert exercise.correct_answer == 1
        assert exercise.lesson_id == lesson.id


# ---------------------------------------------------------------------------
# TestUserLessonProgressModel
# ---------------------------------------------------------------------------

class TestUserLessonProgressModel:

    async def test_create_lesson_progress(self, db_session):
        week = await _make_week(db_session, slug="ulp-wk", number=63)
        lesson = await _make_lesson(db_session, week.id, name="ULP Lesson")
        user = await _make_user(db_session, email="ulp@test.com")

        progress = UserLessonProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            is_started=True,
            is_completed=False,
        )
        db_session.add(progress)
        await db_session.flush()

        assert progress.id is not None
        assert progress.user_id == user.id
        assert progress.is_started is True
        assert progress.is_completed is False


# ---------------------------------------------------------------------------
# TestUserExerciseProgressModel
# ---------------------------------------------------------------------------

class TestUserExerciseProgressModel:

    async def test_create_exercise_progress(self, db_session):
        week = await _make_week(db_session, slug="uep-wk", number=64)
        lesson = await _make_lesson(db_session, week.id, name="UEP Lesson")
        user = await _make_user(db_session, email="uep@test.com")
        exercise = Exercise(
            lesson_id=lesson.id,
            question_description="q",
            question_text="t",
            option_1="a", option_2="b", option_3="c", option_4="d",
            correct_answer=1,
        )
        db_session.add(exercise)
        await db_session.flush()

        prog = UserExerciseProgress(
            user_id=user.id,
            exercise_id=exercise.id,
            is_completed=True,
        )
        db_session.add(prog)
        await db_session.flush()
        assert prog.id is not None
        assert prog.is_completed is True


# ---------------------------------------------------------------------------
# TestUserWeekProgressModel
# ---------------------------------------------------------------------------

class TestUserWeekProgressModel:

    async def test_create_week_progress(self, db_session):
        from datetime import datetime, timezone
        week = await _make_week(db_session, slug="uwp-wk", number=65)
        user = await _make_user(db_session, email="uwp@test.com")

        prog = UserWeekProgress(
            user_id=user.id,
            week_id=week.id,
            opens_at=datetime.now(timezone.utc),
            is_completed=False,
        )
        db_session.add(prog)
        await db_session.flush()
        assert prog.id is not None
        assert prog.is_completed is False


# ---------------------------------------------------------------------------
# TestUserWordProgressModel
# ---------------------------------------------------------------------------

class TestUserWordProgressModel:

    async def test_create_word_progress(self, db_session):
        from datetime import datetime, timezone
        user = await _make_user(db_session, email="uwrd@test.com")
        word = Word(hanzi="字", transcription="zì", translation="character")
        db_session.add(word)
        await db_session.flush()

        prog = UserWordProgress(
            user_id=user.id,
            word_id=word.id,
            mastery_level=0,
            next_review_at=datetime.now(timezone.utc),
        )
        db_session.add(prog)
        await db_session.flush()
        assert prog.id is not None
        assert prog.mastery_level == 0

    async def test_unique_user_word_constraint(self, db_session):
        from datetime import datetime, timezone
        user = await _make_user(db_session, email="uwrd2@test.com")
        word = Word(hanzi="好", transcription="hǎo", translation="good")
        db_session.add(word)
        await db_session.flush()

        p1 = UserWordProgress(
            user_id=user.id, word_id=word.id, mastery_level=0,
            next_review_at=datetime.now(timezone.utc),
        )
        db_session.add(p1)
        await db_session.flush()

        p2 = UserWordProgress(
            user_id=user.id, word_id=word.id, mastery_level=1,
            next_review_at=datetime.now(timezone.utc),
        )
        db_session.add(p2)
        with pytest.raises(IntegrityError):
            await db_session.flush()
