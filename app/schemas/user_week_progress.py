from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserWeekProgressBase(BaseModel):
    user_id: int
    week_id: int
    opens_at: datetime
    is_completed: bool = False
    completed_at: Optional[datetime] = None


class UserWeekProgressCreate(BaseModel):
    user_id: int
    week_id: int
    opens_at: datetime


class UserWeekProgressUpdate(BaseModel):
    opens_at: Optional[datetime] = None
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None


class UserWeekProgressResponse(UserWeekProgressBase):
    id: int

    class Config:
        from_attributes = True


class WeekWithProgressResponse(BaseModel):
    """Для отображения недели с прогрессом пользователя"""

    id: int
    number: int
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    is_locked: bool
    is_completed: bool
    days_until_open: Optional[int] = None
    opens_at: Optional[datetime] = None
    progress_percent: float = 0

    class Config:
        from_attributes = True
