from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(10))
    school_class = Column(String)
    enrollment_date = Column(Date, server_default=func.current_date())

class AbilityEstimate(Base):
    __tablename__ = "ability_estimates"

    estimate_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    theta_estimate = Column(Float)
    theta_confidence_low = Column(Float)
    theta_confidence_high = Column(Float)
    percentile_score = Column(Float)
    theta_history = Column(JSONB)
    irt_model_version = Column(String)
    updated_at = Column(TIMESTAMP, server_default=func.now())

class TestSession(Base):
    __tablename__ = "test_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    start_time = Column(TIMESTAMP, server_default=func.now())
    end_time = Column(TIMESTAMP)
    selection_strategy = Column(String)
    current_item_pool = Column(JSONB)
    fisher_info_history = Column(JSONB)

class Response(Base):
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.session_id", ondelete="CASCADE"))
    item_id = Column(String)
    item_parameters = Column(JSONB)
    is_correct = Column(Integer)
    response_time_seconds = Column(Float)
    answered_at = Column(TIMESTAMP, server_default=func.now())

class PerformanceFeedback(Base):
    __tablename__ = "performance_feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    final_grade = Column(String)
    strength_topics = Column(JSONB)
    weakness_topics = Column(JSONB)
    recommendations = Column(Text)
    progress_over_time = Column(JSONB)