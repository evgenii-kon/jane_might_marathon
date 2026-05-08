from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.models.user_word_progress import UserWordProgress


class UserWordProgressRepository:
    MASTERY_INTERVALS = {
        0: 1,   # не изучено
        1: 3,   # новичок
        2: 7,   # ученик
        3: 14,  # знаю
        4: 30,  # хорошо
        5: 60   # мастер
    }


    def __init__ (self, db):
        self.db = db


    def get_or_create(self, user_id: int, word_id: int) -> UserWordProgress:
        progress = self.db.query(UserWordProgress).filter(
            UserWordProgress.user_id == user_id,
            UserWordProgress.Word_id == word_id
        ).first()

        if not progress:
            progress = UserWordProgress(
                user_id=user_id,
                word_id=word_id,
                next_review_at=datetime.now(timezone.utc)
            )

        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)

        return progress
    

    def update_mastery(self, user_id: int, word_id: int, is_correct: bool) -> UserWordProgress:
        progress = self.get_or_create(user_id, word_id)

        if is_correct:
            progress.correct_count += 1
            progress.mastery_level = min(5, progress.mastery_level + 1)
        else:
            progress.wrong_count += 1
            progress.mastery_level = max(0, progress.mastery_level - 1)

        interval_days = self.MASTERY_INTERVALS.get(progress.mastery_level, 1)
        progress.last_reviewed_at = datetime.now(timezone.utc)
        progress.next_review_at = datetime.now(timezone.utc) + timedelta(days=interval_days)

        self.db.commit()
        self.db.refresh(progress)
        return progress
    

    def get_words_for_review(self, user_id: int, limit: int = 30) -> List[UserWordProgress]:
        now = datetime.now(timezone.utc)
        results = self.db.query(UserWordProgress).filter(
            UserWordProgress.user_id==user_id,
            UserWordProgress.next_review_at<=now
        ).order_by(UserWordProgress.next_review_at.asc()).limit(limit).all()

        return results


    def get_all_by_user(self, user_id: int) -> List[UserWordProgress]:
        return self.db.query(UserWordProgress).filter(
            UserWordProgress.user_id==user_id
        ).all()
    

    def get_review_count_today(self, user_id: int) -> int:
        now = datetime.now(timezone.utc)
        return self.db.query(UserWordProgress).filter(
            UserWordProgress.user_id==user_id,
            UserWordProgress.next_review_at<=now
        ).count()


    def get_mastery_stats(self, user_id: int) -> dict:
        results = self.db.query(UserWordProgress.mastery_level).filter(
            UserWordProgress.user_id == user_id
        ).all()
        
        stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for (level,) in results:
            stats[level] = stats.get(level, 0) + 1
        
        return stats