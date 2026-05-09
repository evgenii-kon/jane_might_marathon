from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ArticleCreate(BaseModel):
    name: str = Field(..., max_length=255, min_length=3)
    slug: str = Field(..., max_length=255, pattern=r'^[a-z0-9-]+$')
    description: str = Field(..., max_length=500)
    text: str = Field(..., min_length=10)
    images: List[str] = Field(default_factory=list)


class ArticleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    text: Optional[str] = None
    images: Optional[List[str]] = None


class ArticleResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    text: str
    images: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True