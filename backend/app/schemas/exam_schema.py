"""
Optimized API Schemas 
"""
from pydantic import BaseModel
from typing import List, Optional, Union


# ============================================================================
# Response Schemas
# ============================================================================

class QuestionResponse(BaseModel):
    """Question data - essentials only"""
    unique_id: int
    question_text: str
    options: List[str]
    image_url: Optional[str]
    question_type: str  # MCQ or MSQ


class StartExamResponse(BaseModel):
    """Start exam - just session_id and question"""
    session_id: int
    question: QuestionResponse


class AnswerFeedback(BaseModel):
    """Feedback after answer submission"""
    is_correct: bool
    correct_answer: Union[str, List[str]]
    question_num: int
    # Removed: theta_math, theta_tech, total_questions


class SubmitAnswerRequest(BaseModel):
    """Submit answer request"""
    session_id: int
    user_answer: Union[str, List[str]]


class SubmitAnswerResponse(BaseModel):
    """Submit answer response"""
    feedback: AnswerFeedback
    next_question: Optional[QuestionResponse]
    exam_completed: bool


class AbilityEstimate(BaseModel):
    """Ability estimate for results"""
    value: float
    standard_error: float
    interpretation: str



class ResultsResponse(BaseModel):
    """
    Final results with comprehensive breakdown
    
    """
    session_id: int
    total_questions: int           # 50 total
    correct_answers: int           # Correct out of 50
    accuracy: float                # Percentage out of 50
    
    # Breakdown
    operational_questions: int     # 40 operational
    operational_correct: int       # Correct operational
        
    # Ability estimates (from 40 operational only)
    math_ability: AbilityEstimate
    tech_ability: AbilityEstimate
    
    completed_at: Optional[str] = None