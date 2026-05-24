from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base
from .lesson_word_association import lesson_word_association


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    hanzi = Column(String(100), nullable=False)
    transcription = Column(String(100), nullable=False)
    translation = Column(String(255), nullable=False)
    audio_url = Column(String(500), nullable=True)
    part_of_speech = Column(String(50), nullable=True)
    example_sentence = Column(Text, nullable=True)
    example_translation = Column(Text, nullable=True)

    # Связь с уроками (многие ко многим)
    lessons = relationship(
        "Lesson", secondary=lesson_word_association, back_populates="words", lazy="selectin"
    )
    user_progress = relationship(
        "UserWordProgress", back_populates="word", cascade="all, delete-orphan", lazy="selectin"
    )
