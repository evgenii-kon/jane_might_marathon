from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import func



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    telegram = Column(String)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True))
    is_admin = Column(Boolean, default=False, nullable=False)

    lesson_progress = relationship("UserLessonProgress", back_populates="user", cascade="all, delete-orphan")
    word_progress = relationship('UserWordProgress', back_populates='user', cascade='all, delete-orphan')
    exercise_progress = relationship("UserExerciseProgress", back_populates="user", cascade="all, delete-orphan")
    week_progress = relationship("UserWeekProgress", back_populates="user", cascade="all, delete-orphan")