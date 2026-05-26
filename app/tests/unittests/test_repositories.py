"""
Async тесты всех репозиториев.
Каждый тест получает изолированную async-сессию (rollback после теста).
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.week import Week
from app.models.lesson import Lesson
from app.models.word import Word
from app.models.exercise import Exercise
from app.models.article import Article
from app.models.feedback import FeedBack
from app.models.user_week_progress import UserWeekProgress
from app.models.user_word_progress import UserWordProgress

from app.repositories.user_repository import UserRepository
from app.repositories.week_repository import WeekRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.word_repository import WordRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.article_repository import ArticleRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.user_lesson_progress_repository import UserLessonProgressRepository
from app.repositories.user_exercise_progress_repository import UserExerciseProgressRepository
from app.repositories.user_week_progress_repository import UserWeekProgressRepository
from app.repositories.user_word_progress_repository import UserWordProgressRepository
from app.repositories.lesson_word_association_repository import LessonWordAssociationRepository

from app.schemas.user import UserUpdate
from app.schemas.week import WeekCreate
from app.schemas.lesson import LessonCreate
from app.schemas.exercise import ExerciseCreate
from app.schemas.article import ArticleCreate
from app.schemas.feedback import FeedbackCreate


# ---------------------------------------------------------------------------
# Хелперы для создания тестовых данных
# ---------------------------------------------------------------------------

async def _mk_user(s, email="u@r.com", name="Repo User", pw="hash") -> User:
    u = User(email=email, name=name, password_hash=pw)
    s.add(u)
    await s.commit()
    return u


async def _mk_week(s, slug="rw", number=200) -> Week:
    w = Week(
        slug=slug,
        short_description="short description",
        long_description="long description here",
        number=number,
        target_words_count=10,
        target_exercises_count=5,
    )
    s.add(w)
    await s.commit()
    return w


async def _mk_lesson(s, week_id, name="Repo Lesson", order=1) -> Lesson:
    ls = Lesson(name=name, week_id=week_id, order_in_week=order, content_html="<p>c</p>")
    s.add(ls)
    await s.commit()
    return ls


async def _mk_word(s, hanzi="字", transcription="zì", translation="char") -> Word:
    w = Word(hanzi=hanzi, transcription=transcription, translation=translation)
    s.add(w)
    await s.commit()
    return w


async def _mk_exercise(s, lesson_id, order=1) -> Exercise:
    e = Exercise(
        lesson_id=lesson_id,
        question_description="desc",
        question_text="q",
        option_1="a", option_2="b", option_3="c", option_4="d",
        correct_answer=1,
        order_in_lesson=order,
    )
    s.add(e)
    await s.commit()
    return e


# ---------------------------------------------------------------------------
# TestUserRepository
# ---------------------------------------------------------------------------

class TestUserRepository:

    async def test_get_all(self, db_session):
        repo = UserRepository(db_session)
        u1 = await _mk_user(db_session, email="ua1@r.com", name="UA1")
        u2 = await _mk_user(db_session, email="ua2@r.com", name="UA2")
        users = await repo.get_all()
        emails = [u.email for u in users]
        assert "ua1@r.com" in emails
        assert "ua2@r.com" in emails

    async def test_get_by_id_found(self, db_session):
        repo = UserRepository(db_session)
        u = await _mk_user(db_session, email="uid@r.com")
        found = await repo.get_by_id(u.id)
        assert found is not None
        assert found.id == u.id

    async def test_get_by_id_not_found(self, db_session):
        repo = UserRepository(db_session)
        found = await repo.get_by_id(999_999)
        assert found is None

    async def test_get_by_email_found(self, db_session):
        repo = UserRepository(db_session)
        u = await _mk_user(db_session, email="em@r.com")
        found = await repo.get_by_email("em@r.com")
        assert found is not None
        assert found.id == u.id

    async def test_get_by_email_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert await repo.get_by_email("nobody@r.com") is None

    async def test_get_by_name_found(self, db_session):
        repo = UserRepository(db_session)
        u = await _mk_user(db_session, email="nm@r.com", name="RepoName")
        found = await repo.get_by_name("RepoName")
        assert found is not None
        assert found.id == u.id

    async def test_create(self, db_session):
        repo = UserRepository(db_session)
        data = {"email": "cr@r.com", "name": "Created", "password_hash": "h"}
        u = await repo.create(data)
        assert u.id is not None
        assert u.email == "cr@r.com"

    async def test_delete_found(self, db_session):
        repo = UserRepository(db_session)
        u = await _mk_user(db_session, email="del@r.com")
        result = await repo.delete(u.id)
        assert result is True
        assert await repo.get_by_id(u.id) is None

    async def test_delete_not_found(self, db_session):
        repo = UserRepository(db_session)
        result = await repo.delete(999_999)
        assert result is False

    async def test_update(self, db_session):
        repo = UserRepository(db_session)
        u = await _mk_user(db_session, email="upd@r.com")
        updated = await repo.update(u.id, {"name": "NewName"})
        assert updated is not None
        assert updated.name == "NewName"

    async def test_update_not_found(self, db_session):
        repo = UserRepository(db_session)
        result = await repo.update(999_999, {"name": "X"})
        assert result is None


# ---------------------------------------------------------------------------
# TestWeekRepository
# ---------------------------------------------------------------------------

class TestWeekRepository:

    async def test_get_all(self, db_session):
        repo = WeekRepository(db_session)
        w1 = await _mk_week(db_session, slug="wr-1", number=201)
        w2 = await _mk_week(db_session, slug="wr-2", number=202)
        weeks = await repo.get_all()
        slugs = [w.slug for w in weeks]
        assert "wr-1" in slugs
        assert "wr-2" in slugs

    async def test_get_by_id(self, db_session):
        repo = WeekRepository(db_session)
        w = await _mk_week(db_session, slug="wid", number=203)
        found = await repo.get_by_id(w.id)
        assert found is not None
        assert found.slug == "wid"

    async def test_get_by_id_not_found(self, db_session):
        repo = WeekRepository(db_session)
        assert await repo.get_by_id(999_999) is None

    async def test_get_by_slug(self, db_session):
        repo = WeekRepository(db_session)
        w = await _mk_week(db_session, slug="by-slug", number=204)
        found = await repo.get_by_slug("by-slug")
        assert found is not None
        assert found.id == w.id

    async def test_get_by_number(self, db_session):
        repo = WeekRepository(db_session)
        w = await _mk_week(db_session, slug="by-num", number=205)
        found = await repo.get_by_number(205)
        assert found is not None
        assert found.id == w.id

    async def test_create(self, db_session):
        repo = WeekRepository(db_session)
        data = WeekCreate(
            slug="new-week-r",
            short_description="short desc here",
            long_description="very long description indeed",
            number=46,
            target_words_count=20,
            target_exercises_count=10,
        )
        w = await repo.create(data)
        assert w.id is not None
        assert w.slug == "new-week-r"

    async def test_update(self, db_session):
        repo = WeekRepository(db_session)
        w = await _mk_week(db_session, slug="upd-wk", number=207)
        updated = await repo.update(w.id, {"short_description": "updated short desc"})
        assert updated is not None
        assert updated.short_description == "updated short desc"

    async def test_delete(self, db_session):
        repo = WeekRepository(db_session)
        w = await _mk_week(db_session, slug="del-wk", number=208)
        assert await repo.delete(w.id) is True
        assert await repo.get_by_id(w.id) is None


# ---------------------------------------------------------------------------
# TestLessonRepository
# ---------------------------------------------------------------------------

class TestLessonRepository:

    async def test_get_all(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lr-wk", number=209)
        await _mk_lesson(db_session, w.id, name="LR Lesson 1", order=1)
        await _mk_lesson(db_session, w.id, name="LR Lesson 2", order=2)
        lessons = await repo.get_all()
        names = [l.name for l in lessons]
        assert "LR Lesson 1" in names
        assert "LR Lesson 2" in names

    async def test_get_by_id(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrid-wk", number=210)
        ls = await _mk_lesson(db_session, w.id, name="LR ByID")
        found = await repo.get_by_id(ls.id)
        assert found is not None
        assert found.name == "LR ByID"

    async def test_get_by_id_not_found(self, db_session):
        repo = LessonRepository(db_session)
        assert await repo.get_by_id(999_999) is None

    async def test_get_by_name(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrn-wk", number=211)
        ls = await _mk_lesson(db_session, w.id, name="UniqueLRName")
        found = await repo.get_by_name("UniqueLRName")
        assert found is not None
        assert found.id == ls.id

    async def test_create(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrc-wk", number=212)
        data = LessonCreate(name="Created Lesson R", week_id=w.id, order_in_week=1, content_html="c")
        ls = await repo.create(data)
        assert ls.id is not None
        assert ls.week_id == w.id

    async def test_update(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lru-wk", number=213)
        ls = await _mk_lesson(db_session, w.id, name="LR Before")
        updated = await repo.update(ls.id, {"name": "LR After"})
        assert updated is not None
        assert updated.name == "LR After"

    async def test_delete(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrd-wk", number=214)
        ls = await _mk_lesson(db_session, w.id, name="LR Delete")
        assert await repo.delete(ls.id) is True
        assert await repo.get_by_id(ls.id) is None

    async def test_get_by_week_id(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrw-wk", number=215)
        await _mk_lesson(db_session, w.id, name="LRW 1", order=1)
        await _mk_lesson(db_session, w.id, name="LRW 2", order=2)
        lessons = await repo.get_by_week_id(w.id)
        assert len(lessons) == 2
        # Должны быть отсортированы по order_in_week
        assert lessons[0].order_in_week == 1
        assert lessons[1].order_in_week == 2

    async def test_get_count(self, db_session):
        repo = LessonRepository(db_session)
        w = await _mk_week(db_session, slug="lrc2-wk", number=216)
        before = await repo.get_count()
        await _mk_lesson(db_session, w.id, name="LR Count Test")
        after = await repo.get_count()
        assert after == before + 1


# ---------------------------------------------------------------------------
# TestWordRepository
# ---------------------------------------------------------------------------

class TestWordRepository:

    async def test_get_all(self, db_session):
        repo = WordRepository(db_session)
        w1 = await _mk_word(db_session, hanzi="甲", transcription="jiǎ", translation="first")
        w2 = await _mk_word(db_session, hanzi="乙", transcription="yǐ", translation="second")
        words = await repo.get_all()
        hanzi_list = [w.hanzi for w in words]
        assert "甲" in hanzi_list
        assert "乙" in hanzi_list

    async def test_get_by_id(self, db_session):
        repo = WordRepository(db_session)
        w = await _mk_word(db_session, hanzi="独", translation="alone")
        found = await repo.get_by_id(w.id)
        assert found is not None
        assert found.hanzi == "独"

    async def test_get_by_id_not_found(self, db_session):
        repo = WordRepository(db_session)
        assert await repo.get_by_id(999_999) is None

    async def test_get_by_ids(self, db_session):
        repo = WordRepository(db_session)
        w1 = await _mk_word(db_session, hanzi="一", translation="one")
        w2 = await _mk_word(db_session, hanzi="二", translation="two")
        found = await repo.get_by_ids([w1.id, w2.id])
        ids = [w.id for w in found]
        assert w1.id in ids
        assert w2.id in ids

    async def test_get_by_ids_empty(self, db_session):
        repo = WordRepository(db_session)
        assert await repo.get_by_ids([]) == []

    async def test_create(self, db_session):
        repo = WordRepository(db_session)
        data = {"hanzi": "新", "transcription": "xīn", "translation": "new"}
        w = await repo.create(data)
        assert w.id is not None
        assert w.hanzi == "新"

    async def test_update(self, db_session):
        repo = WordRepository(db_session)
        w = await _mk_word(db_session, hanzi="旧", translation="old")
        updated = await repo.update(w.id, {"translation": "ancient"})
        assert updated is not None
        assert updated.translation == "ancient"

    async def test_delete(self, db_session):
        repo = WordRepository(db_session)
        w = await _mk_word(db_session, hanzi="删", translation="delete")
        assert await repo.delete(w.id) is True
        assert await repo.get_by_id(w.id) is None

    async def test_add_to_lesson_and_get_by_lesson(self, db_session):
        repo = WordRepository(db_session)
        wk = await _mk_week(db_session, slug="wr-wk", number=217)
        ls = await _mk_lesson(db_session, wk.id, name="WR Lesson")
        word = await _mk_word(db_session, hanzi="课", translation="lesson")
        assert await repo.add_to_lesson(word.id, ls.id) is True
        words = await repo.get_by_lesson(ls.id)
        assert len(words) == 1
        assert words[0].hanzi == "课"

    async def test_add_to_lesson_idempotent(self, db_session):
        """Повторное добавление не создаёт дублей."""
        repo = WordRepository(db_session)
        wk = await _mk_week(db_session, slug="wr-idem-wk", number=218)
        ls = await _mk_lesson(db_session, wk.id, name="WR Idem Lesson")
        word = await _mk_word(db_session, hanzi="幂", translation="idempotent")
        await repo.add_to_lesson(word.id, ls.id)
        await repo.add_to_lesson(word.id, ls.id)  # второй раз
        words = await repo.get_by_lesson(ls.id)
        assert len(words) == 1

    async def test_remove_from_lesson(self, db_session):
        repo = WordRepository(db_session)
        wk = await _mk_week(db_session, slug="wr-rm-wk", number=219)
        ls = await _mk_lesson(db_session, wk.id, name="WR Remove Lesson")
        word = await _mk_word(db_session, hanzi="移", translation="move")
        await repo.add_to_lesson(word.id, ls.id)
        assert await repo.remove_from_lesson(word.id, ls.id) is True
        assert len(await repo.get_by_lesson(ls.id)) == 0

    async def test_get_lesson_ids(self, db_session):
        repo = WordRepository(db_session)
        wk = await _mk_week(db_session, slug="wr-li-wk", number=220)
        ls = await _mk_lesson(db_session, wk.id, name="WR LessonIds")
        word = await _mk_word(db_session, hanzi="联", translation="linked")
        await repo.add_to_lesson(word.id, ls.id)
        lesson_ids = await repo.get_lesson_ids(word.id)
        assert ls.id in lesson_ids


# ---------------------------------------------------------------------------
# TestExerciseRepository
# ---------------------------------------------------------------------------

class TestExerciseRepository:

    async def test_get_all(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="er-wk", number=221)
        ls = await _mk_lesson(db_session, wk.id, name="ER Lesson")
        e1 = await _mk_exercise(db_session, ls.id, order=1)
        e2 = await _mk_exercise(db_session, ls.id, order=2)
        exercises = await repo.get_all()
        ids = [e.id for e in exercises]
        assert e1.id in ids
        assert e2.id in ids

    async def test_get_by_id(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="erbid-wk", number=222)
        ls = await _mk_lesson(db_session, wk.id, name="ER BID Lesson")
        e = await _mk_exercise(db_session, ls.id)
        found = await repo.get_by_id(e.id)
        assert found is not None
        assert found.id == e.id

    async def test_get_by_id_not_found(self, db_session):
        repo = ExerciseRepository(db_session)
        assert await repo.get_by_id(999_999) is None

    async def test_get_by_lesson(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="erbl-wk", number=223)
        ls = await _mk_lesson(db_session, wk.id, name="ER BL Lesson")
        e1 = await _mk_exercise(db_session, ls.id, order=2)
        e2 = await _mk_exercise(db_session, ls.id, order=1)
        exercises = await repo.get_by_lesson(ls.id)
        assert len(exercises) == 2
        # Отсортированы по order_in_lesson
        assert exercises[0].order_in_lesson == 1
        assert exercises[1].order_in_lesson == 2

    async def test_get_count_by_lesson(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="ercnt-wk", number=224)
        ls = await _mk_lesson(db_session, wk.id, name="ER Count Lesson")
        before = await repo.get_count_by_lesson(ls.id)
        await _mk_exercise(db_session, ls.id)
        after = await repo.get_count_by_lesson(ls.id)
        assert after == before + 1

    async def test_create(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="erc-wk", number=225)
        ls = await _mk_lesson(db_session, wk.id, name="ER Create Lesson")
        data = ExerciseCreate(
            lesson_id=ls.id,
            question_description="d",
            question_text="t",
            option_1="a", option_2="b", option_3="c", option_4="d",
            correct_answer=2,
            order_in_lesson=1,
        )
        e = await repo.create(data)
        assert e.id is not None
        assert e.correct_answer == 2

    async def test_update(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="eru-wk", number=226)
        ls = await _mk_lesson(db_session, wk.id, name="ER Update Lesson")
        e = await _mk_exercise(db_session, ls.id)
        updated = await repo.update(e.id, {"correct_answer": 3})
        assert updated is not None
        assert updated.correct_answer == 3

    async def test_delete(self, db_session):
        repo = ExerciseRepository(db_session)
        wk = await _mk_week(db_session, slug="erd-wk", number=227)
        ls = await _mk_lesson(db_session, wk.id, name="ER Delete Lesson")
        e = await _mk_exercise(db_session, ls.id)
        assert await repo.delete(e.id) is True
        assert await repo.get_by_id(e.id) is None


# ---------------------------------------------------------------------------
# TestArticleRepository
# ---------------------------------------------------------------------------

class TestArticleRepository:

    async def test_create(self, db_session):
        repo = ArticleRepository(db_session)
        data = ArticleCreate(
            name="Test Article",
            slug="test-ar",
            description="Short desc",
            text="Full text of the article",
            images=["/img1.jpg"],
        )
        a = await repo.create(data)
        assert a.id is not None
        assert a.slug == "test-ar"

    async def test_get_by_id(self, db_session):
        repo = ArticleRepository(db_session)
        art = Article(name="AR Get", slug="ar-get", description="d", text="t", images=[])
        db_session.add(art)
        await db_session.commit()
        found = await repo.get_by_id(art.id)
        assert found is not None
        assert found.name == "AR Get"

    async def test_get_by_id_not_found(self, db_session):
        repo = ArticleRepository(db_session)
        assert await repo.get_by_id(999_999) is None

    async def test_get_by_slug(self, db_session):
        repo = ArticleRepository(db_session)
        art = Article(name="AR Slug", slug="ar-slug-test", description="d", text="t", images=[])
        db_session.add(art)
        await db_session.commit()
        found = await repo.get_by_slug("ar-slug-test")
        assert found is not None
        assert found.id == art.id

    async def test_get_all(self, db_session):
        repo = ArticleRepository(db_session)
        art1 = Article(name="A1", slug="ar-a1", description="d1", text="t1", images=[])
        art2 = Article(name="A2", slug="ar-a2", description="d2", text="t2", images=[])
        db_session.add_all([art1, art2])
        await db_session.commit()
        articles = await repo.get_all()
        slugs = [a.slug for a in articles]
        assert "ar-a1" in slugs
        assert "ar-a2" in slugs

    async def test_update(self, db_session):
        repo = ArticleRepository(db_session)
        art = Article(name="AR Old", slug="ar-upd", description="old", text="t", images=[])
        db_session.add(art)
        await db_session.commit()
        updated = await repo.update(art.id, {"name": "AR New", "description": "new"})
        assert updated is not None
        assert updated.name == "AR New"

    async def test_delete(self, db_session):
        repo = ArticleRepository(db_session)
        art = Article(name="AR Del", slug="ar-del", description="d", text="t", images=[])
        db_session.add(art)
        await db_session.commit()
        assert await repo.delete(art.id) is True
        assert await repo.get_by_id(art.id) is None


# ---------------------------------------------------------------------------
# TestFeedbackRepository
# ---------------------------------------------------------------------------

class TestFeedbackRepository:

    async def test_create(self, db_session):
        repo = FeedbackRepository(db_session)
        user = await _mk_user(db_session, email="fb@r.com")
        data = FeedbackCreate(text="Great app!")
        fb = await repo.create(user.id, data)
        assert fb.id is not None
        assert fb.text == "Great app!"
        assert fb.user_id == user.id

    async def test_get_by_user(self, db_session):
        repo = FeedbackRepository(db_session)
        user = await _mk_user(db_session, email="fb2@r.com")
        data1 = FeedbackCreate(text="Feedback 1")
        data2 = FeedbackCreate(text="Feedback 2")
        await repo.create(user.id, data1)
        await repo.create(user.id, data2)
        fbs = await repo.get_by_user(user.id)
        assert len(fbs) == 2

    async def test_get_all(self, db_session):
        repo = FeedbackRepository(db_session)
        user = await _mk_user(db_session, email="fb3@r.com")
        await repo.create(user.id, FeedbackCreate(text="FB all"))
        fbs = await repo.get_all()
        assert len(fbs) >= 1

    async def test_get_by_id(self, db_session):
        repo = FeedbackRepository(db_session)
        user = await _mk_user(db_session, email="fb4@r.com")
        fb = await repo.create(user.id, FeedbackCreate(text="FB get"))
        found = await repo.get_by_id(fb.id)
        assert found is not None
        assert found.text == "FB get"

    async def test_delete(self, db_session):
        repo = FeedbackRepository(db_session)
        user = await _mk_user(db_session, email="fb5@r.com")
        fb = await repo.create(user.id, FeedbackCreate(text="FB del"))
        assert await repo.delete(fb.id) is True
        assert await repo.get_by_id(fb.id) is None


# ---------------------------------------------------------------------------
# TestUserLessonProgressRepository
# ---------------------------------------------------------------------------

class TestUserLessonProgressRepository:

    async def test_mark_started_new(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp1@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk1", number=230)
        ls = await _mk_lesson(db_session, wk.id, name="ULP Started")
        prog = await repo.mark_started(user.id, ls.id)
        assert prog.is_started is True
        assert prog.is_completed is False

    async def test_mark_started_existing(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp2@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk2", number=231)
        ls = await _mk_lesson(db_session, wk.id, name="ULP Started Exist")
        await repo.mark_started(user.id, ls.id)
        prog = await repo.mark_started(user.id, ls.id)
        assert prog.is_started is True

    async def test_mark_completed_new(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp3@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk3", number=232)
        ls = await _mk_lesson(db_session, wk.id, name="ULP Completed")
        prog = await repo.mark_completed(user.id, ls.id)
        assert prog.is_completed is True
        assert prog.completed_at is not None

    async def test_mark_completed_existing(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp4@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk4", number=233)
        ls = await _mk_lesson(db_session, wk.id, name="ULP Completed Exist")
        await repo.mark_started(user.id, ls.id)
        prog = await repo.mark_completed(user.id, ls.id)
        assert prog.is_completed is True

    async def test_is_started_and_is_completed(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp5@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk5", number=234)
        ls = await _mk_lesson(db_session, wk.id, name="ULP IsStarted")
        assert await repo.is_started(user.id, ls.id) is False
        await repo.mark_started(user.id, ls.id)
        assert await repo.is_started(user.id, ls.id) is True
        assert await repo.is_completed(user.id, ls.id) is False
        await repo.mark_completed(user.id, ls.id)
        assert await repo.is_completed(user.id, ls.id) is True

    async def test_get_completed_lesson_ids(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp6@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk6", number=235)
        ls1 = await _mk_lesson(db_session, wk.id, name="ULP CID1", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="ULP CID2", order=2)
        await repo.mark_completed(user.id, ls1.id)
        ids = await repo.get_completed_lesson_ids(user.id)
        assert ls1.id in ids
        assert ls2.id not in ids

    async def test_get_completed_count_by_user(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp7@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk7", number=236)
        ls = await _mk_lesson(db_session, wk.id, name="ULP CCnt User")
        assert await repo.get_completed_count_by_user(user.id) == 0
        await repo.mark_completed(user.id, ls.id)
        assert await repo.get_completed_count_by_user(user.id) == 1

    async def test_get_completed_count_by_week(self, db_session):
        repo = UserLessonProgressRepository(db_session)
        user = await _mk_user(db_session, email="ulp8@r.com")
        wk = await _mk_week(db_session, slug="ulp-wk8", number=237)
        ls1 = await _mk_lesson(db_session, wk.id, name="ULP CCW1", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="ULP CCW2", order=2)
        await repo.mark_completed(user.id, ls1.id)
        count = await repo.get_completed_count_by_week(user.id, wk.id)
        assert count == 1


# ---------------------------------------------------------------------------
# TestUserExerciseProgressRepository
# ---------------------------------------------------------------------------

class TestUserExerciseProgressRepository:

    async def test_mark_completed_new(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep1@r.com")
        wk = await _mk_week(db_session, slug="uep-wk1", number=240)
        ls = await _mk_lesson(db_session, wk.id, name="UEP Lesson1")
        ex = await _mk_exercise(db_session, ls.id)
        prog = await repo.mark_completed(user.id, ex.id)
        assert prog.is_completed is True

    async def test_mark_completed_existing(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep2@r.com")
        wk = await _mk_week(db_session, slug="uep-wk2", number=241)
        ls = await _mk_lesson(db_session, wk.id, name="UEP Lesson2")
        ex = await _mk_exercise(db_session, ls.id)
        await repo.mark_completed(user.id, ex.id)
        prog = await repo.mark_completed(user.id, ex.id)  # повторно
        assert prog.is_completed is True

    async def test_get_progress_by_lesson(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep3@r.com")
        wk = await _mk_week(db_session, slug="uep-wk3", number=242)
        ls = await _mk_lesson(db_session, wk.id, name="UEP Lesson3")
        ex1 = await _mk_exercise(db_session, ls.id, order=1)
        ex2 = await _mk_exercise(db_session, ls.id, order=2)
        await repo.mark_completed(user.id, ex1.id)
        progress = await repo.get_progress_by_lesson(user.id, ls.id)
        assert progress["total"] == 2
        assert progress["completed"] == 1
        assert progress["percent"] == 50.0

    async def test_get_progress_by_lessons_batch(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep4@r.com")
        wk = await _mk_week(db_session, slug="uep-wk4", number=243)
        ls1 = await _mk_lesson(db_session, wk.id, name="UEP Batch L1", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="UEP Batch L2", order=2)
        ex1 = await _mk_exercise(db_session, ls1.id)
        ex2 = await _mk_exercise(db_session, ls2.id)
        await repo.mark_completed(user.id, ex1.id)
        result = await repo.get_progress_by_lessons(user.id, [ls1.id, ls2.id])
        assert result[ls1.id]["completed"] == 1
        assert result[ls2.id]["completed"] == 0

    async def test_get_completed_count(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep5@r.com")
        wk = await _mk_week(db_session, slug="uep-wk5", number=244)
        ls = await _mk_lesson(db_session, wk.id, name="UEP Count Lesson")
        ex = await _mk_exercise(db_session, ls.id)
        assert await repo.get_completed_count(user.id) == 0
        await repo.mark_completed(user.id, ex.id)
        assert await repo.get_completed_count(user.id) == 1

    async def test_get_progress_by_lessons_empty(self, db_session):
        repo = UserExerciseProgressRepository(db_session)
        user = await _mk_user(db_session, email="uep6@r.com")
        result = await repo.get_progress_by_lessons(user.id, [])
        assert result == {}


# ---------------------------------------------------------------------------
# TestUserWeekProgressRepository
# ---------------------------------------------------------------------------

class TestUserWeekProgressRepository:

    async def test_create(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp1@r.com")
        wk = await _mk_week(db_session, slug="uwp-wk1", number=250)
        now = datetime.now(timezone.utc)
        prog = await repo.create(user.id, wk.id, now)
        assert prog.id is not None
        assert prog.is_completed is False

    async def test_create_many(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp2@r.com")
        wk1 = await _mk_week(db_session, slug="uwp-wk2a", number=251)
        wk2 = await _mk_week(db_session, slug="uwp-wk2b", number=252)
        now = datetime.now(timezone.utc)
        count = await repo.create_many(user.id, [(wk1.id, now), (wk2.id, now)])
        assert count == 2

    async def test_get_by_user_and_week(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp3@r.com")
        wk = await _mk_week(db_session, slug="uwp-wk3", number=253)
        now = datetime.now(timezone.utc)
        await repo.create(user.id, wk.id, now)
        found = await repo.get_by_user_and_week(user.id, wk.id)
        assert found is not None
        assert found.user_id == user.id

    async def test_get_by_user_and_week_not_found(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp4@r.com")
        assert await repo.get_by_user_and_week(user.id, 999_999) is None

    async def test_mark_completed(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp5@r.com")
        wk = await _mk_week(db_session, slug="uwp-wk5", number=254)
        now = datetime.now(timezone.utc)
        await repo.create(user.id, wk.id, now)
        prog = await repo.mark_completed(user.id, wk.id)
        assert prog.is_completed is True
        assert prog.completed_at is not None

    async def test_get_completed_week_ids(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp6@r.com")
        wk1 = await _mk_week(db_session, slug="uwp-cwk1", number=255)
        wk2 = await _mk_week(db_session, slug="uwp-cwk2", number=256)
        now = datetime.now(timezone.utc)
        await repo.create(user.id, wk1.id, now)
        await repo.create(user.id, wk2.id, now)
        await repo.mark_completed(user.id, wk1.id)
        ids = await repo.get_completed_week_ids(user.id)
        assert wk1.id in ids
        assert wk2.id not in ids

    async def test_get_by_user(self, db_session):
        repo = UserWeekProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwp7@r.com")
        wk1 = await _mk_week(db_session, slug="uwp-bu1", number=257)
        wk2 = await _mk_week(db_session, slug="uwp-bu2", number=258)
        now = datetime.now(timezone.utc)
        await repo.create_many(user.id, [(wk1.id, now), (wk2.id, now)])
        progs = await repo.get_by_user(user.id)
        assert len(progs) == 2


# ---------------------------------------------------------------------------
# TestUserWordProgressRepository
# ---------------------------------------------------------------------------

class TestUserWordProgressRepository:

    async def test_get_or_create_new(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd1@r.com")
        word = await _mk_word(db_session, hanzi="人", translation="person")
        prog = await repo.get_or_create(user.id, word.id)
        assert prog.id is not None
        assert prog.mastery_level == 0

    async def test_get_or_create_existing(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd2@r.com")
        word = await _mk_word(db_session, hanzi="大", translation="big")
        p1 = await repo.get_or_create(user.id, word.id)
        p2 = await repo.get_or_create(user.id, word.id)
        assert p1.id == p2.id

    async def test_update_mastery_correct(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd3@r.com")
        word = await _mk_word(db_session, hanzi="小", translation="small")
        await repo.get_or_create(user.id, word.id)
        prog = await repo.update_mastery(user.id, word.id, is_correct=True)
        assert prog.mastery_level == 1
        assert prog.correct_count == 1

    async def test_update_mastery_wrong(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd4@r.com")
        word = await _mk_word(db_session, hanzi="中", translation="middle")
        await repo.get_or_create(user.id, word.id)
        prog = await repo.update_mastery(user.id, word.id, is_correct=False)
        assert prog.mastery_level == 0  # не уходит ниже 0
        assert prog.wrong_count == 1

    async def test_mastery_capped_at_5(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd5@r.com")
        word = await _mk_word(db_session, hanzi="上", translation="up")
        for _ in range(10):  # Попытка поднять выше 5
            await repo.update_mastery(user.id, word.id, is_correct=True)
        prog = await repo.get_or_create(user.id, word.id)
        assert prog.mastery_level <= 5

    async def test_create_many(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd6@r.com")
        w1 = await _mk_word(db_session, hanzi="左", translation="left")
        w2 = await _mk_word(db_session, hanzi="右", translation="right")
        count = await repo.create_many(user.id, [w1.id, w2.id])
        assert count == 2

    async def test_create_many_empty(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd7@r.com")
        count = await repo.create_many(user.id, [])
        assert count == 0

    async def test_get_existing_word_ids(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd8@r.com")
        w = await _mk_word(db_session, hanzi="前", translation="front")
        await repo.get_or_create(user.id, w.id)
        ids = await repo.get_existing_word_ids(user.id)
        assert w.id in ids

    async def test_get_count(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd9@r.com")
        assert await repo.get_count(user.id) == 0
        w = await _mk_word(db_session, hanzi="后", translation="back")
        await repo.get_or_create(user.id, w.id)
        assert await repo.get_count(user.id) == 1

    async def test_get_mastery_stats(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd10@r.com")
        w1 = await _mk_word(db_session, hanzi="里", translation="inside")
        w2 = await _mk_word(db_session, hanzi="外", translation="outside")
        await repo.get_or_create(user.id, w1.id)
        await repo.get_or_create(user.id, w2.id)
        await repo.update_mastery(user.id, w1.id, is_correct=True)
        stats = await repo.get_mastery_stats(user.id)
        assert isinstance(stats, dict)
        assert stats.get(1, 0) >= 1  # w1 поднялась до 1

    async def test_get_words_for_review(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd11@r.com")
        w = await _mk_word(db_session, hanzi="高", translation="tall")
        # next_review_at в прошлом — слово должно выйти в список
        prog = UserWordProgress(
            user_id=user.id,
            word_id=w.id,
            mastery_level=0,
            next_review_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(prog)
        await db_session.commit()
        words = await repo.get_words_for_review(user.id)
        ids = [p.word_id for p in words]
        assert w.id in ids

    async def test_get_review_count_today(self, db_session):
        repo = UserWordProgressRepository(db_session)
        user = await _mk_user(db_session, email="uwrd12@r.com")
        w = await _mk_word(db_session, hanzi="低", translation="low")
        prog = UserWordProgress(
            user_id=user.id,
            word_id=w.id,
            mastery_level=0,
            next_review_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(prog)
        await db_session.commit()
        count = await repo.get_review_count_today(user.id)
        assert count >= 1


# ---------------------------------------------------------------------------
# TestLessonWordAssociationRepository
# ---------------------------------------------------------------------------

class TestLessonWordAssociationRepository:

    async def test_get_word_ids_by_lesson(self, db_session):
        word_repo = WordRepository(db_session)
        wk = await _mk_week(db_session, slug="lwa-wk", number=260)
        ls = await _mk_lesson(db_session, wk.id, name="LWA Lesson")
        w1 = await _mk_word(db_session, hanzi="快", translation="fast")
        w2 = await _mk_word(db_session, hanzi="慢", translation="slow")
        await word_repo.add_to_lesson(w1.id, ls.id)
        await word_repo.add_to_lesson(w2.id, ls.id)

        repo = LessonWordAssociationRepository(db_session)
        word_ids = await repo.get_word_ids_by_lesson(ls.id)
        assert w1.id in word_ids
        assert w2.id in word_ids

    async def test_get_word_ids_empty(self, db_session):
        wk = await _mk_week(db_session, slug="lwa-empty-wk", number=261)
        ls = await _mk_lesson(db_session, wk.id, name="LWA Empty Lesson")
        repo = LessonWordAssociationRepository(db_session)
        word_ids = await repo.get_word_ids_by_lesson(ls.id)
        assert word_ids == []
