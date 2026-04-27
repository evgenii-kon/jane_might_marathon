from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    week_id = Column(Integer, ForeignKey('weeks.id'), nullable=False)
    order_in_week = Column(Integer, nullable=False)
    content_html = Column(String, nullable=False)
    video_url = Column(String, nullable=True)

    week = relationship('Week', back_populates='lessons')
    user_progress = relationship("UserLessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    