from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .db import Base

class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True, index=True)
    course = Column(String(32), index=True)
    week = Column(Integer, index=True)
    source = Column(String(256), nullable=True)
    type = Column(String(32), index=True)  # MCQ, MSQ, NUMERIC, TRUE_FALSE
    topic = Column(String(128), index=True, default="General")
    difficulty = Column(String(32), default="medium")
    marks = Column(Float, default=1.0)
    negative_marks = Column(Float, default=0.0)
    text = Column(Text, nullable=False)
    options_json = Column(Text, default="[]")       # JSON string
    correct_json = Column(Text, default="[]")       # JSON string
    numeric_value = Column(Float, nullable=True)
    tolerance = Column(Float, default=0.0)
    explanation = Column(Text, default="")
    image = Column(String(512), nullable=True)
    answer_meta_json = Column(Text, default="{}")   # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ExamAttemptModel(Base):
    __tablename__ = "exam_attempts"

    id = Column(String(64), primary_key=True, index=True)
    course = Column(String(32), default="ALL")
    week = Column(String(32), default="ALL")
    mode = Column(String(32), default="EXAM")
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    responses = relationship("ExamResponseModel", back_populates="attempt", cascade="all, delete-orphan")

class ExamResponseModel(Base):
    __tablename__ = "exam_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    attempt_id = Column(String(64), ForeignKey("exam_attempts.id"), index=True)
    question_id = Column(String(64), index=True)
    selected_json = Column(Text, default="null")
    is_correct = Column(Boolean, default=False)
    marks_awarded = Column(Float, default=0.0)

    attempt = relationship("ExamAttemptModel", back_populates="responses")

class LeitnerQueueModel(Base):
    __tablename__ = "leitner_queue"

    question_id = Column(String(64), primary_key=True)
    box_level = Column(Integer, default=1)  # 1 = daily, 2 = 3-day, 3 = 7-day, 4 = mastered
    consecutive_correct = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, default=datetime.datetime.utcnow)
    next_due_at = Column(DateTime, default=datetime.datetime.utcnow)
