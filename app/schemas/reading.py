from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pydantic_settings import SettingsConfigDict


class ReadingQuestionCreate(BaseModel):
    question: str = Field(..., max_length=500)
    option_1: str = Field(..., max_length=255)
    option_2: str = Field(..., max_length=255)
    option_3: str = Field(..., max_length=255)
    option_4: str = Field(..., max_length=255)
    correct_answer: int = Field(..., ge=1, le=4)
    explanation: Optional[str] = Field(None, max_length=500)
    order_in_text: int = Field(default=0)


class ReadingQuestionResponse(BaseModel):
    id: int
    text_id: int
    question: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: int
    explanation: Optional[str] = None
    order_in_text: int

    model_config = SettingsConfigDict(from_attributes=True)


class ReadingTextCreate(BaseModel):
    title: str = Field(..., max_length=255, min_length=2)
    slug: str = Field(..., max_length=255, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    content_hanzi: str = Field(..., min_length=1)
    content_pinyin: Optional[str] = None
    content_translation: Optional[str] = None
    hsk_level: Optional[str] = Field(None, max_length=20)
    week_id: Optional[int] = None


class ReadingTextUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    content_hanzi: Optional[str] = None
    content_pinyin: Optional[str] = None
    content_translation: Optional[str] = None
    hsk_level: Optional[str] = Field(None, max_length=20)
    week_id: Optional[int] = None


class ReadingTextResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    content_hanzi: str
    content_pinyin: Optional[str] = None
    content_translation: Optional[str] = None
    hsk_level: Optional[str] = None
    week_id: Optional[int] = None
    created_at: datetime
    questions: List[ReadingQuestionResponse] = []

    model_config = SettingsConfigDict(from_attributes=True)


class ReadingCheckAnswer(BaseModel):
    question_id: int
    selected: int  # 1/2/3/4


class ReadingCheckResult(BaseModel):
    score: int
    total: int
    results: List[dict]  # [{question_id, correct, correct_answer, explanation}]
