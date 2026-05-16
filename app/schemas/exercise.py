from pydantic import BaseModel
from typing import Optional


class ExerciseCreate(BaseModel):
    lesson_id: int
    question_description: str
    question_text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: int
    explanation: Optional[str] = None
    order_in_lesson: int = 0


class ExerciseUpdate(BaseModel):
    lesson_id: Optional[int] = None
    question_description: Optional[str] = None
    question_text: Optional[str] = None
    option_1: Optional[str] = None
    option_2: Optional[str] = None
    option_3: Optional[str] = None
    option_4: Optional[str] = None
    correct_answer: Optional[int] = None
    explanation: Optional[str] = None
    order_in_lesson: Optional[int] = None


class ExerciseResponse(BaseModel):
    id: int
    lesson_id: int
    question_description: str
    question_text: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: int
    explanation: Optional[str] = None
    order_in_lesson: int

    class Config:
        from_attributes = True


class ExerciseCheckRequest(BaseModel):
    exercise_id: int
    selected_option: int


class ExerciseCheckResponse(BaseModel):
    is_correct: bool
    correct_answer: int
    explanation: Optional[str] = None
    user_answer: str
    correct_answer_text: str
