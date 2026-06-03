"""
Async тесты сервисного слоя.
Тестируем бизнес-логику, обработку ошибок и взаимодействие с репозиториями.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.models.user import User
from app.models.week import Week
from app.models.lesson import Lesson
from app.models.word import Word
from app.models.exercise import Exercise
from app.models.user_word_progress import UserWordProgress

from app.services.user_service import UserService
from app.services.week_service import WeekService
from app.services.lesson_service import LessonService
from app.services.exercise_service import ExerciseService
from app.services.word_service import WordService
from app.services.word_trainer_service import WordTrainerService
from app.services.user_lesson_progress_service import UserLessonProgressService
from app.services.user_week_progress_service import UserWeekProgressService
from app.services.user_exercise_progress_service import UserExerciseProgressService

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.week import WeekCreate, WeekUpdate
from app.schemas.lesson import LessonCreate, LessonUpdate
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate
from app.schemas.word import WordCreate, WordUpdate


# ---------------------------------------------------------------------------
# Вспомогательные хелперы
# ---------------------------------------------------------------------------

async def _mk_user(s, email="svc@t.com", name="Svc User", pw="hash") -> User:
    u = User(email=email, name=name, password_hash=pw)
    s.add(u)
    await s.commit()
    return u


async def _mk_week(s, slug="sw", number=300) -> Week:
    w = Week(
        slug=slug,
        short_description="short description",
        long_description="long description text",
        number=number,
        target_words_count=10,
        target_exercises_count=5,
    )
    s.add(w)
    await s.commit()
    return w


async def _mk_lesson(s, week_id, name="Svc Lesson", order=1) -> Lesson:
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
        explanation="Because a",
        order_in_lesson=order,
    )
    s.add(e)
    await s.commit()
    return e


# ---------------------------------------------------------------------------
# TestUserService
# ---------------------------------------------------------------------------

class TestUserService:

    async def test_get_all_users(self, db_session):
        svc = UserService(db_session)
        await _mk_user(db_session, email="ua@svc.com", name="UA")
        await _mk_user(db_session, email="ub@svc.com", name="UB")
        users = await svc.get_all_users()
        emails = [u.email for u in users]
        assert "ua@svc.com" in emails
        assert "ub@svc.com" in emails

    async def test_get_user_by_id_found(self, db_session):
        svc = UserService(db_session)
        u = await _mk_user(db_session, email="uid@svc.com")
        resp = await svc.get_user_by_id(u.id)
        assert resp.id == u.id
        assert resp.email == "uid@svc.com"

    async def test_get_user_by_id_not_found(self, db_session):
        svc = UserService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_user_by_id(999_999)
        assert exc_info.value.status_code == 404

    async def test_get_user_by_email_found(self, db_session):
        svc = UserService(db_session)
        u = await _mk_user(db_session, email="email@svc.com")
        resp = await svc.get_user_by_email("email@svc.com")
        assert resp.id == u.id

    async def test_get_user_by_email_not_found(self, db_session):
        svc = UserService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_user_by_email("nobody@svc.com")
        assert exc_info.value.status_code == 404

    async def test_create_user_success(self, db_session):
        svc = UserService(db_session)
        data = UserCreate(name="NewUser", email="new@svc.com", password="securepassword")
        resp = await svc.create_user(data)
        assert resp.id is not None
        assert resp.email == "new@svc.com"

    async def test_create_user_duplicate_email(self, db_session):
        svc = UserService(db_session)
        data = UserCreate(name="Dup", email="dup@svc.com", password="securepassword")
        await svc.create_user(data)
        with pytest.raises(HTTPException) as exc_info:
            await svc.create_user(data)
        assert exc_info.value.status_code == 400

    async def test_delete_user(self, db_session):
        svc = UserService(db_session)
        u = await _mk_user(db_session, email="del@svc.com")
        result = await svc.delete_user(u.id)
        assert result is True

    async def test_update_user_success(self, db_session):
        svc = UserService(db_session)
        u = await _mk_user(db_session, email="upd@svc.com", name="Before")
        update = UserUpdate(name="After")
        resp = await svc.update_user(u.id, update)
        assert resp.name == "After"

    async def test_update_user_not_found(self, db_session):
        svc = UserService(db_session)
        update = UserUpdate(name="NXX")
        with pytest.raises(HTTPException) as exc_info:
            await svc.update_user(999_999, update)
        assert exc_info.value.status_code == 404

    async def test_authenticate_user_success(self, db_session):
        svc = UserService(db_session)
        data = UserCreate(name="Auth", email="auth@svc.com", password="mypassword")
        await svc.create_user(data)
        user = await svc.authenticate_user("auth@svc.com", "mypassword")
        assert user.email == "auth@svc.com"

    async def test_authenticate_user_wrong_password(self, db_session):
        svc = UserService(db_session)
        data = UserCreate(name="WrongPw", email="wrongpw@svc.com", password="correct")
        await svc.create_user(data)
        with pytest.raises(HTTPException) as exc_info:
            await svc.authenticate_user("wrongpw@svc.com", "wrong")
        assert exc_info.value.status_code == 401

    async def test_authenticate_user_not_found(self, db_session):
        svc = UserService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.authenticate_user("ghost@svc.com", "any")
        assert exc_info.value.status_code == 401

    async def test_verify_password(self, db_session):
        svc = UserService(db_session)
        hashed = svc._hash_password("mysecret")
        assert svc.verify_password("mysecret", hashed) is True
        assert svc.verify_password("wrong", hashed) is False


# ---------------------------------------------------------------------------
# TestWeekService
# ---------------------------------------------------------------------------

class TestWeekService:

    async def test_get_all_weeks(self, db_session):
        svc = WeekService(db_session)
        await _mk_week(db_session, slug="wsvc-1", number=301)
        await _mk_week(db_session, slug="wsvc-2", number=302)
        weeks = await svc.get_all_weeks()
        slugs = [w.slug for w in weeks]
        assert "wsvc-1" in slugs
        assert "wsvc-2" in slugs

    async def test_get_week_by_id_found(self, db_session):
        svc = WeekService(db_session)
        w = await _mk_week(db_session, slug="wsvc-id", number=303)
        resp = await svc.get_week_by_id(w.id)
        assert resp.id == w.id

    async def test_get_week_by_id_not_found(self, db_session):
        svc = WeekService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_week_by_id(999_999)
        assert exc_info.value.status_code == 404

    async def test_get_week_by_slug_found(self, db_session):
        svc = WeekService(db_session)
        await _mk_week(db_session, slug="by-slug-svc", number=304)
        resp = await svc.get_week_by_slug("by-slug-svc")
        assert resp.slug == "by-slug-svc"

    async def test_get_week_by_slug_not_found(self, db_session):
        svc = WeekService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_week_by_slug("nonexistent-slug")
        assert exc_info.value.status_code == 404

    async def test_create_week_success(self, db_session):
        svc = WeekService(db_session)
        data = WeekCreate(
            slug="new-wsvc",
            short_description="short desc text",
            long_description="very long description for week",
            number=45,
            target_words_count=5,
            target_exercises_count=5,
        )
        resp = await svc.create_week(data)
        assert resp.slug == "new-wsvc"

    async def test_create_week_duplicate_slug(self, db_session):
        svc = WeekService(db_session)
        data = WeekCreate(
            slug="dup-wsvc",
            short_description="short desc text",
            long_description="very long description for week",
            number=43,
            target_words_count=5,
            target_exercises_count=5,
        )
        await svc.create_week(data)
        data2 = WeekCreate(
            slug="dup-wsvc",  # тот же slug
            short_description="short desc text",
            long_description="very long description for week",
            number=44,
            target_words_count=5,
            target_exercises_count=5,
        )
        with pytest.raises(HTTPException) as exc_info:
            await svc.create_week(data2)
        assert exc_info.value.status_code == 400

    async def test_create_week_duplicate_number(self, db_session):
        svc = WeekService(db_session)
        data = WeekCreate(
            slug="dup-num-wsvc",
            short_description="short desc text",
            long_description="very long description for week",
            number=42,
            target_words_count=5,
            target_exercises_count=5,
        )
        await svc.create_week(data)
        data2 = WeekCreate(
            slug="dup-num-wsvc-2",
            short_description="short desc text",
            long_description="very long description for week",
            number=42,  # тот же номер
            target_words_count=5,
            target_exercises_count=5,
        )
        with pytest.raises(HTTPException) as exc_info:
            await svc.create_week(data2)
        assert exc_info.value.status_code == 400

    async def test_delete_week_success(self, db_session):
        svc = WeekService(db_session)
        w = await _mk_week(db_session, slug="del-wsvc", number=309)
        result = await svc.delete_week(w.id)
        assert result is True

    async def test_delete_week_not_found(self, db_session):
        svc = WeekService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.delete_week(999_999)
        assert exc_info.value.status_code == 404

    async def test_update_week_success(self, db_session):
        svc = WeekService(db_session)
        w = await _mk_week(db_session, slug="upd-wsvc", number=310)
        data = WeekUpdate(short_description="updated short desc")
        resp = await svc.update_week(w.id, data)
        assert resp.short_description == "updated short desc"

    async def test_update_week_not_found(self, db_session):
        svc = WeekService(db_session)
        data = WeekUpdate(short_description="x" * 10)
        with pytest.raises(HTTPException) as exc_info:
            await svc.update_week(999_999, data)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# TestLessonService
# ---------------------------------------------------------------------------

class TestLessonService:

    async def test_get_all_lessons(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-wk", number=311)
        await _mk_lesson(db_session, wk.id, name="LS All 1")
        await _mk_lesson(db_session, wk.id, name="LS All 2", order=2)
        lessons = await svc.get_all_lessons()
        names = [l.name for l in lessons]
        assert "LS All 1" in names

    async def test_get_lesson_by_id_found(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-id-wk", number=312)
        ls = await _mk_lesson(db_session, wk.id, name="LS ByID")
        resp = await svc.get_lesson_by_id(ls.id)
        assert resp.id == ls.id

    async def test_get_lesson_by_id_not_found(self, db_session):
        svc = LessonService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_lesson_by_id(999_999)
        assert exc_info.value.status_code == 404

    async def test_create_lesson_success(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-c-wk", number=313)
        data = LessonCreate(name="LS Create", week_id=wk.id, order_in_week=1, content_html="c")
        resp = await svc.create_lesson(data)
        assert resp.name == "LS Create"

    async def test_create_lesson_duplicate_name(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-dup-wk", number=314)
        data = LessonCreate(name="LS Dup", week_id=wk.id, order_in_week=1, content_html="c")
        await svc.create_lesson(data)
        with pytest.raises(HTTPException) as exc_info:
            await svc.create_lesson(data)
        assert exc_info.value.status_code == 400

    async def test_update_lesson_success(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-u-wk", number=315)
        ls = await _mk_lesson(db_session, wk.id, name="LS Before")
        data = LessonUpdate(name="LS After")
        resp = await svc.update_lesson(ls.id, data)
        assert resp.name == "LS After"

    async def test_update_lesson_not_found(self, db_session):
        svc = LessonService(db_session)
        data = LessonUpdate(name="X" * 10)
        with pytest.raises(HTTPException) as exc_info:
            await svc.update_lesson(999_999, data)
        assert exc_info.value.status_code == 404

    async def test_delete_lesson_success(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-d-wk", number=316)
        ls = await _mk_lesson(db_session, wk.id, name="LS Delete")
        result = await svc.delete_lesson(ls.id)
        assert result is True

    async def test_delete_lesson_not_found(self, db_session):
        svc = LessonService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.delete_lesson(999_999)
        assert exc_info.value.status_code == 404

    async def test_get_lessons_by_week(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-bw-wk", number=317)
        await _mk_lesson(db_session, wk.id, name="LS Week 1", order=1)
        await _mk_lesson(db_session, wk.id, name="LS Week 2", order=2)
        lessons = await svc.get_lessons_by_week(wk.id)
        assert len(lessons) == 2

    async def test_get_lessons_count(self, db_session):
        svc = LessonService(db_session)
        wk = await _mk_week(db_session, slug="ls-cnt-wk", number=318)
        before = await svc.get_lessons_count()
        
        await svc.create_lesson(LessonCreate(
            name="LS Count Test", 
            week_id=wk.id, 
            order_in_week=1, 
            content_html="c"
        ))
        
        after = await svc.get_lessons_count()
        assert after == before + 1


# ---------------------------------------------------------------------------
# TestExerciseService
# ---------------------------------------------------------------------------

class TestExerciseService:

    async def test_get_all_exercises(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-wk", number=319)
        ls = await _mk_lesson(db_session, wk.id, name="ES All Lesson")
        e = await _mk_exercise(db_session, ls.id)
        exercises = await svc.get_all_exercises()
        ids = [ex.id for ex in exercises]
        assert e.id in ids

    async def test_get_exercise_by_id_found(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-id-wk", number=320)
        ls = await _mk_lesson(db_session, wk.id, name="ES ByID Lesson")
        e = await _mk_exercise(db_session, ls.id)
        resp = await svc.get_exercise_by_id(e.id)
        assert resp.id == e.id

    async def test_get_exercise_by_id_not_found(self, db_session):
        svc = ExerciseService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_exercise_by_id(999_999)
        assert exc_info.value.status_code == 404

    async def test_get_exercises_by_lesson(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-bl-wk", number=321)
        ls = await _mk_lesson(db_session, wk.id, name="ES ByLesson")
        await _mk_exercise(db_session, ls.id, order=1)
        await _mk_exercise(db_session, ls.id, order=2)
        exercises = await svc.get_exercises_by_lesson(ls.id)
        assert len(exercises) == 2

    async def test_create_exercise(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-c-wk", number=322)
        ls = await _mk_lesson(db_session, wk.id, name="ES Create")
        data = ExerciseCreate(
            lesson_id=ls.id,
            question_description="d",
            question_text="t",
            option_1="a", option_2="b", option_3="c", option_4="d",
            correct_answer=2,
            order_in_lesson=1,
        )
        resp = await svc.create_exercise(data)
        assert resp.correct_answer == 2

    async def test_update_exercise_success(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-u-wk", number=323)
        ls = await _mk_lesson(db_session, wk.id, name="ES Update")
        e = await _mk_exercise(db_session, ls.id)
        data = ExerciseUpdate(correct_answer=3)
        resp = await svc.update_exercise(e.id, data)
        assert resp.correct_answer == 3

    async def test_update_exercise_not_found(self, db_session):
        svc = ExerciseService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.update_exercise(999_999, ExerciseUpdate(correct_answer=1))
        assert exc_info.value.status_code == 404

    async def test_delete_exercise_success(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-d-wk", number=324)
        ls = await _mk_lesson(db_session, wk.id, name="ES Delete")
        e = await _mk_exercise(db_session, ls.id)
        result = await svc.delete_exercise(e.id)
        assert result is True

    async def test_delete_exercise_not_found(self, db_session):
        svc = ExerciseService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.delete_exercise(999_999)
        assert exc_info.value.status_code == 404

    async def test_check_answer_correct(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-ca-wk", number=325)
        ls = await _mk_lesson(db_session, wk.id, name="ES CheckAnswer")
        e = await _mk_exercise(db_session, ls.id)  # correct_answer=1
        resp = await svc.check_answer(e.id, 1)
        assert resp.is_correct is True
        assert resp.explanation is None

    async def test_check_answer_wrong(self, db_session):
        svc = ExerciseService(db_session)
        wk = await _mk_week(db_session, slug="es-caw-wk", number=326)
        ls = await _mk_lesson(db_session, wk.id, name="ES CheckAnswer Wrong")
        e = await _mk_exercise(db_session, ls.id)  # correct_answer=1
        resp = await svc.check_answer(e.id, 2)
        assert resp.is_correct is False
        assert resp.explanation == "Because a"


# ---------------------------------------------------------------------------
# TestWordService
# ---------------------------------------------------------------------------

class TestWordService:

    async def test_get_all_words(self, db_session):
        svc = WordService(db_session)
        await _mk_word(db_session, hanzi="快", translation="fast")
        words = await svc.get_all_words()
        assert len(words) >= 1

    async def test_get_word_by_id_found(self, db_session):
        svc = WordService(db_session)
        w = await _mk_word(db_session, hanzi="慢", translation="slow")
        resp = await svc.get_word_by_id(w.id)
        assert resp.id == w.id

    async def test_get_word_by_id_not_found(self, db_session):
        svc = WordService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_word_by_id(999_999)
        assert exc_info.value.status_code == 404

    async def test_create_word(self, db_session):
        svc = WordService(db_session)
        data = WordCreate(hanzi="新", transcription="xīn", translation="new")
        resp = await svc.create_word(data)
        assert resp.hanzi == "新"

    async def test_update_word_success(self, db_session):
        svc = WordService(db_session)
        w = await _mk_word(db_session, hanzi="旧", translation="old")
        resp = await svc.update_word(w.id, WordUpdate(translation="ancient"))
        assert resp.translation == "ancient"

    async def test_update_word_not_found(self, db_session):
        svc = WordService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.update_word(999_999, WordUpdate(translation="x"))
        assert exc_info.value.status_code == 404

    async def test_delete_word(self, db_session):
        svc = WordService(db_session)
        w = await _mk_word(db_session, hanzi="删", translation="delete")
        result = await svc.delete_word(w.id)
        assert "deleted" in result["message"]

    async def test_delete_word_not_found(self, db_session):
        svc = WordService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.delete_word(999_999)
        assert exc_info.value.status_code == 404

    async def test_get_words_by_lesson(self, db_session):
        from app.repositories.word_repository import WordRepository
        svc = WordService(db_session)
        wk = await _mk_week(db_session, slug="ws-bl-wk", number=327)
        ls = await _mk_lesson(db_session, wk.id, name="WS ByLesson")
        w = await _mk_word(db_session, hanzi="课", translation="lesson")
        wr = WordRepository(db_session)
        await wr.add_to_lesson(w.id, ls.id)
        words = await svc.get_words_by_lesson(ls.id)
        assert len(words) == 1
        assert words[0].hanzi == "课"

    async def test_add_word_to_lesson(self, db_session):
        svc = WordService(db_session)
        wk = await _mk_week(db_session, slug="ws-al-wk", number=328)
        ls = await _mk_lesson(db_session, wk.id, name="WS AddLesson")
        w = await _mk_word(db_session, hanzi="加", translation="add")
        result = await svc.add_word_to_lesson(w.id, ls.id)
        assert "added" in result["message"]

    async def test_remove_word_from_lesson(self, db_session):
        svc = WordService(db_session)
        wk = await _mk_week(db_session, slug="ws-rl-wk", number=329)
        ls = await _mk_lesson(db_session, wk.id, name="WS RemoveLesson")
        w = await _mk_word(db_session, hanzi="减", translation="remove")
        await svc.add_word_to_lesson(w.id, ls.id)
        result = await svc.remove_word_from_lesson(w.id, ls.id)
        assert "removed" in result["message"]


# ---------------------------------------------------------------------------
# TestUserLessonProgressService
# ---------------------------------------------------------------------------

class TestUserLessonProgressService:

    async def test_mark_lesson_as_started(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk1", number=330)
        ls = await _mk_lesson(db_session, wk.id, name="ULPS Started")
        user = await _mk_user(db_session, email="ulps1@svc.com")
        resp = await svc.mark_lesson_as_started(user.id, ls.id)
        assert resp.is_started is True

    async def test_mark_lesson_as_started_not_found(self, db_session):
        svc = UserLessonProgressService(db_session)
        user = await _mk_user(db_session, email="ulps2@svc.com")
        with pytest.raises(HTTPException) as exc_info:
            await svc.mark_lesson_as_started(user.id, 999_999)
        assert exc_info.value.status_code == 404

    async def test_mark_lesson_as_completed(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk2", number=331)
        ls = await _mk_lesson(db_session, wk.id, name="ULPS Completed")
        user = await _mk_user(db_session, email="ulps3@svc.com")
        resp = await svc.mark_lesson_as_completed(user.id, ls.id)
        assert resp.is_completed is True

    async def test_mark_lesson_as_completed_already(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk3", number=332)
        ls = await _mk_lesson(db_session, wk.id, name="ULPS Already Done")
        user = await _mk_user(db_session, email="ulps4@svc.com")
        await svc.mark_lesson_as_completed(user.id, ls.id)
        with pytest.raises(HTTPException) as exc_info:
            await svc.mark_lesson_as_completed(user.id, ls.id)
        assert exc_info.value.status_code == 400

    async def test_is_lesson_started(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk4", number=333)
        ls = await _mk_lesson(db_session, wk.id, name="ULPS IsStarted")
        user = await _mk_user(db_session, email="ulps5@svc.com")
        assert await svc.is_lesson_started(user.id, ls.id) is False
        await svc.mark_lesson_as_started(user.id, ls.id)
        assert await svc.is_lesson_started(user.id, ls.id) is True

    async def test_get_week_progress(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk5", number=334)
        ls1 = await _mk_lesson(db_session, wk.id, name="ULPS WP L1", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="ULPS WP L2", order=2)
        user = await _mk_user(db_session, email="ulps6@svc.com")
        await svc.mark_lesson_as_completed(user.id, ls1.id)
        summary = await svc.get_week_progress(user.id, wk.id)
        assert summary.total_lessons == 2
        assert summary.completed_lessons == 1
        assert summary.is_week_completed is False

    async def test_get_completed_count_by_user(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk6", number=335)
        ls = await _mk_lesson(db_session, wk.id, name="ULPS Count User")
        user = await _mk_user(db_session, email="ulps7@svc.com")
        assert await svc.get_completed_count_by_user(user.id) == 0
        await svc.mark_lesson_as_completed(user.id, ls.id)
        assert await svc.get_completed_count_by_user(user.id) == 1

    async def test_get_lessons_with_progress(self, db_session):
        svc = UserLessonProgressService(db_session)
        wk = await _mk_week(db_session, slug="ulps-wk7", number=336)
        ls1 = await _mk_lesson(db_session, wk.id, name="ULPS WP R1", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="ULPS WP R2", order=2)
        user = await _mk_user(db_session, email="ulps8@svc.com")
        await svc.mark_lesson_as_started(user.id, ls1.id)
        result = await svc.get_lessons_with_progress(user.id, wk.id)
        started_ids = [l.id for l in result if l.is_started]
        assert ls1.id in started_ids


# ---------------------------------------------------------------------------
# TestUserWeekProgressService
# ---------------------------------------------------------------------------

class TestUserWeekProgressService:

    async def test_init_user_weeks(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps1@svc.com")
        wk1 = await _mk_week(db_session, slug="uwps-wk1", number=340)
        wk2 = await _mk_week(db_session, slug="uwps-wk2", number=341)
        # init_user_weeks создаёт записи для всех недель
        await svc.init_user_weeks(user.id)
        from app.repositories.user_week_progress_repository import UserWeekProgressRepository
        repo = UserWeekProgressRepository(db_session)
        progs = await repo.get_by_user(user.id)
        week_ids = [p.week_id for p in progs]
        assert wk1.id in week_ids
        assert wk2.id in week_ids

    async def test_get_or_create_creates_new(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps2@svc.com")
        wk = await _mk_week(db_session, slug="uwps-wk3", number=342)
        resp = await svc.get_or_create(user.id, wk.id)
        assert resp.week_id == wk.id

    async def test_get_or_create_returns_existing(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps3@svc.com")
        wk = await _mk_week(db_session, slug="uwps-wk4", number=343)
        r1 = await svc.get_or_create(user.id, wk.id)
        r2 = await svc.get_or_create(user.id, wk.id)
        assert r1.id == r2.id

    async def test_is_week_available_opened(self, db_session):
        from app.repositories.user_week_progress_repository import UserWeekProgressRepository
        user = await _mk_user(db_session, email="uwps4@svc.com")
        wk = await _mk_week(db_session, slug="uwps-wk5", number=41)
        repo = UserWeekProgressRepository(db_session)
        # opens_at в прошлом — неделя открыта
        past = datetime.now(timezone.utc) - timedelta(days=1)
        await repo.create(user.id, wk.id, past)
        svc = UserWeekProgressService(db_session)
        available = await svc.is_week_available(user.id, wk.id)
        assert available is True

    async def test_is_week_available_locked(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps5@svc.com")
        wk = await _mk_week(db_session, slug="uwps-wk6", number=350)
        from app.repositories.user_week_progress_repository import UserWeekProgressRepository
        repo = UserWeekProgressRepository(db_session)
        # Устанавливаем opens_at в будущем
        future = datetime.now(timezone.utc) + timedelta(days=100)
        await repo.create(user.id, wk.id, future)
        available = await svc.is_week_available(user.id, wk.id)
        assert available is False

    async def test_is_week_available_no_progress(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps6@svc.com")
        available = await svc.is_week_available(user.id, 999_999)
        assert available is False

    async def test_mark_week_completed(self, db_session):
        svc = UserWeekProgressService(db_session)
        user = await _mk_user(db_session, email="uwps7@svc.com")
        wk = await _mk_week(db_session, slug="uwps-wk7", number=351)
        await svc.get_or_create(user.id, wk.id)
        resp = await svc.mark_week_completed(user.id, wk.id)
        assert resp.is_completed is True

    async def test_init_user_weeks_user_not_found(self, db_session):
        svc = UserWeekProgressService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await svc.init_user_weeks(999_999)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# TestUserExerciseProgressService
# ---------------------------------------------------------------------------

class TestUserExerciseProgressService:

    async def test_is_exercise_completed(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk1", number=352)
        ls = await _mk_lesson(db_session, wk.id, name="UEPS Lesson1")
        ex = await _mk_exercise(db_session, ls.id)
        user = await _mk_user(db_session, email="ueps1@svc.com")
        assert await svc.is_exercise_completed(user.id, ex.id) is False
        await svc.mark_exercise_completed(user.id, ex.id)
        assert await svc.is_exercise_completed(user.id, ex.id) is True

    async def test_mark_exercise_completed(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk2", number=353)
        ls = await _mk_lesson(db_session, wk.id, name="UEPS Lesson2")
        ex = await _mk_exercise(db_session, ls.id)
        user = await _mk_user(db_session, email="ueps2@svc.com")
        resp = await svc.mark_exercise_completed(user.id, ex.id)
        assert resp.is_completed is True

    async def test_mark_exercise_not_found(self, db_session):
        svc = UserExerciseProgressService(db_session)
        user = await _mk_user(db_session, email="ueps3@svc.com")
        with pytest.raises(HTTPException) as exc_info:
            await svc.mark_exercise_completed(user.id, 999_999)
        assert exc_info.value.status_code == 404

    async def test_get_lesson_progress(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk3", number=354)
        ls = await _mk_lesson(db_session, wk.id, name="UEPS Lesson3")
        ex1 = await _mk_exercise(db_session, ls.id, order=1)
        ex2 = await _mk_exercise(db_session, ls.id, order=2)
        user = await _mk_user(db_session, email="ueps4@svc.com")
        await svc.mark_exercise_completed(user.id, ex1.id)
        progress = await svc.get_lesson_progress(user.id, ls.id)
        assert progress.total == 2
        assert progress.completed == 1

    async def test_get_completed_exercise_ids(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk4", number=355)
        ls = await _mk_lesson(db_session, wk.id, name="UEPS Lesson4")
        ex = await _mk_exercise(db_session, ls.id)
        user = await _mk_user(db_session, email="ueps5@svc.com")
        await svc.mark_exercise_completed(user.id, ex.id)
        ids = await svc.get_completed_exercise_ids(user.id, ls.id)
        assert ex.id in ids

    async def test_get_total_completed_count(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk5", number=356)
        ls = await _mk_lesson(db_session, wk.id, name="UEPS Lesson5")
        ex = await _mk_exercise(db_session, ls.id)
        user = await _mk_user(db_session, email="ueps6@svc.com")
        assert await svc.get_total_completed_count(user.id) == 0
        await svc.mark_exercise_completed(user.id, ex.id)
        assert await svc.get_total_completed_count(user.id) == 1

    async def test_get_lessons_progress_batch(self, db_session):
        svc = UserExerciseProgressService(db_session)
        wk = await _mk_week(db_session, slug="ueps-wk6", number=357)
        ls1 = await _mk_lesson(db_session, wk.id, name="UEPS L6a", order=1)
        ls2 = await _mk_lesson(db_session, wk.id, name="UEPS L6b", order=2)
        ex1 = await _mk_exercise(db_session, ls1.id)
        user = await _mk_user(db_session, email="ueps7@svc.com")
        await svc.mark_exercise_completed(user.id, ex1.id)
        result = await svc.get_lessons_progress(user.id, [ls1.id, ls2.id])
        assert ls1.id in result
        assert ls2.id in result
        assert result[ls1.id].completed == 1
        assert result[ls2.id].completed == 0


# ---------------------------------------------------------------------------
# TestWordTrainerService
# ---------------------------------------------------------------------------

class TestWordTrainerService:

    async def test_add_lesson_words_to_progress(self, db_session):
        svc = WordTrainerService(db_session)
        from app.repositories.word_repository import WordRepository
        wk = await _mk_week(db_session, slug="wts-wk1", number=360)
        ls = await _mk_lesson(db_session, wk.id, name="WTS Lesson1")
        w1 = await _mk_word(db_session, hanzi="手", translation="hand")
        w2 = await _mk_word(db_session, hanzi="脚", translation="foot")
        wr = WordRepository(db_session)
        await wr.add_to_lesson(w1.id, ls.id)
        await wr.add_to_lesson(w2.id, ls.id)
        user = await _mk_user(db_session, email="wts1@svc.com")
        count = await svc.add_lesson_words_to_progress(user.id, ls.id)
        assert count == 2

    async def test_add_lesson_words_idempotent(self, db_session):
        svc = WordTrainerService(db_session)
        from app.repositories.word_repository import WordRepository
        wk = await _mk_week(db_session, slug="wts-wk2", number=361)
        ls = await _mk_lesson(db_session, wk.id, name="WTS Lesson2")
        w = await _mk_word(db_session, hanzi="眼", translation="eye")
        wr = WordRepository(db_session)
        await wr.add_to_lesson(w.id, ls.id)
        user = await _mk_user(db_session, email="wts2@svc.com")
        await svc.add_lesson_words_to_progress(user.id, ls.id)
        count = await svc.add_lesson_words_to_progress(user.id, ls.id)  # повторно
        assert count == 0

    async def test_add_lesson_words_no_words(self, db_session):
        svc = WordTrainerService(db_session)
        wk = await _mk_week(db_session, slug="wts-wk3", number=362)
        ls = await _mk_lesson(db_session, wk.id, name="WTS Lesson3 Empty")
        user = await _mk_user(db_session, email="wts3@svc.com")
        count = await svc.add_lesson_words_to_progress(user.id, ls.id)
        assert count == 0

    async def test_get_due_count(self, db_session):
        svc = WordTrainerService(db_session)
        user = await _mk_user(db_session, email="wts4@svc.com")
        w = await _mk_word(db_session, hanzi="耳", translation="ear")
        prog = UserWordProgress(
            user_id=user.id,
            word_id=w.id,
            mastery_level=0,
            next_review_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(prog)
        await db_session.commit()
        count = await svc.get_due_count(user.id)
        assert count >= 1

    async def test_get_all_words_session(self, db_session):
        svc = WordTrainerService(db_session)
        await _mk_word(db_session, hanzi="鼻", translation="nose")
        await _mk_word(db_session, hanzi="口", translation="mouth")
        words = await svc.get_all_words_session(999)  # user_id не используется
        assert len(words) >= 2

    async def test_update_mastery(self, db_session):
        svc = WordTrainerService(db_session)
        user = await _mk_user(db_session, email="wts5@svc.com")
        w = await _mk_word(db_session, hanzi="头", translation="head")
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        await UserWordProgressRepository(db_session).get_or_create(user.id, w.id)
        prog = await svc.update_mastery(user.id, w.id, is_correct=True)
        assert prog.mastery_level == 1

    async def test_get_mastery_stats(self, db_session):
        svc = WordTrainerService(db_session)
        user = await _mk_user(db_session, email="wts6@svc.com")
        w = await _mk_word(db_session, hanzi="身", translation="body")
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        await UserWordProgressRepository(db_session).get_or_create(user.id, w.id)
        stats = await svc.get_mastery_stats(user.id)
        assert isinstance(stats, dict)
        assert stats.get(0, 0) >= 1

    async def test_get_total_words_count(self, db_session):
        svc = WordTrainerService(db_session)
        user = await _mk_user(db_session, email="wts7@svc.com")
        assert await svc.get_total_words_count(user.id) == 0
        w = await _mk_word(db_session, hanzi="背", translation="back")
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        await UserWordProgressRepository(db_session).get_or_create(user.id, w.id)
        assert await svc.get_total_words_count(user.id) == 1

    async def test_get_word_ranking(self, db_session):
        svc = WordTrainerService(db_session)
        user = await _mk_user(db_session, email="wts8@svc.com")
        w = await _mk_word(db_session, hanzi="腿", translation="leg")
        from app.repositories.user_word_progress_repository import UserWordProgressRepository
        await UserWordProgressRepository(db_session).get_or_create(user.id, w.id)
        ranking = await svc.get_word_ranking(user.id)
        assert isinstance(ranking, list)
        assert len(ranking) >= 1
