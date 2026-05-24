from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .lesson_word_association import lesson_word_association


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    order_in_week = Column(Integer, nullable=False)
    content_html = Column(String, nullable=False)
    video_url = Column(String, nullable=True)

    week = relationship("Week", back_populates="lessons", lazy="selectin")
    user_progress = relationship(
        "UserLessonProgress", back_populates="lesson", lazy="selectin", cascade="all, delete-orphan"
    )
    words = relationship(
        "Word", secondary=lesson_word_association, back_populates="lessons", lazy="selectin"
    )
    exercises = relationship(
        "Exercise", back_populates="lesson", lazy="selectin", order_by="Exercise.order_in_lesson"
    )
