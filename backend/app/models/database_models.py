from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.postgresql.connection import Base



class Question(Base):
    """Question/Item bank model"""
    __tablename__ = "questions"
    
    unique_id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(100), nullable=False)  # 'math' or 'tech'
    concept_tag = Column(String(200))
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # List of options
    correct_answer = Column(JSON)  # Can be string or list for MSQ
    image_url = Column(Text)
    question_type = Column(String(10))  # 'MCQ' or 'MSQ'
    a_values = Column(JSON, nullable=False)  # [a1, a2] discrimination parameters
    b_value = Column(Float, nullable=False)  # difficulty parameter
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExamSession(Base):
    """Exam session tracking"""
    __tablename__ = "exam_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))  # Optional user identifier
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    n_questions = Column(Integer, default=40)
    current_question_num = Column(Integer, default=0)
    theta_math = Column(Float, default=0.0)
    theta_tech = Column(Float, default=0.0)
    theta_se_math = Column(Float, default=1.0)
    theta_se_tech = Column(Float, default=1.0)
    math_count = Column(Integer, default=0)
    tech_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")


class Response(Base):
    """Individual question responses"""
    __tablename__ = "responses"
    
    response_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.session_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.unique_id"), nullable=False)
    question_num = Column(Integer, nullable=False)  # Order in exam
    user_answer = Column(JSON)  # Can be string or list
    is_correct = Column(Integer)  # 1 for correct, 0 for incorrect
    theta_math_after = Column(Float)
    theta_tech_after = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ExamSession", back_populates="responses")
    question = relationship("Question")