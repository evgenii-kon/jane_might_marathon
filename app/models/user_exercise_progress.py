from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class UserExerciseProgress(Base):
    __tablename__ = "user_exercise_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )

    user = relationship("User", back_populates="exercise_progress", lazy="selectin")
    exercise = relationship("Exercise", back_populates="user_progress", lazy="selectin")
