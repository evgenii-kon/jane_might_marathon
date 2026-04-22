from pydantic import BaseModel, Field


class LessonCreate(BaseModel):
    name: str = Field(..., min_length=3)
    week_id: int
    order_in_week: int
    content_html: str
    video_url: str | None = None


class LessonUpdate(BaseModel):
    name: str | None = Field(None, min_length=3)
    week_id: int | None = None
    order_in_week: int | None = None
    content_html: str | None = None
    video_url: str | None = None


    class Config:
        from_attributes=True


class LessonResponse(BaseModel):
    id: int
    name: str 
    week_id: int
    order_in_week: int
    content_html: str
    video_url: str

    class Config:
        from_attributes=True