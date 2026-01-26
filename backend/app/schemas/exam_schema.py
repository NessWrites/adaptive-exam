from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime


# Request Schemas
class SessionCreateRequest(BaseModel):
    """Request to start a new exam session"""
    user_id: Optional[str] = None
    n_questions: int = Field(default=40, ge=1, le=100)


class AnswerSubmitRequest(BaseModel):
    """Request to submit an answer"""
    session_id: int
    user_answer: Union[str, List[str]]  # Single answer or multiple for MSQ


# Response Schemas
class SessionInfo(BaseModel):
    """Basic session information"""
    session_id: int
    user_id: Optional[str]
    status: str
    current_question_num: int
    n_questions: int
    theta_math: float
    theta_tech: float
    math_count: int
    tech_count: int
    created_at: datetime


class QuestionData(BaseModel):
    """Question data to send to client"""
    unique_id: int
    question_text: str
    options: Optional[List[str]]
    image_url: Optional[str]
    question_type: str
    question_num: int
    total_questions: int


class StartExamResponse(BaseModel):
    """Response when starting exam - includes session and first question"""
    session: SessionInfo
    question: QuestionData


class AnswerFeedback(BaseModel):
    """Feedback after submitting an answer"""
    is_correct: bool
    correct_answer: Union[str, List[str]]
    theta_math: float
    theta_tech: float
    question_num: int
    total_questions: int


class SubmitAnswerResponse(BaseModel):
    """Response after submitting answer - includes feedback and next question (or completion)"""
    feedback: AnswerFeedback
    next_question: Optional[QuestionData] = None
    exam_completed: bool = False


class AbilityEstimate(BaseModel):
    """Ability estimate for a dimension"""
    value: float
    standard_error: float
    interpretation: str


class ResultsResponse(BaseModel):
    """Final exam results"""
    session_id: int
    total_questions: int
    correct_answers: int
    accuracy: float
    math_ability: AbilityEstimate
    tech_ability: AbilityEstimate
    completed_at: datetime