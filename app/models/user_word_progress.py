from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)

    mastery_level = Column(Integer, nullable=False, default=0)

    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)

    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="word_progress")
    word = relationship("Word", back_populates="user_progress")
