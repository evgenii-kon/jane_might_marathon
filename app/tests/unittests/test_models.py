import pytest
from app.models.user import User
from app.models.week import Week
from app.models.lesson import Lesson
from app.models.user_lesson_progress import UserLessonProgress
from app.models.exercise import Exercise
from app.models.user_exercise_progress import UserExerciseProgress


class TestUserModel:
    def test_create_user(self, db_session):
        user = User(
            email="test@test.com",
            name="Test User",
            password_hash="hash123"
        )

        db_session.add(user)
        db_session.commit()
        user_result = db_session.query(User).filter(user.email=="test@test.com").first()
        assert user.id is not None
        assert user_result.email == "test@test.com"


    def test_email_unique_user(self, db_session):
        user1 = User(email="test@test.com", name="Test User", password_hash="hash123")
        user2 = User(email="test@test.com", name="Test User", password_hash="hash123")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)

        with pytest.raises(Exception):
            db_session.commit()
        

    def test_create_user_with_telegram(self, db_session):
        user = User(email="test@test.com", name="Test User", password_hash="hash123", telegram='TestUser')

        db_session.add(user)
        db_session.commit()
        user_result = db_session.query(User).filter(user.id==user.id).first()
        assert user.telegram == user_result.telegram


class TestWeekModel:
    def test_create_week(self, db_session):
        week = Week(
            slug = 'Week_1',
            short_description = 'Week_short_description',
            long_description = 'Week_long_description',
            number = 1,
            target_words_count = 10,
            target_exercises_count = 10
        )

        db_session.add(week)
        db_session.commit()
        result_week = db_session.query(Week).filter(week.id==week.id).first()

        assert week.slug == result_week.slug
        assert week.short_description == result_week.short_description
        assert week.long_description == result_week.long_description
        assert week.number == result_week.number
        assert week.target_words_count == result_week.target_words_count
        assert week.target_exercises_count == result_week.target_exercises_count


    def test_unique_number_of_week(self, db_session):
        week1 = Week(
            slug = 'Week_1',
            short_description = 'Week_short_description',
            long_description = 'Week_long_description',
            number = 1,
            target_words_count = 10,
            target_exercises_count = 10
        )

        week2 = Week(
            slug = 'Week_2',
            short_description = 'Week2_short_description',
            long_description = 'Week2_long_description',
            number = 1,
            target_words_count = 10,
            target_exercises_count = 10
        )

        db_session.add(week1)
        db_session.commit()

        db_session.add(week2)
        with pytest.raises(Exception):
            db_session.commit()



class TestUserLessonProgressModel:
    def test_create_lesson_progress(self, db_session):
        # Создаём пользователя
        user = User(email="lesson@test.com", name="Lesson User", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        # Создаём неделю
        week = Week(
            slug="week_1", short_description="sd", long_description="ld",
            number=1, target_words_count=10, target_exercises_count=5
        )
        db_session.add(week)
        db_session.commit()

        # Создаём урок, привязанный к неделе
        lesson = Lesson(
            name="Lesson 1",
            week_id=week.id,
            order_in_week=1,
            content_html="<p>Content</p>"
        )
        db_session.add(lesson)
        db_session.commit()

        # Создаём прогресс пользователя по уроку
        progress = UserLessonProgress(
            user_id=user.id,
            lesson_id=lesson.id,
            is_started=True,
            is_completed=False
        )
        db_session.add(progress)
        db_session.commit()

        assert progress.id is not None
        assert progress.user_id == user.id
        assert progress.lesson_id == lesson.id
        assert progress.is_started is True
        assert progress.is_completed is False


class TestExerciseModel:
    def test_create_exercise(self, db_session):
        # Создаём неделю
        week = Week(
            slug="week_1", short_description="sd", long_description="ld",
            number=1, target_words_count=10, target_exercises_count=5
        )
        db_session.add(week)
        db_session.commit()

        # Создаём урок, привязанный к неделе
        lesson = Lesson(
            name="Lesson with exercise",
            week_id=week.id,
            order_in_week=1,
            content_html="<p>Content</p>"
        )
        db_session.add(lesson)
        db_session.commit()

        # Создаём упражнение, привязанное к уроку
        exercise = Exercise(
            lesson_id=lesson.id,
            question_description="Выберите правильный перевод",
            question_text="apple",
            option_1="яблоко",
            option_2="апельсин",
            option_3="банан",
            option_4="груша",
            correct_answer=1,
            explanation="Яблоко по-английски apple",
            order_in_lesson=1
        )
        db_session.add(exercise)
        db_session.commit()

        assert exercise.id is not None
        assert exercise.lesson_id == lesson.id
        assert exercise.correct_answer == 1
        assert exercise.order_in_lesson == 1


class TestUserExerciseProgressModel:
    def test_mark_exercise_completed(self, db_session):
        # Создаём пользователя
        user = User(email="ex_progress@test.com", name="Ex Progress", password_hash="hash")
        db_session.add(user)
        db_session.commit()

        # Создаём неделю
        week = Week(
            slug="week_1", short_description="sd", long_description="ld",
            number=1, target_words_count=10, target_exercises_count=5
        )
        db_session.add(week)
        db_session.commit()

        # Создаём урок
        lesson = Lesson(
            name="Lesson ex",
            week_id=week.id,
            order_in_week=1,
            content_html="<p>Content</p>"
        )
        db_session.add(lesson)
        db_session.commit()

        # Создаём упражнение
        exercise = Exercise(
            lesson_id=lesson.id,
            question_description="q",
            question_text="t",
            option_1="a", option_2="b", option_3="c", option_4="d",
            correct_answer=1
        )
        db_session.add(exercise)
        db_session.commit()

        # Создаём прогресс выполнения упражнения
        progress = UserExerciseProgress(
            user_id=user.id,
            exercise_id=exercise.id,
            is_completed=True
        )
        db_session.add(progress)
        db_session.commit()

        assert progress.id is not None
        assert progress.user_id == user.id
        assert progress.exercise_id == exercise.id
        assert progress.is_completed is True