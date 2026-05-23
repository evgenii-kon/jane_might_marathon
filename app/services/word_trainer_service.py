from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.repositories.user_word_progress_repository import UserWordProgressRepository
from app.repositories.word_repository import WordRepository
from app.repositories.lesson_word_association_repository import (
    LessonWordAssociationRepository,
)
from app.models.word import Word
from app.models.user_word_progress import UserWordProgress


class WordTrainerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_repo = UserWordProgressRepository(db)
        self.word_repo = WordRepository(db)
        self.lesson_word_repo = LessonWordAssociationRepository(db)

    async def add_lesson_words_to_progress(self, user_id: int, lesson_id: int) -> int:
        """
        Добавить все слова урока в прогресс пользователя (если ещё не добавлены)
        """
        word_ids = await self.lesson_word_repo.get_word_ids_by_lesson(lesson_id)

        if not word_ids:
            print(f"В уроке {lesson_id} нет слов")
            return 0

        existing_word_ids = await self.progress_repo.get_existing_word_ids(user_id)

        new_word_ids = [wid for wid in word_ids if wid not in existing_word_ids]

        if new_word_ids:
            added_count = await self.progress_repo.create_many(user_id, new_word_ids)
            print(
                f"✅ Добавлено {added_count} новых слов из урока {lesson_id} для пользователя {user_id}"
            )
            return added_count

        print(
            f"Все слова урока {lesson_id} уже есть в прогрессе пользователя {user_id}"
        )
        return 0

    async def get_daily_session(
        self, user_id: int, limit: int = 30
    ) -> List[UserWordProgress]:
        """
        Получить слова для ежедневного повторения
        """
        return await self.progress_repo.get_words_for_review(user_id, limit)

    async def get_due_count(self, user_id: int) -> int:
        """
        Получить количество слов, ожидающих повторения сегодня
        """
        return await self.progress_repo.get_review_count_today(user_id)

    async def get_all_words_session(self, user_id: int) -> List[Word]:
        """
        Получить все слова
        """
        words = await self.word_repo.get_all()
        return words

    async def update_mastery(
        self, user_id: int, word_id: int, is_correct: bool
    ) -> UserWordProgress:
        """
        Обновить уровень владения словом после ответа пользователя
        """
        return await self.progress_repo.update_mastery(user_id, word_id, is_correct)

    async def get_mastery_stats(self, user_id: int) -> dict:
        """
        Получить статистику уровней mastery пользователя
        """
        return await self.progress_repo.get_mastery_stats(user_id)

    async def get_review_count_today(self, user_id: int) -> int:
        """
        Получить количество слов, запланированных на повторение сегодня
        """
        return await self.progress_repo.get_review_count_today(user_id)

    async def get_total_words_count(self, user_id: int) -> int:
        """
        Получить общее количество слов в прогрессе пользователя
        (все слова из уроков, которые он открыл)
        """
        word_ids = await self.progress_repo.get_existing_word_ids(user_id)
        return len(word_ids)

    async def get_word_ranking(self, user_id: int) -> List[dict]:
        """Возвращает список всех слов с прогрессом пользователя (mastery, correct/wrong)"""
        all_words = await self.word_repo.get_all()
        progresses = await self.progress_repo.get_all_by_user(user_id)
        progress_map = {p.word_id: p for p in progresses}

        ranking = []
        for word in all_words:
            prog = progress_map.get(word.id)
            ranking.append({
                'id': word.id,
                'hanzi': word.hanzi,
                'transcription': word.transcription,
                'translation': word.translation,
                'mastery_level': prog.mastery_level if prog else 0,
                'correct_count': prog.correct_count if prog else 0,
                'wrong_count': prog.wrong_count if prog else 0,
                'audio_url': word.audio_url,
            })
        # Сортировка по mastery (по убыванию)
        ranking.sort(key=lambda x: x['mastery_level'], reverse=True)
        return ranking