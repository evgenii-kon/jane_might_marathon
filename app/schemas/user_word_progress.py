from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic_settings import SettingsConfigDict


class UserWordProgressBase(BaseModel):
    mastery_level: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None


class UserWordProgressCreate(BaseModel):
    user_id: int
    word_id: int


class UserWordProgressUpdate(BaseModel):
    mastery_level: Optional[int] = None
    correct_count: Optional[int] = None
    wrong_count: Optional[int] = None
    last_reviewed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None


class UserWordProgressResponse(UserWordProgressBase):
    id: int
    user_id: int
    word_id: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes = True)



# Схемы для тренажёра
class TrainerWordData(BaseModel):
    """Данные слова для тренажёра (с прогрессом)"""

    id: int
    hanzi: str
    transcription: str
    translation: str
    example: Optional[str] = None
    part_of_speech: Optional[str] = None
    audio_url: Optional[str] = None
    mastery_level: int = 0
    next_review_at: Optional[datetime] = None

    model_config = SettingsConfigDict(from_attributes = True)



class CheckAnswerRequest(BaseModel):
    word_id: int
    user_answer: str


class CheckAnswerResponse(BaseModel):
    is_correct: bool
    correct_translation: str
    transcription: str
    example: Optional[str] = None
    new_mastery_level: int
    next_review_days: int  # через сколько дней повторить


class TrainerSessionResponse(BaseModel):
    word_id: int
    hanzi: str
    transcription: str
    translation: str
    example: Optional[str] = None
    user_progress: Optional[UserWordProgressResponse] = None


class TrainerSessionData(BaseModel):
    """Сессия тренажёра (список слов + статистика)"""

    words: List[TrainerWordData]
    due_today_count: int  # сколько слов нужно повторить сегодня
    total_words: int  # всего слов в базе
    mastered_count: int  # слов на уровне 5
    new_words_count: int  # новых слов (уровень 0)

    model_config = SettingsConfigDict(from_attributes = True)

