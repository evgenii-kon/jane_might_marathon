from sqlalchemy import Table, Column, Integer, ForeignKey
from ..database import Base

lesson_word_association = Table(
    'lesson_word_association',
    Base.metadata,
    Column('lesson_id', Integer, ForeignKey('lessons.id'), primary_key=True),
    Column('word_id', Integer, ForeignKey('words.id'), primary_key=True)
)