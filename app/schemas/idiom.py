from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from pydantic_settings import SettingsConfigDict


class IdiomCreate(BaseModel):
    hanzi: str = Field(..., max_length=20)
    pinyin: str = Field(..., max_length=100)
    translate: str = Field(..., max_length=500)
    meaning: str
    story: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)


class IdiomUpdate(BaseModel):
    hanzi: Optional[str] = Field(None, max_length=20)
    pinyin: Optional[str] = Field(None, max_length=100)
    translate: Optional[str] = Field(None, max_length=500)
    meaning: Optional[str] = None
    story: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)


class IdiomResponse(BaseModel):
    id: int
    hanzi: str
    pinyin: str
    translate: str
    meaning: str
    story: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = SettingsConfigDict(from_attributes=True)
