from pydantic import BaseModel
from typing import Optional, Any, List
from pydantic_settings import SettingsConfigDict

EXERCISE_TYPES = (
    "quiz",
    "choose_hanzi",
    "matching_pairs",
    "build_word",
    "fill_blank",
    "translate",
    "audio_quiz",
    "fill_blank_open",
    "multi_select",
)


class ExerciseCreate(BaseModel):
    lesson_id: Optional[int] = None
    type: str
    question_text: Optional[str] = None
    config: dict
    explanation: Optional[str] = None
    order_in_lesson: int = 0


class ExerciseUpdate(BaseModel):
    lesson_id: Optional[int] = None
    type: Optional[str] = None
    question_text: Optional[str] = None
    config: Optional[dict] = None
    explanation: Optional[str] = None
    order_in_lesson: Optional[int] = None


class ExerciseResponse(BaseModel):
    id: int
    lesson_id: Optional[int]
    type: str
    question_text: Optional[str]
    config: dict
    explanation: Optional[str] = None
    order_in_lesson: int

    model_config = SettingsConfigDict(from_attributes=True)


class ExerciseCheckRequest(BaseModel):
    exercise_id: int
    selected_option: Optional[int] = None
    user_answer: Optional[str] = None
    pairs: Optional[List[dict]] = None


class ExerciseCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: Optional[Any] = None
    explanation: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer_text: Optional[str] = None
