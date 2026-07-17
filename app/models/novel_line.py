from sqlalchemy import Column, Integer, String, ForeignKey, Text
from ..database import Base


class NovelLine(Base):
    __tablename__ = "novel_lines"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    order = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)  # "narrative" | "dialogue"
    character = Column(String(50), nullable=True)  # "confusi" | "zhulan" | "zho" | "chingisu" | "brus_ley" | "user" | null
    speaker = Column(String(100), nullable=True)  # отображаемое имя | null
    text = Column(Text, nullable=False)
    side = Column(String(10), nullable=True)  # "left" | "right" | null для narrative
