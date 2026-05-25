from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserExerciseProgress(Base):
    __tablename__ = "user_exercise_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    user = relationship("User", back_populates="exercise_progress")
    exercise = relationship("Exercise", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint("user_id", "exercise_id", name="uq_user_exercise_progress"),
        Index("ix_user_exercise_progress_user_completed", "user_id", "is_completed"),
    )
