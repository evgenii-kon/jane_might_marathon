from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.lesson import LessonResponse


class WeekCreate(BaseModel):
    slug: str = Field(..., min_length=3, max_length=100)
    short_description: str = Field(..., min_length=10, max_length=200)
    long_description: str = Field(..., min_length=20)
    number: int = Field(..., ge=1, le=50)
    target_words_count: int = Field(0, ge=0)
    target_exercises_count: int = Field(0, ge=0)


class WeekUpdate(BaseModel):
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    short_description: Optional[str] = Field(None, min_length=10, max_length=200)
    long_description: Optional[str] = Field(None, min_length=20)
    number: Optional[int] = Field(None, ge=1, le=50)
    target_words_count: Optional[int] = Field(None, ge=0)
    target_exercises_count: Optional[int] = Field(None, ge=0)

    class Config:
        from_attributes = True


class WeekResponse(BaseModel):
    id: int
    slug: str
    short_description: str
    long_description: str
    number: int
    target_words_count: int
    target_exercises_count: int
    lessons: list[LessonResponse]

    class Config:
        from_attributes = True
