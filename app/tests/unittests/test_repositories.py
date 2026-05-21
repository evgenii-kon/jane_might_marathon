import pytest
from app.repositories.user_repository import UserRepository
from app.repositories.week_repository import WeekRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.word_repository import WordRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.article_repository import ArticleRepository

from app.models.user import User
from app.models.week import Week
from app.models.lesson import Lesson
from app.models.word import Word
from app.models.exercise import Exercise
from app.models.article import Article
from app.schemas.week import WeekCreate
from app.schemas.user import UserUpdate
from app.schemas.lesson import LessonCreate
from app.schemas.exercise import ExerciseCreate
from app.schemas.article import ArticleCreate



@pytest.fixture
def two_users(db_session):
    """Создаёт двух пользователей в БД для тестов"""
    user1 = User(email="test1@test.com", name="Test User1", password_hash="hash123")
    user2 = User(email="test2@test.com", name="Test User2", password_hash="hash321")
    db_session.add_all([user1, user2])
    db_session.commit()
    return user1, user2

@pytest.fixture
def two_weeks(db_session):
    week1 = Week(
        slug="week-1",
        short_description="First week",
        long_description="Description of first week",
        number=1,
        target_words_count=10,
        target_exercises_count=5
    )
    week2 = Week(
        slug="week-2",
        short_description="Second week",
        long_description="Description of second week",
        number=2,
        target_words_count=15,
        target_exercises_count=8
    )
    db_session.add_all([week1, week2])
    db_session.commit()
    return week1, week2

@pytest.fixture
def test_week(db_session):
    week = Week(
        slug="test-week",
        short_description="Test Week",
        long_description="Long desc",
        number=100,
        target_words_count=10,
        target_exercises_count=5
    )
    db_session.add(week)
    db_session.commit()
    return week


@pytest.fixture
def test_lesson(db_session, test_week):
    lesson = Lesson(
        name="Test Word Lesson",
        week_id=test_week.id,
        order_in_week=1,
        content_html="<p>Lesson for words</p>"
    )
    db_session.add(lesson)
    db_session.commit()
    return lesson

class TestUserRepository:

    def test_user_repository_get_all(self, db_session, two_users):
        repo = UserRepository(db_session)
        all_users = repo.get_all()
        emails = [u.email for u in all_users]
        assert "test1@test.com" in emails
        assert "test2@test.com" in emails

    def test_user_repository_get_by_id(self, db_session, two_users):
        repo = UserRepository(db_session)
        user1, user2 = two_users
        found1 = repo.get_by_id(user1.id)
        found2 = repo.get_by_id(user2.id)
        assert found1.email == "test1@test.com"
        assert found1.name == "Test User1"
        assert found2.email == "test2@test.com"
        assert found2.name == "Test User2"

    def test_user_repository_get_by_name(self, db_session, two_users):
        repo = UserRepository(db_session)
        user1, user2 = two_users
        found1 = repo.get_by_name(user1.name)
        found2 = repo.get_by_name(user2.name)
        assert found1.email == "test1@test.com"
        assert found2.email == "test2@test.com"

    def test_user_repository_get_by_email(self, db_session, two_users):
        repo = UserRepository(db_session)
        user1, user2 = two_users
        found1 = repo.get_by_email(user1.email)
        found2 = repo.get_by_email(user2.email)
        assert found1.id == user1.id
        assert found2.id == user2.id

    def test_user_repository_create(self, db_session):
        repo = UserRepository(db_session)
        data = {
            "email": "create@test.com",
            "name": "Created User",
            "password_hash": "hash789"
        }
        user = repo.create(data)
        assert user.id is not None
        assert user.email == "create@test.com"
        assert user.name == "Created User"

    def test_user_repository_delete(self, db_session, two_users):
        repo = UserRepository(db_session)
        user1, user2 = two_users
        result = repo.delete(user1.id)
        assert result is True
        deleted = repo.get_by_id(user1.id)
        assert deleted is None
        remaining = repo.get_by_id(user2.id)
        assert remaining.id == user2.id

    def test_user_repository_update(self, db_session, two_users):
        repo = UserRepository(db_session)
        user1, user2 = two_users
        update_data = UserUpdate(name="Updated Name", email="updated@test.com")
        updated = repo.update(user1.id, update_data)
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == "updated@test.com"
        unchanged = repo.get_by_id(user2.id)
        assert unchanged.name == "Test User2"
        assert unchanged.email == "test2@test.com"


