from pydantic import BaseModel, Field


class LessonCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: str = Field()


class LessonResponse(BaseModel):
    id: int
    name: str = Field(..., min_length=3)
    description: str

    class Config:
        from_attributes=True