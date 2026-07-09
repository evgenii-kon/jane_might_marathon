from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from ..database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    type = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=True)
    config = Column(JSON, nullable=False, default=dict)
    explanation = Column(Text, nullable=True)
    order_in_lesson = Column(Integer, default=0)

    lesson = relationship("Lesson", back_populates="exercises")
    user_progress = relationship(
        "UserExerciseProgress", back_populates="exercise", cascade="all, delete-orphan", lazy="selectin"
    )
