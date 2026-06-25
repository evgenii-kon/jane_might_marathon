from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pydantic_settings import SettingsConfigDict


class GrammarTagCreate(BaseModel):
    name: str
    slug: str


class GrammarTagResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = SettingsConfigDict(from_attributes=True)


class GrammarRuleCreate(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    content: str
    hsk_level: Optional[str] = None
    tag_ids: List[int] = []


class GrammarRuleUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    hsk_level: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class GrammarRuleResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    content: str
    hsk_level: Optional[str] = None
    created_at: datetime
    tags: List[GrammarTagResponse] = []

    model_config = SettingsConfigDict(from_attributes=True)
