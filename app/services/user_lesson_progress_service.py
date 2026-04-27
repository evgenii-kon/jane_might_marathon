from sqlalchemy.orm import Session
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.repositories.user_lesson_progress_repository import UserLessonProgressRepository
from app.repositories.lesson_repository import LessonRepository


class UserLessonProgressService:
    """Сервис для управления прогрессом пользователя по урокам"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserLessonProgressRepository(db)
        self.lesson_repository = LessonRepository(db)


    def mark_lesson_as_completed(self, user_id: int, lesson_id: int) -> Dict[str, Any]:
        """Отметить урок как пройденный"""
        
        # Проверяем, существует ли урок
        lesson = self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id {lesson_id} not found"
            )
        
        # Проверяем, не пройден ли уже урок
        if self.is_lesson_completed(user_id, lesson_id):
            return {
                "status": "already_completed",
                "message": "Lesson already completed",
                "lesson_id": lesson_id
            }
        
        # Отмечаем урок пройденным
        progress = self.repository.mark_completed(user_id, lesson_id)
        
        # Получаем следующий урок
        next_lesson = self._get_next_lesson_in_week(lesson.week_id, lesson.order_in_week)
        
        return {
            "status": "completed",
            "message": "Lesson marked as completed",
            "lesson_id": lesson_id,
            "completed_at": progress.completed_at,
            "next_lesson": next_lesson
        }
    

    def mark_lesson_as_started(self, user_id: int, lesson_id: int) -> dict:
        """Отметить урок как начатый"""
        lesson = self.lesson_repository.get_by_id(lesson_id)
        if not lesson:
            raise HTTPException(404, "Lesson not found")
        
        self.repository.mark_started(user_id, lesson_id)
        
        return {
            "status": "started",
            "message": "Lesson started",
            "lesson_id": lesson_id
        }

    def is_lesson_started(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, начат ли урок"""
        return self.repository.is_started(user_id, lesson_id)


    def _get_next_lesson_in_week(self, week_id: int, current_order: int) -> Dict[str, Any] | None:
        """Получить следующий урок в неделе"""
        lessons = self.lesson_repository.get_by_week_id(week_id)
        
        for lesson in lessons:
            if lesson.order_in_week == current_order + 1:
                return {
                    "id": lesson.id,
                    "name": lesson.name,
                    "order_in_week": lesson.order_in_week
                }
        return None

    def get_user_lesson_progress(self, user_id: int) -> Dict[str, Any]:
        """Получить общий прогресс пользователя по урокам"""
        completed_lessons = self.repository.get_completed_lessons_by_user(user_id)
        all_lessons = self.lesson_repository.get_all()
        
        return {
            "total_lessons": len(all_lessons),
            "completed_lessons": len(completed_lessons),
            "completed_lesson_ids": completed_lessons,
            "progress_percent": int((len(completed_lessons) / len(all_lessons)) * 100) if all_lessons else 0
        }

    def get_week_lesson_progress(self, user_id: int, week_id: int) -> Dict[str, Any]:
        """Получить прогресс по урокам в конкретной неделе"""
        lessons = self.lesson_repository.get_by_week_id(week_id)
        completed_count = self.repository.get_completed_count_by_week(user_id, week_id)
        
        return {
            "week_id": week_id,
            "total_lessons": len(lessons),
            "completed_lessons": completed_count,
            "progress_percent": int((completed_count / len(lessons)) * 100) if lessons else 0,
            "is_week_completed": completed_count == len(lessons) if lessons else False
        }


    def is_lesson_completed(self, user_id: int, lesson_id: int) -> bool:
        """Проверить, пройден ли конкретный урок"""
        return self.repository.is_completed(user_id, lesson_id)


    def get_completed_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID пройденных уроков пользователя"""
        return self.repository.get_completed_lessons_by_user(user_id)
    

    def get_started_lesson_ids(self, user_id: int) -> List[int]:
        """Получить список ID пройденных уроков пользователя"""
        return self.repository.get_started_lessons_by_user(user_id)


    def get_completed_count_by_user(self, user_id: int) -> int:
        """Получить количество пройденных уроков пользователя"""
        return self.repository.get_completed_count_by_user(user_id)


    def get_completed_count_by_week(self, user_id: int, week_id: int) -> int:
        """Получить количество пройденных уроков в неделе"""
        return self.repository.get_completed_count_by_week(user_id, week_id)