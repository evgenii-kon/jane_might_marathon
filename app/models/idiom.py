from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Idiom(Base):
    __tablename__ = "idioms"

    id = Column(Integer, primary_key=True)
    hanzi = Column(String(20), nullable=False)
    pinyin = Column(String(100), nullable=False)
    translate = Column(String(500), nullable=False)
    meaning = Column(Text, nullable=False)
    story = Column(Text, nullable=True)
    example = Column(Text, nullable=True)
    example_translation = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user_progress = relationship(
        "UserIdiomProgress", back_populates="idiom", cascade="all, delete-orphan"
    )
