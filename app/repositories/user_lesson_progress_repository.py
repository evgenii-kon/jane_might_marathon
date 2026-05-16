from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.user_lesson_progress import UserLessonProgress
from app.models.lesson import Lesson


class UserLessonProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_lesson(
        self, user_id: int, lesson_id: int
    ) -> Optional[UserLessonProgress]:
        return (
            self.db.query(UserLessonProgress)
            .filter(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.lesson_id == lesson_id,
            )
            .first()
        )

    def create(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Создать запись прогресса (урок начат, но не пройден)"""
        progress = UserLessonProgress(
            user_id=user_id, lesson_id=lesson_id, is_completed=False, completed_at=None
        )
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def mark_completed(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Отметить урок как пройденный"""
        progress = self.get_by_user_and_lesson(user_id, lesson_id)

        if not progress:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=func.now(),
            )
            self.db.add(progress)
        else:
            progress.is_completed = True
            progress.completed_at = func.now()

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def mark_started(self, user_id: int, lesson_id: int) -> UserLessonProgress:
        """Отметить урок как начатый"""
        progress = self.get_by_user_and_lesson(user_id, lesson_id)

        if not progress:
            progress = UserLessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_started=True,
                is_completed=False,
            )
            self.db.add(progress)
        else:
            progress.is_started = True

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def is_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли урок"""
        progress = self.get_by_user_and_lesson(user_id, lesson_id)
        return progress is not None and progress.is_completed

    def is_started(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, начат ли урок"""
        progress = self.get_by_user_and_lesson(user_id, lesson_id)
        return progress is not None and progress.is_started

    def get_completed_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID пройденных уроков пользователя"""
        results = (
            self.db.query(UserLessonProgress.lesson_id)
            .filter(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_completed == True,
            )
            .all()
        )
        return [r[0] for r in results]

    def get_started_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID начатых уроков пользователя"""
        results = (
            self.db.query(UserLessonProgress.lesson_id)
            .filter(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_started == True,
            )
            .all()
        )
        return [r[0] for r in results]

    def get_completed_count_by_user(self, user_id: int) -> int:
        """Получить количество пройденных уроков пользователя"""
        return (
            self.db.query(func.count(UserLessonProgress.id))
            .filter(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.is_completed == True,
            )
            .scalar()
            or 0
        )

    def get_completed_count_by_week(self, user_id: int, week_id: int) -> int:
        """Получить количество пройденных уроков в конкретной неделе"""
        return (
            self.db.query(func.count(UserLessonProgress.id))
            .join(Lesson, Lesson.id == UserLessonProgress.lesson_id)
            .filter(
                UserLessonProgress.user_id == user_id,
                Lesson.week_id == week_id,
                UserLessonProgress.is_completed == True,
            )
            .scalar()
            or 0
        )
