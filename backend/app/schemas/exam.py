from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Request Models
class StartExamRequest(BaseModel):
    item_bank_path: Optional[str] = ""
    max_items: int = 40
    target_se: float = 0.30

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: Any  # Can be string (MCQ) or list (MSQ)

# Response Models
class StartExamResponse(BaseModel):
    session_id: str
    message: str
    total_items: int
    config: Dict[str, Any]

class QuestionResponse(BaseModel):
    session_id: str
    question_num: int
    item_id: str
    question_text: str
    options: Optional[List[str]]
    image_url: Optional[str]
    is_msq: bool
    progress: Dict[str, Any]
    current_theta: List[float]
    current_se: List[float]

class AnswerFeedback(BaseModel):
    is_correct: bool
    user_answer: Any
    correct_answer: Optional[Any]
    theta_before: List[float]
    theta_after: List[float]
    se_before: List[float]
    se_after: List[float]
    se_target_met: Dict[str, bool]
    next_question: Optional[QuestionResponse]
    test_completed: bool
    completion_reason: Optional[str]

class FinalResults(BaseModel):
    completion_reason: str
    questions_answered: int
    correct_responses: int
    accuracy: float
    final_theta_math: float
    final_theta_tech: float
    final_se_math: float
    final_se_tech: float
    se_target_achieved_math: bool
    se_target_achieved_tech: bool
    math_questions: int
    tech_questions: int

class SessionDeleteResponse(BaseModel):
    message: str