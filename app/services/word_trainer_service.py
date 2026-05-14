from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.repositories.user_word_progress_repository import UserWordProgressRepository
from app.repositories.word_repository import WordRepository
from app.repositories.lesson_word_association_repository import LessonWordAssociationRepository
from app.models.word import Word
from app.models.user_word_progress import UserWordProgress


class WordTrainerService:
    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = UserWordProgressRepository(db)
        self.word_repo = WordRepository(db)
        self.lesson_word_repo = LessonWordAssociationRepository(db)


    def add_lesson_words_to_progress(self, user_id: int, lesson_id: int) -> int:
        """
        Добавить все слова урока в прогресс пользователя (если ещё не добавлены)
        """
        word_ids = self.lesson_word_repo.get_word_ids_by_lesson(lesson_id)
        
        if not word_ids:
            print(f"В уроке {lesson_id} нет слов")
            return 0
        
        existing_word_ids = self.progress_repo.get_existing_word_ids(user_id)
        
        new_word_ids = [wid for wid in word_ids if wid not in existing_word_ids]
        
        if new_word_ids:
            added_count = self.progress_repo.create_many(user_id, new_word_ids)
            print(f"✅ Добавлено {added_count} новых слов из урока {lesson_id} для пользователя {user_id}")
            return added_count
        
        print(f"Все слова урока {lesson_id} уже есть в прогрессе пользователя {user_id}")
        return 0


    def get_daily_session(self, user_id: int, limit: int = 30) -> List[UserWordProgress]:
        """
        Получить слова для ежедневного повторения
        """
        return self.progress_repo.get_words_for_review(user_id, limit)


    def get_due_count(self, user_id: int) -> int:
        """
        Получить количество слов, ожидающих повторения сегодня
        """
        return self.progress_repo.get_review_count_today(user_id)


    def get_all_words_session(self, user_id: int) -> List[Word]:
        """
        Получить все слова, которые есть в прогрессе пользователя
        (только из уроков, которые он открыл)
        """
        word_ids = self.progress_repo.get_existing_word_ids(user_id)
        if not word_ids:
            return []
        return self.word_repo.get_by_ids(word_ids)


    def update_mastery(self, user_id: int, word_id: int, is_correct: bool) -> UserWordProgress:
        """
        Обновить уровень владения словом после ответа пользователя
        """
        return self.progress_repo.update_mastery(user_id, word_id, is_correct)


    def get_mastery_stats(self, user_id: int) -> dict:
        """
        Получить статистику уровней mastery пользователя
        """
        return self.progress_repo.get_mastery_stats(user_id)


    def get_review_count_today(self, user_id: int) -> int:
        """
        Получить количество слов, запланированных на повторение сегодня
        """
        return self.progress_repo.get_review_count_today(user_id)
    

    def get_total_words_count(self, user_id: int) -> int:
        """
        Получить общее количество слов в прогрессе пользователя
        (все слова из уроков, которые он открыл)
        """
        word_ids = self.progress_repo.get_existing_word_ids(user_id)
        return len(word_ids)