from pydantic import BaseModel
from datetime import datetime
from pydantic_settings import SettingsConfigDict


class FeedbackCreate(BaseModel):
    text: str


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    text: str
    created_at: datetime

    model_config = SettingsConfigDict(from_attributes = True)
