from pydantic import BaseModel, Field
from typing import Optional, List


class WordCreate(BaseModel):
    hanzi: str = Field(..., min_length=1, max_length=100)
    transcription: str = Field(..., min_length=1, max_length=100)
    translation: str = Field(..., min_length=1, max_length=255)
    part_of_speech: Optional[str] = Field(None, max_length=50)
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)


class WordUpdate(BaseModel):
    hanzi: Optional[str] = Field(None, min_length=1, max_length=100)
    transcription: Optional[str] = Field(None, min_length=1, max_length=100)
    translation: Optional[str] = Field(None, min_length=1, max_length=255)
    part_of_speech: Optional[str] = Field(None, max_length=50)
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class WordResponse(BaseModel):
    id: int
    hanzi: str = Field(..., min_length=1, max_length=100)
    transcription: str = Field(..., min_length=1, max_length=100)
    translation: str = Field(..., min_length=1, max_length=255)
    part_of_speech: Optional[str] = Field(None, max_length=50)
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class WordWithLessonsResponse(BaseModel):
    id: int
    hanzi: str = Field(..., min_length=1, max_length=100)
    transcription: str = Field(..., min_length=1, max_length=100)
    translation: str = Field(..., min_length=1, max_length=255)
    part_of_speech: Optional[str] = Field(None, max_length=50)
    example_sentence: Optional[str] = None
    example_translation: Optional[str] = None
    audio_url: Optional[str] = Field(None, max_length=500)
    lesson_ids: List[int] = []

    class Config:
        from_attributes = True