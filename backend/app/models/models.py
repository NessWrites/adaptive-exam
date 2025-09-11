from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from ..database.postgresql.connection import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    enrollment_date = Column(Date, server_default=func.current_date())

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(String(50), primary_key=True, index=True)
    question_text = Column(Text)
    img_url = Column(Text)
    marks = Column(Integer)
    type = Column(String(100))
    n_choices = Column(Integer, nullable=False, default=1)
    correct_answer = Column(Integer)
    parameter_a = Column(Float)
    parameter_b = Column(Float)
    parameter_c = Column(Float)
    difficulty_level = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now())


class BayesianAbilityEstimate(Base):
    __tablename__ = "bayesian_ability_estimates"

    estimate_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    theta_mean = Column(Float, nullable=False)
    theta_std = Column(Float)
    theta_samples = Column(JSONB)
    posterior_summary = Column(JSONB)
    model_version = Column(String(100), default="bayesian_irt_v1")
    estimation_method = Column(String(100), default="mcmc")
    n_samples = Column(Integer)
    convergence_diagnostics = Column(JSONB)
    updated_at = Column(TIMESTAMP, server_default=func.now())

class TestSession(Base):
    __tablename__ = "test_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"))
    start_time = Column(TIMESTAMP, server_default=func.now())
    end_time = Column(TIMESTAMP)
    selection_strategy = Column(String)
    session_type = Column(String(100), default="assessment")
    current_item_pool = Column(JSONB)
    session_metadata = Column(JSONB)

class Response(Base):
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.session_id", ondelete="CASCADE"))
    question_id = Column(String(50), ForeignKey("questions.question_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    chosen_answer = Column(Integer, nullable=False)
    is_correct = Column(Integer)
    response_time_seconds = Column(Float)
    answered_at = Column(TIMESTAMP, server_default=func.now())
    theta_before = Column(Float)
    theta_after = Column(Float)
    theta_change = Column(Float)
    confidence_interval_low = Column(Float)
    confidence_interval_high = Column(Float)
    item_parameters = Column(JSONB)
    response_metadata = Column(JSONB)

class QuestionParameter(Base):
    __tablename__ = "question_parameters"

    param_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(50), ForeignKey("questions.question_id", ondelete="CASCADE"))
    parameter_a_mean = Column(Float)
    parameter_a_std = Column(Float)
    parameter_b_mean = Column(Float)
    parameter_b_std = Column(Float)
    parameter_c_mean = Column(Float)
    parameter_c_std = Column(Float)
    parameter_samples = Column(JSONB)
    model_version = Column(String(100), default="bayesian_irt_v1")
    estimation_method = Column(String(100), default="mcmc")
    n_samples = Column(Integer)
    convergence_diagnostics = Column(JSONB)
    updated_at = Column(TIMESTAMP, server_default=func.now())

class Submission(Base):
    __tablename__ = "submissions"

    submission_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    question_id = Column(String(50), ForeignKey("questions.question_id"))
    obtained_score = Column(Integer)
    total_score = Column(Integer)
    submitted_at = Column(TIMESTAMP)
    plagiarism = Column(String(100))
    status = Column(String(100))
    submission_url = Column(Text)
    selected_options = Column(Text)
    options_metadata = Column(JSONB)
    is_correct = Column(Integer)
    theta_estimate = Column(Float)
    theta_change = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        {"schema": "public"}
    )