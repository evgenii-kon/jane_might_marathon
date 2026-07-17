from pydantic import BaseModel
from typing import Optional
from pydantic_settings import SettingsConfigDict

NOVEL_LINE_TYPES = ("narrative", "dialogue")


class NovelLineCreate(BaseModel):
    lesson_id: int
    order: int = 0
    type: str
    character: Optional[str] = None
    speaker: Optional[str] = None
    text: str
    side: Optional[str] = None


class NovelLineUpdate(BaseModel):
    order: Optional[int] = None
    type: Optional[str] = None
    character: Optional[str] = None
    speaker: Optional[str] = None
    text: Optional[str] = None
    side: Optional[str] = None


class NovelLineResponse(BaseModel):
    id: int
    lesson_id: int
    order: int
    type: str
    character: Optional[str] = None
    speaker: Optional[str] = None
    text: str
    side: Optional[str] = None

    model_config = SettingsConfigDict(from_attributes=True)