class TestWeekRepository:

    def test_week_repository_get_all(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        all_weeks = repo.get_all()
        slugs = [w.slug for w in all_weeks]
        assert "week-1" in slugs
        assert "week-2" in slugs
        assert len(all_weeks) == 2


    def test_week_repository_get_by_id(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        week1, week2 = two_weeks
        found1 = repo.get_by_id(week1.id)
        found2 = repo.get_by_id(week2.id)
        assert found1.slug == "week-1"
        assert found2.slug == "week-2"
        assert found1.number == 1
        assert found2.number == 2


    def test_week_repository_get_by_slug(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        week1, week2 = two_weeks
        found1 = repo.get_by_slug("week-1")
        found2 = repo.get_by_slug("week-2")
        assert found1.id == week1.id
        assert found2.id == week2.id


    def test_week_repository_get_by_number(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        week1, week2 = two_weeks
        found1 = repo.get_by_number(1)
        found2 = repo.get_by_number(2)
        assert found1.id == week1.id
        assert found2.id == week2.id


    def test_week_repository_create(self, db_session):
        repo = WeekRepository(db_session)
        data = WeekCreate(
            slug="new-week",
            short_description="very short description",
            long_description="Very very long description",
            number=3,
            target_words_count=20,
            target_exercises_count=10
        )
        week = repo.create(data)
        assert week.id is not None
        assert week.slug == "new-week"
        assert week.number == 3


    def test_week_repository_update(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        week1, _ = two_weeks
        update_dict = {"short_description": "Updated description", "target_words_count": 25}
        updated = repo.update(week1.id, update_dict)
        assert updated.short_description == "Updated description"
        assert updated.target_words_count == 25
        assert updated.slug == "week-1"


    def test_week_repository_delete(self, db_session, two_weeks):
        repo = WeekRepository(db_session)
        week1, week2 = two_weeks
        result = repo.delete(week1.id)
        assert result is True
        assert repo.get_by_id(week1.id) is None
        assert repo.get_by_id(week2.id) is not None


class TestLessonRepository:

    def test_lesson_repository_get_all(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson1 = Lesson(name="Lesson 1", week_id=test_week.id, order_in_week=1, content_html="c1")
        lesson2 = Lesson(name="Lesson 2", week_id=test_week.id, order_in_week=2, content_html="c2")
        db_session.add_all([lesson1, lesson2])
        db_session.commit()
        all_lessons = repo.get_all()
        assert len(all_lessons) >= 2
        names = [l.name for l in all_lessons]
        assert "Lesson 1" in names
        assert "Lesson 2" in names


    def test_lesson_repository_get_by_id(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson = Lesson(name="GetById", week_id=test_week.id, order_in_week=1, content_html="c")
        db_session.add(lesson)
        db_session.commit()
        found = repo.get_by_id(lesson.id)
        assert found.name == "GetById"


    def test_lesson_repository_get_by_name(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson = Lesson(name="UniqueName", week_id=test_week.id, order_in_week=1, content_html="c")
        db_session.add(lesson)
        db_session.commit()
        found = repo.get_by_name("UniqueName")
        assert found.id == lesson.id


    def test_lesson_repository_create(self, db_session, test_week):
        repo = LessonRepository(db_session)
        data = LessonCreate(
            name="Created Lesson",
            week_id=test_week.id,
            order_in_week=3,
            content_html="<p>Content</p>",
            video_url=None
        )
        lesson = repo.create(data)
        assert lesson.id is not None
        assert lesson.name == "Created Lesson"
        assert lesson.week_id == test_week.id


    def test_lesson_repository_update(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson = Lesson(name="Before Update", week_id=test_week.id, order_in_week=4, content_html="old")
        db_session.add(lesson)
        db_session.commit()
        update_dict = {"name": "After Update", "content_html": "new"}
        updated = repo.update(lesson.id, update_dict)
        assert updated.name == "After Update"
        assert updated.content_html == "new"


    def test_lesson_repository_delete(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson = Lesson(name="ToDelete", week_id=test_week.id, order_in_week=5, content_html="c")
        db_session.add(lesson)
        db_session.commit()
        result = repo.delete(lesson.id)
        assert result is True
        assert repo.get_by_id(lesson.id) is None


    def test_lesson_repository_get_by_week_id(self, db_session, test_week):
        repo = LessonRepository(db_session)
        lesson_a = Lesson(name="WeekLesson1", week_id=test_week.id, order_in_week=1, content_html="c1")
        lesson_b = Lesson(name="WeekLesson2", week_id=test_week.id, order_in_week=2, content_html="c2")
        db_session.add_all([lesson_a, lesson_b])
        db_session.commit()
        lessons = repo.get_by_week_id(test_week.id)
        assert len(lessons) == 2

        assert lessons[0].order_in_week == 1
        assert lessons[1].order_in_week == 2


    def test_lesson_repository_get_count(self, db_session, test_week):
        repo = LessonRepository(db_session)
        count_before = repo.get_count()
        lesson = Lesson(name="CountTest", week_id=test_week.id, order_in_week=10, content_html="c")
        db_session.add(lesson)
        db_session.commit()
        count_after = repo.get_count()
        assert count_after == count_before + 1


class TestWordRepository:

    def test_word_repository_get_all(self, db_session, test_week, test_lesson):
        repo = WordRepository(db_session)
        word1 = Word(hanzi="字1", transcription="zi1", translation="word1")
        word2 = Word(hanzi="字2", transcription="zi2", translation="word2")
        db_session.add_all([word1, word2])
        db_session.commit()
        repo.add_to_lesson(word1.id, test_lesson.id)
        all_words = repo.get_all()
        assert len(all_words) >= 2
        hanzi_list = [w.hanzi for w in all_words]
        assert "字1" in hanzi_list
        assert "字2" in hanzi_list


    def test_word_repository_get_by_id(self, db_session):
        repo = WordRepository(db_session)
        word = Word(hanzi="独", transcription="dú", translation="один")
        db_session.add(word)
        db_session.commit()
        found = repo.get_by_id(word.id)
        assert found.hanzi == "独"


    def test_word_repository_get_by_ids(self, db_session):
        repo = WordRepository(db_session)
        word1 = Word(hanzi="甲", transcription="jiǎ", translation="первый")
        word2 = Word(hanzi="乙", transcription="yǐ", translation="второй")
        db_session.add_all([word1, word2])
        db_session.commit()
        found = repo.get_by_ids([word1.id, word2.id])
        assert len(found) == 2
        ids = [w.id for w in found]
        assert word1.id in ids
        assert word2.id in ids


    def test_word_repository_get_by_lesson(self, db_session, test_week, test_lesson):
        repo = WordRepository(db_session)
        word = Word(hanzi="课", transcription="kè", translation="урок")
        db_session.add(word)
        db_session.commit()
        repo.add_to_lesson(word.id, test_lesson.id)
        words = repo.get_by_lesson(test_lesson.id)
        assert len(words) == 1
        assert words[0].hanzi == "课"


    def test_word_repository_get_lesson_ids(self, db_session, test_week, test_lesson):
        repo = WordRepository(db_session)
        word = Word(hanzi="关联", transcription="guānlián", translation="связь")
        db_session.add(word)
        db_session.commit()
        repo.add_to_lesson(word.id, test_lesson.id)
        lesson_ids = repo.get_lesson_ids(word.id)
        assert len(lesson_ids) == 1
        assert lesson_ids[0] == test_lesson.id


    def test_word_repository_create(self, db_session):
        repo = WordRepository(db_session)
        data = {
            "hanzi": "新",
            "transcription": "xīn",
            "translation": "новый",
            "audio_url": "/static/audio/xin.mp3"
        }
        word = repo.create(data)
        assert word.id is not None
        assert word.hanzi == "新"
        assert word.translation == "новый"


    def test_word_repository_update(self, db_session):
        repo = WordRepository(db_session)
        word = Word(hanzi="旧", transcription="jiù", translation="старый")
        db_session.add(word)
        db_session.commit()
        update_dict = {"translation": "древний", "hanzi": "古"}
        updated = repo.update(word.id, update_dict)
        assert updated.hanzi == "古"
        assert updated.translation == "древний"


    def test_word_repository_delete(self, db_session):
        repo = WordRepository(db_session)
        word = Word(hanzi="删除", transcription="shānchú", translation="удалить")
        db_session.add(word)
        db_session.commit()
        result = repo.delete(word.id)
        assert result is True
        assert repo.get_by_id(word.id) is None


    def test_word_repository_add_to_lesson(self, db_session, test_week, test_lesson):
        repo = WordRepository(db_session)
        word = Word(hanzi="增加", transcription="zēngjiā", translation="добавить")
        db_session.add(word)
        db_session.commit()
        result = repo.add_to_lesson(word.id, test_lesson.id)
        assert result is True
        words = repo.get_by_lesson(test_lesson.id)
        assert any(w.id == word.id for w in words)


    def test_word_repository_remove_from_lesson(self, db_session, test_week, test_lesson):
        repo = WordRepository(db_session)
        word = Word(hanzi="移除", transcription="yíchú", translation="удалить из урока")
        db_session.add(word)
        db_session.commit()
        repo.add_to_lesson(word.id, test_lesson.id)
        assert len(repo.get_by_lesson(test_lesson.id)) == 1
        result = repo.remove_from_lesson(word.id, test_lesson.id)
        assert result is True
        assert len(repo.get_by_lesson(test_lesson.id)) == 0


class TestExerciseRepository:
    def test_exercise_repository_get_all(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        ex1 = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc1",
            question_text="text1",
            option_1="a1", option_2="a2", option_3="a3", option_4="a4",
            correct_answer=1,
            order_in_lesson=1
        )
        ex2 = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc2",
            question_text="text2",
            option_1="b1", option_2="b2", option_3="b3", option_4="b4",
            correct_answer=2,
            order_in_lesson=2
        )
        db_session.add_all([ex1, ex2])
        db_session.commit()
        all_ex = repo.get_all()
        assert len(all_ex) >= 2
        texts = [e.question_text for e in all_ex]
        assert "text1" in texts
        assert "text2" in texts


    def test_exercise_repository_get_by_lesson(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        ex = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc",
            question_text="qtext",
            option_1="o1", option_2="o2", option_3="o3", option_4="o4",
            correct_answer=1,
            order_in_lesson=5
        )
        db_session.add(ex)
        db_session.commit()
        exercises = repo.get_by_lesson(test_lesson.id)
        assert len(exercises) == 1
        assert exercises[0].question_text == "qtext"
        # Проверка сортировки по order_in_lesson
        ex2 = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc2",
            question_text="qtext2",
            option_1="x1", option_2="x2", option_3="x3", option_4="x4",
            correct_answer=2,
            order_in_lesson=1
        )
        db_session.add(ex2)
        db_session.commit()
        exercises = repo.get_by_lesson(test_lesson.id)
        assert exercises[0].order_in_lesson == 1
        assert exercises[1].order_in_lesson == 5


    def test_exercise_repository_get_by_id(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        ex = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc",
            question_text="get_by_id",
            option_1="1", option_2="2", option_3="3", option_4="4",
            correct_answer=3,
            order_in_lesson=1
        )
        db_session.add(ex)
        db_session.commit()
        found = repo.get_by_id(ex.id)
        assert found.question_text == "get_by_id"
        assert found.correct_answer == 3


    def test_exercise_repository_get_count_by_lesson(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        count_before = repo.get_count_by_lesson(test_lesson.id)
        ex = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc",
            question_text="text",
            option_1="a", option_2="b", option_3="c", option_4="d",
            correct_answer=1,
            order_in_lesson=1
        )
        db_session.add(ex)
        db_session.commit()
        count_after = repo.get_count_by_lesson(test_lesson.id)
        assert count_after == count_before + 1


    def test_exercise_repository_create(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        data = ExerciseCreate(
            lesson_id=test_lesson.id,
            question_description="Create desc",
            question_text="Create text",
            option_1="c1", option_2="c2", option_3="c3", option_4="c4",
            correct_answer=4,
            explanation="explanation",
            order_in_lesson=10
        )
        ex = repo.create(data)
        assert ex.id is not None
        assert ex.question_text == "Create text"
        assert ex.correct_answer == 4
        assert ex.explanation == "explanation"


    def test_exercise_repository_update(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        ex = Exercise(
            lesson_id=test_lesson.id,
            question_description="old desc",
            question_text="old text",
            option_1="o1", option_2="o2", option_3="o3", option_4="o4",
            correct_answer=2,
            order_in_lesson=1
        )
        db_session.add(ex)
        db_session.commit()
        update_dict = {"question_text": "new text", "correct_answer": 1}
        updated = repo.update(ex.id, update_dict)
        assert updated.question_text == "new text"
        assert updated.correct_answer == 1
        assert updated.question_description == "old desc"


    def test_exercise_repository_delete(self, db_session, test_lesson):
        repo = ExerciseRepository(db_session)
        ex = Exercise(
            lesson_id=test_lesson.id,
            question_description="desc",
            question_text="delete me",
            option_1="1", option_2="2", option_3="3", option_4="4",
            correct_answer=1,
            order_in_lesson=1
        )
        db_session.add(ex)
        db_session.commit()
        result = repo.delete(ex.id)
        assert result is True
        assert repo.get_by_id(ex.id) is None


class TestArticleRepository:

    def test_article_repository_create(self, db_session):
        repo = ArticleRepository(db_session)
        data = ArticleCreate(
            name="Test Article",
            slug="test-article",
            description="Short description",
            text="Full text of the article",
            images=["/static/img1.jpg", "/static/img2.jpg"]
        )
        article = repo.create(data)
        assert article.id is not None
        assert article.name == "Test Article"
        assert article.slug == "test-article"
        assert article.images == ["/static/img1.jpg", "/static/img2.jpg"]


    def test_article_repository_get_by_id(self, db_session):
        repo = ArticleRepository(db_session)
        article = Article(
            name="Get by ID",
            slug="get-by-id",
            description="desc",
            text="text",
            images=[]
        )
        db_session.add(article)
        db_session.commit()
        found = repo.get_by_id(article.id)
        assert found.name == "Get by ID"
        assert found.slug == "get-by-id"


    def test_article_repository_get_by_slug(self, db_session):
        repo = ArticleRepository(db_session)
        article = Article(
            name="Unique Slug",
            slug="unique-slug-test",
            description="desc",
            text="text",
            images=[]
        )
        db_session.add(article)
        db_session.commit()
        found = repo.get_by_slug("unique-slug-test")
        assert found.id == article.id
        assert found.name == "Unique Slug"


    def test_article_repository_get_all(self, db_session):
        repo = ArticleRepository(db_session)
        article1 = Article(name="A1", slug="a1", description="d1", text="t1", images=[])
        article2 = Article(name="A2", slug="a2", description="d2", text="t2", images=[])
        db_session.add_all([article1, article2])
        db_session.commit()
        all_articles = repo.get_all()
        assert len(all_articles) >= 2
        slugs = [a.slug for a in all_articles]
        assert "a1" in slugs
        assert "a2" in slugs


    def test_article_repository_update(self, db_session):
        repo = ArticleRepository(db_session)
        article = Article(
            name="Old Name",
            slug="old-slug",
            description="old desc",
            text="old text",
            images=[]
        )
        db_session.add(article)
        db_session.commit()
        update_data = {
            "name": "New Name",
            "description": "new desc",
            "images": ["/static/new.jpg"]
        }
        updated = repo.update(article.id, update_data)
        assert updated.name == "New Name"
        assert updated.description == "new desc"
        assert updated.images == ["/static/new.jpg"]
        assert updated.slug == "old-slug"
        assert updated.text == "old text"


    def test_article_repository_delete(self, db_session):
        repo = ArticleRepository(db_session)
        article = Article(
            name="Delete Me",
            slug="delete-me",
            description="desc",
            text="text",
            images=[]
        )
        db_session.add(article)
        db_session.commit()
        result = repo.delete(article.id)
        assert result is True
        assert repo.get_by_id(article.id) is None