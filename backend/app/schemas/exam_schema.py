"""
Optimized API Schemas - Refined based on user feedback
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field


# ============================================================================
# Response Schemas - Optimized
# ============================================================================

class QuestionResponse(BaseModel):
    """Question data - essentials only"""
    unique_id: int
    question_text: str
    options: List[str]
    image_url: Optional[str] = None
    question_type: str  # MCQ or MSQ


class StartExamResponse(BaseModel):
    """Start exam - just session_id and question"""
    session_id: int
    question: QuestionResponse


class AnswerFeedback(BaseModel):
    """
    Feedback after answer submission.
    Note: Theta estimates are excluded during exam to avoid confusion.
    """
    is_correct: bool
    correct_answer: Union[str, List[str]]
    question_num: int


class SubmitAnswerRequest(BaseModel):
    """Submit answer request"""
    session_id: int
    user_answer: Union[str, List[str]]


class SubmitAnswerResponse(BaseModel):
    """Submit answer response"""
    feedback: AnswerFeedback
    next_question: Optional[QuestionResponse] = None
    exam_completed: bool


class AbilityEstimate(BaseModel):
    """Ability estimate with standard error and interpretation"""
    value: float = Field(..., description="Estimated ability value")
    standard_error: float = Field(..., description="Standard error of estimate")
    interpretation: str = Field(..., description="Human-readable interpretation")


class ResultsResponse(BaseModel):
    """
    Final results with comprehensive breakdown.
    
    Contains:
    - Overall performance (50 total questions)
    - Operational questions breakdown (40 questions)
    - Ability estimates (calculated from 40 operational questions only)
    """
    session_id: int
    
    # Overall performance
    total_questions: int = Field(..., description="Total questions (50)")
    correct_answers: int = Field(..., description="Correct answers out of 50")
    accuracy: float = Field(..., description="Accuracy percentage out of 50")
    
    # Operational breakdown
    operational_questions: int = Field(..., description="Operational questions (40)")
    operational_correct: int = Field(..., description="Correct operational answers")
    
    # Ability estimates (from 40 operational questions only)
    math_ability: AbilityEstimate
    tech_ability: AbilityEstimate
    
    completed_at: Optional[str] = None