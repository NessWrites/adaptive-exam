"""
Optimized API Schemas - Refined based on user feedback
"""
from pydantic import BaseModel
from typing import List, Optional, Union


# ============================================================================
# Response Schemas - Optimized
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
    """Feedback after answer - no theta (confusing during exam)"""
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
    """Final results - keep everything"""
    session_id: int
    total_questions: int
    correct_answers: int
    accuracy: float
    math_ability: AbilityEstimate
    tech_ability: AbilityEstimate
    