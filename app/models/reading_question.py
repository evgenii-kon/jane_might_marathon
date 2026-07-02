from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ReadingQuestion(Base):
    __tablename__ = "reading_questions"

    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey("reading_texts.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(String(500), nullable=False)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)
    correct_answer = Column(Integer, nullable=False)  # 1/2/3/4
    explanation = Column(String(500), nullable=True)
    order_in_text = Column(Integer, default=0, nullable=False)

    text = relationship("ReadingText", back_populates="questions")
