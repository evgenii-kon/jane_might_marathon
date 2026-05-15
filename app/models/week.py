from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base


class Week(Base):
    __tablename__ = 'weeks'

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, nullable=False)
    short_description = Column(String, nullable=False)
    long_description = Column(String, nullable=False)
    number =Column(Integer, unique=True, nullable=False)
    target_words_count = Column(Integer, nullable=False)
    target_exercises_count =Column(Integer, nullable=False)

    lessons = relationship('Lesson', back_populates='week')
    user_progress = relationship("UserWeekProgress", back_populates="week", cascade="all, delete-orphan")