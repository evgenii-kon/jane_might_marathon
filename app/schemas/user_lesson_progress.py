from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.lesson import LessonResponse


class UserLessonProgressBase(BaseModel):
    """Базовые поля прогресса урока"""

    is_started: bool = False
    is_completed: bool = False


class UserLessonProgressCreate(BaseModel):
    """Создание прогресса урока"""

    user_id: int
    lesson_id: int
    is_started: bool = False
    is_completed: bool = False


class UserLessonProgressUpdate(BaseModel):
    """Обновление прогресса урока (частичное)"""

    is_started: Optional[bool] = None
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None


class UserLessonProgressResponse(UserLessonProgressBase):
    """Ответ с данными прогресса урока"""

    id: int
    user_id: int
    lesson_id: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LessonWithProgressResponse(LessonResponse):
    """Урок с информацией о прогрессе пользователя"""

    is_started: bool = False
    is_completed: bool = False

    class Config:
        from_attributes = True


class WeekProgressSummary(BaseModel):
    """Сводка прогресса по неделе"""

    week_id: int
    week_number: int
    week_title: str
    total_lessons: int
    completed_lessons: int
    started_lessons: int
    progress_percent: int
    is_week_completed: bool

    class Config:
        from_attributes = True


class UserTotalProgressResponse(BaseModel):
    """Общий прогресс пользователя"""

    total_lessons: int
    completed_lessons: int
    started_lessons: int
    progress_percent: int

    class Config:
        from_attributes = True
