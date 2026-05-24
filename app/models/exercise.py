from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question_description = Column(String(255), nullable=False)
    question_text = Column(Text, nullable=False)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    order_in_lesson = Column(Integer, default=0)

    lesson = relationship("Lesson", back_populates="exercises")
    user_progress = relationship(
        "UserExerciseProgress", back_populates="exercise", cascade="all, delete-orphan", lazy="selectin"
    )
