from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON,ARRAY,Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.postgresql.connection import Base

class Question(Base):
    __tablename__ = "questions"
    
    unique_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    domain = Column(String(100), nullable=False)
    concept_tag = Column(String(200), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=True)
    image_url = Column(Text, nullable=True)
    question_type = Column(String(10))
    
    # IRT Parameters
    a_values = Column(ARRAY(Float), nullable=False)  # # [0,0] for pretest
    b_value = Column(Float, nullable=False)  # 0 for pretest
    
    # CALIBRATION STATUS (NEW!)
    calibration_status = Column(String(20), default='operational', index=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #polymorphic config : 
    __mapper_args__= {
        "polymorphic_on": question_type,
        "polymorphic_identity": "question",
    }

class ExamSession(Base):
    """Exam session tracking"""
    __tablename__ = "exam_sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100)) 
    status = Column(String(20), default="in_progress")  
    n_questions = Column(Integer, default=40)
    current_question_num = Column(Integer, default=0)
    theta_math = Column(Float, default=0.0)
    theta_tech = Column(Float, default=0.0)
    theta_se_math = Column(Float, default=1.0)
    theta_se_tech = Column(Float, default=1.0)
    math_count = Column(Integer, default=0)
    tech_count = Column(Integer, default=0)
    # Timestamps - let database handle defaults
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
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
    user_answer = Column(JSON)  
    is_correct = Column(Boolean)  
    theta_math_after = Column(Float)
    theta_tech_after = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ExamSession", back_populates="responses")
    question = relationship("Question")


class SubjectiveQuestion(Question):
    __tablename__ = "subjective_questions"

    id = Column(Integer, ForeignKey("questions.unique_id", ondelete = "CASCADE"), primary_key=True)
    mark_schema = Column(JSON, nullable=True)
    bloom_level = Column(Float, nullable=False)
    total_marks = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint('total_marks <= 5', name='check_total_marks_max'),
    )
    
    __mapper_args__ = {"polymorphic_identity": "subjective"}


    
    #easily fetch all mcq genrated from this question 
    derived_mcqs = relationship(
        "MCQQuestion",
        back_populates= "source_subjective_question",
        foreign_keys= "[MCQQuestion.derived_from_subjective_id]",
        cascade="all, delete-orphan",)
    

class CodeQuestion(Question):
    __tablename__ = "code_questions"

    # Links to the base Question table
    id = Column(Integer, ForeignKey("questions.unique_id", ondelete="CASCADE"), primary_key=True)
    
    # --- Code Grader Specific Fields ---
    
    # The initial code template shown to the student
    placeholder = Column(Text, nullable=False, default="def solution():\n    pass")
    
    # The exact name of the function the student must implement
    function_name = Column(String(100), nullable=False) 
    
    # JSON containing 'allowed_imports' (List[str]) and 'data_type' (str)
    # Example: {"allowed_imports": ["import math"], "data_type": "linked_list"}
    configurations = Column(JSON, nullable=False, default=lambda: {})
    
    # JSON array holding the test cases
    # Example: [{"input": [[1,2]], "expected": [2,1], "hidden": False}]
    markscheme = Column(JSON, nullable=False, default=lambda: [])
    
    # Resource constraints for the Docker sandbox
    total_marks = Column(Integer, nullable=False)
    timeout = Column(Integer, nullable=False, default=5)          # seconds
    memory_limit = Column(String(20), nullable=False, default="128m")
    
    # Academic/IRT metadata
    bloom_level = Column(Float, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "code"}

    # Relationship to easily fetch all MCQs generated from this coding question
    derived_mcqs = relationship(
        "MCQQuestion",
        back_populates="source_code_question",
        foreign_keys="[MCQQuestion.derived_from_code_id]",
        cascade="all, delete-orphan"
    )




class MCQQuestion(Question):
    __tablename__ = 'mcq_questions_converted'
    
    id = Column(Integer, ForeignKey("questions.unique_id", ondelete = "CASCADE"), primary_key= True)
    
    bloom_level = Column(Integer, nullable= False)
    
    derived_from_subjective_id = Column(Integer, ForeignKey("subjective_questions.id", ondelete ="CASCADE"), nullable=True)
    derived_from_code_id = Column(Integer, ForeignKey("code_questions.id", ondelete = "CASCADE"), nullable=True)
    
    explanation = Column(Text, nullable = True) 
    validation_score = Column(JSON, nullable=True)
    

    __table_args__ = ( 
        CheckConstraint(
            "(derived_from_code_id IS NOT NULL AND derived_from_subjective_id IS NULL) "
            "OR "
            "(derived_from_code_id IS NULL AND derived_from_subjective_id IS NOT NULL)",
            name= "check_exactly_one_parent"
        ),)
    __mapper_args__ = {"polymorphic_identity": "mcq"}  #
    
    source_subjective_question = relationship(
        "SubjectiveQuestion",
        back_populates = "derived_mcqs",
        foreign_keys=[derived_from_subjective_id],
        )

    source_code_question = relationship(
        "CodeQuestion", 
        back_populates = "derived_mcqs",
        foreign_keys = [derived_from_code_id],
        )


    #getter for parent 
    @property 
    def source_question(self):
        """returns parent questions if it is code or subjective, returns first it finds"""
        return self.source_subjective_question or self.source_code_question