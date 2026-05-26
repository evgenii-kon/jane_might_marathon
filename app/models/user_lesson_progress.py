from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    is_started = Column(Boolean, default=False, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    # Постоянный флаг: True после первого успешного прохождения всех упражнений.
    # Сбросы упражнений не меняют это поле.
    exercises_ever_completed = Column(Boolean, default=False, nullable=False, server_default="false")

    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
        Index("ix_user_lesson_progress_user_completed", "user_id", "is_completed"),
    )
