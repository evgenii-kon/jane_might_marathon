from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserExerciseProgressBase(BaseModel):
    user_id: int
    exercise_id: int
    is_completed: bool = False
    completed_at: Optional[datetime] = None


class UserExerciseProgressCreate(UserExerciseProgressBase):
    pass


class UserExerciseProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None


class UserExerciseProgressResponse(UserExerciseProgressBase):
    id: int

    class Config:
        from_attributes = True


class LessonExerciseProgressResponse(BaseModel):
    total: int
    completed: int
    percent: float
