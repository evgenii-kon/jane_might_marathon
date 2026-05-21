from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from app.repositories.user_lesson_progress_repository import (
    UserLessonProgressRepository,
)
from app.repositories.lesson_repository import LessonRepository
from app.schemas.user_lesson_progress import (
    UserLessonProgressResponse,
    LessonWithProgressResponse,
    WeekProgressSummary,
    UserTotalProgressResponse,
)


class UserLessonProgressService:
    """Сервис для управления прогрессом пользователя по урокам"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserLessonProgressRepository(db)
        self.lesson_repository = LessonRepository(db)


    def mark_lesson_as_completed(
        self, user_id: int, lesson_id: int
    ) -> UserLessonProgressResponse:
        """Отметить урок как пройденный"""
        lesson = self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(404, f"Lesson {lesson_id} not found")

        if self.is_lesson_completed(user_id, lesson_id):
            raise HTTPException(400, f"Lesson {lesson_id} already completed")

        progress = self.repository.mark_completed(user_id, lesson_id)
        return UserLessonProgressResponse.model_validate(progress)


    def mark_lesson_as_started(
        self, user_id: int, lesson_id: int
    ) -> UserLessonProgressResponse:
        """Отметить урок как начатый"""
        lesson = self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(404, f"Lesson {lesson_id} not found")

        progress = self.repository.mark_started(user_id, lesson_id)
        return UserLessonProgressResponse.model_validate(progress)


    def is_lesson_started(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, начат ли урок"""
        return self.repository.is_started(user_id, lesson_id)


    def is_lesson_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли урок"""
        return self.repository.is_completed(user_id, lesson_id)


    def get_next_lesson_in_week(
        self, week_id: int, current_order: int
    ) -> Optional[LessonWithProgressResponse]:
        """Получить следующий урок в неделе"""
        lessons = self.lesson_repository.get_by_week_id(week_id)

        for lesson in lessons:
            if lesson.order_in_week == current_order + 1:
                return LessonWithProgressResponse(
                    id=lesson.id,
                    name=lesson.name,
                    week_id=lesson.week_id,
                    order_in_week=lesson.order_in_week,
                    description=getattr(lesson, "description", None),
                    content_html=lesson.content_html,
                    video_url=lesson.video_url,
                    is_started=False,
                    is_completed=False,
                )
        return None

    def get_user_total_progress(self, user_id: int) -> UserTotalProgressResponse:
        """Получить общий прогресс пользователя по урокам"""
        completed_lessons = self.repository.get_completed_lesson_ids(user_id)
        all_lessons = self.lesson_repository.get_all()

        total = len(all_lessons)
        completed = len(completed_lessons)
        progress_percent = int((completed / total) * 100) if total > 0 else 0

        return UserTotalProgressResponse(
            total_lessons=total,
            completed_lessons=completed,
            started_lessons=0,
            progress_percent=progress_percent,
        )


    def get_week_progress(self, user_id: int, week_id: int) -> WeekProgressSummary:
        """Получить прогресс по урокам в конкретной неделе"""
        lessons = self.lesson_repository.get_by_week_id(week_id)
        completed_count = self.repository.get_completed_count_by_week(user_id, week_id)

        week = lessons[0].week if lessons else None
        week_number = week.number if week else 0
        week_title = week.short_description if week else ""
        progress_percent = int((completed_count / len(lessons)) * 100) if lessons else 0

        return WeekProgressSummary(
            week_id=week_id,
            week_number=week_number,
            week_title=week_title,
            total_lessons=len(lessons),
            completed_lessons=completed_count,
            started_lessons=0,
            progress_percent=progress_percent,
            is_week_completed=completed_count == len(lessons) if lessons else False,
        )

    def get_completed_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID пройденных уроков пользователя"""
        return self.repository.get_completed_lesson_ids(user_id)


    def get_started_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID начатых уроков пользователя"""
        return self.repository.get_started_lesson_ids(user_id)


    def get_completed_count_by_user(self, user_id: int) -> int:
        """Получить количество пройденных уроков пользователя"""
        return self.repository.get_completed_count_by_user(user_id)


    def get_completed_count_by_week(self, user_id: int, week_id: int) -> int:
        """Получить количество пройденных уроков в неделе"""
        return self.repository.get_completed_count_by_week(user_id, week_id)


    def get_lessons_with_progress(
        self, user_id: int, week_id: int
    ) -> List[LessonWithProgressResponse]:
        """Получить уроки недели с прогрессом пользователя"""
        lessons = self.lesson_repository.get_by_week_id(week_id)
        completed_ids = self.repository.get_completed_lesson_ids(user_id)
        started_ids = self.repository.get_started_lesson_ids(user_id)

        result = []
        for lesson in lessons:
            result.append(
                LessonWithProgressResponse(
                    id=lesson.id,
                    name=lesson.name,
                    week_id=lesson.week_id,
                    order_in_week=lesson.order_in_week,
                    description=getattr(lesson, "description", None),
                    content_html=lesson.content_html,
                    video_url=lesson.video_url,
                    is_started=lesson.id in started_ids,
                    is_completed=lesson.id in completed_ids,
                )
            )
        return result
