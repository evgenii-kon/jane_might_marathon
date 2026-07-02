from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ReadingText(Base):
    __tablename__ = "reading_texts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    content_hanzi = Column(Text, nullable=False)
    content_pinyin = Column(Text, nullable=True)
    content_translation = Column(Text, nullable=True)
    hsk_level = Column(String(20), nullable=True)
    week_id = Column(Integer, ForeignKey("weeks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship(
        "ReadingQuestion",
        back_populates="text",
        cascade="all, delete-orphan",
        order_by="ReadingQuestion.order_in_text",
    )
    user_progress = relationship("UserReadingProgress", back_populates="text", cascade="all, delete-orphan")
