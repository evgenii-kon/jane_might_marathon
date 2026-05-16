from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.models.user_week_progress import UserWeekProgress


class UserWeekProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_week(
        self, user_id: int, week_id: int
    ) -> Optional[UserWeekProgress]:
        """Получить прогресс пользователя по конкретной неделе"""
        return (
            self.db.query(UserWeekProgress)
            .filter(
                UserWeekProgress.user_id == user_id, UserWeekProgress.week_id == week_id
            )
            .first()
        )

    def get_by_user(self, user_id: int) -> List[UserWeekProgress]:
        """Получить весь прогресс пользователя по неделям"""
        return (
            self.db.query(UserWeekProgress)
            .filter(UserWeekProgress.user_id == user_id)
            .all()
        )

    def create(
        self, user_id: int, week_id: int, opens_at: datetime
    ) -> UserWeekProgress:
        """Создать запись прогресса для недели"""
        progress = UserWeekProgress(user_id=user_id, week_id=week_id, opens_at=opens_at)
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def create_many(self, user_id: int, weeks_opens_at: List[tuple]) -> int:
        """Создать записи прогресса для нескольких недель сразу"""
        progresses = []
        for week_id, opens_at in weeks_opens_at:
            progress = UserWeekProgress(
                user_id=user_id, week_id=week_id, opens_at=opens_at
            )
            progresses.append(progress)

        self.db.add_all(progresses)
        self.db.commit()
        return len(progresses)

    def update(self, progress_id: int, update_data: dict) -> Optional[UserWeekProgress]:
        """Обновить прогресс"""
        progress = (
            self.db.query(UserWeekProgress)
            .filter(UserWeekProgress.id == progress_id)
            .first()
        )

        if not progress:
            return None

        for key, value in update_data.items():
            setattr(progress, key, value)

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def mark_completed(self, user_id: int, week_id: int) -> Optional[UserWeekProgress]:
        """Отметить неделю как пройденную"""
        progress = self.get_by_user_and_week(user_id, week_id)
        if progress and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(progress)
        return progress

    def get_completed_week_ids(self, user_id: int) -> List[int]:
        """Получить ID всех пройденных недель"""
        results = (
            self.db.query(UserWeekProgress.week_id)
            .filter(
                UserWeekProgress.user_id == user_id,
                UserWeekProgress.is_completed == True,
            )
            .all()
        )
        return [r[0] for r in results]
