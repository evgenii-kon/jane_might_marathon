from sqlalchemy.orm import Session
from typing import List
from app.repositories.user_word_progress_repository import UserWordProgressRepository
from app.repositories.word_repository import WordRepository
from app.models.word import Word
from app.models.user_word_progress import UserWordProgress
from ..schemas.word import WordResponse


class WordTrainerService:
    """Сервис для тренажёра слов"""
    
    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = UserWordProgressRepository(db)
        self.word_repo = WordRepository(db)


    def get_daily_session(self, user_id: int, limit: int = 30) -> List[UserWordProgress]:
        """Ежедневная сессия — слова для повторения сегодня"""
        return self.progress_repo.get_words_for_review(user_id, limit)


    def get_all_words_session(self, user_id: int) -> List[WordResponse]:
        """Режим "Все слова" — просто все слова"""
        words = self.word_repo.get_all()
        return [WordResponse.model_validate(word) for word in words]


    def get_mastery_stats(self, user_id: int) -> dict:
        """Статистика по уровням мастерства"""
        return self.progress_repo.get_mastery_stats(user_id)


    def get_due_count(self, user_id: int) -> int:
        """Количество слов для повторения сегодня"""
        return self.progress_repo.get_review_count_today(user_id)


    def get_total_words_count(self) -> int:
        """Общее количество слов в базе"""
        return len(self.word_repo.get_all())