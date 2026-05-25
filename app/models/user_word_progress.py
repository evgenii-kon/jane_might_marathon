from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, index=True)

    mastery_level = Column(Integer, nullable=False, default=0)

    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)

    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="word_progress")
    word = relationship("Word", back_populates="user_progress")

    __table_args__ = (
        # Один пользователь — одна запись прогресса на слово
        UniqueConstraint("user_id", "word_id", name="uq_user_word_progress"),
        # Составной индекс для запроса "слова пользователя к повторению сегодня"
        Index("ix_user_word_progress_user_review", "user_id", "next_review_at"),
    )
