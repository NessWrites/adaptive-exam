from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Dict, Optional, Any, Union
from datetime import date, datetime
import json

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError('Name must contain at least one letter')
        return v.strip()

class StudentOut(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    enrollment_date: date

    class Config:
        from_attributes = True  # Updated for Pydantic v2 compatibility

    # def model_dump_json(self, *args, **kwargs) -> str:
    #     return super().model_dump_json(*args, **kwargs)

class QuestionCreate(BaseModel):
    question_id: str = Field(..., max_length=50)
    question_text: Optional[str] = None
    img_url: Optional[str] = None
    marks: Optional[int] = None
    type: Optional[str] = Field(None, max_length=100)
    n_choices: int = Field(default=1, ge=1)
    correct_answer: Optional[Union[int, List[int]]] = None  # Changed to support both single and multiple answers
    options: Optional[List[Dict[str, Any]]] = None  # Question options as list of dictionaries
    parameter_a: Optional[float] = None
    parameter_b: Optional[float] = None
    parameter_c: Optional[float] = None
    difficulty_level: Optional[str] = Field(None, max_length=50)
    topic_dimension: Optional[str] = Field(None, max_length=100)
    cognitive_dimension: Optional[str] = Field(None, max_length=100)

class QuestionOut(BaseModel):
    question_id: str
    question_text: Optional[str]
    img_url: Optional[str]
    marks: Optional[int]
    type: Optional[str]
    n_choices: int
    correct_answer: Optional[Union[int, List[int]]]  # Changed to support both single and multiple answers
    options: Optional[List[Dict[str, Any]]]  # Question options as list of dictionaries
    parameter_a: Optional[float]  # 3PL discrimination
    parameter_b: Optional[float]  # 3PL difficulty
    parameter_c: Optional[float]  # 3PL guessing
    parameter_a_2pl: Optional[float]  # 2PL discrimination
    parameter_b_2pl: Optional[float]  # 2PL difficulty
    difficulty_level: Optional[str]
    topic_dimension: Optional[str]
    cognitive_dimension: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TestSessionCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    selection_strategy: str = Field(default="random", max_length=255)
    session_type: str = Field(default="assessment", max_length=100)
    current_item_pool: Optional[List[str]] = None
    metadata: Optional[Dict] = None

    @field_validator('end_time')
    def validate_end_time(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get('start_time') and v < info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class TestSessionOut(BaseModel):
    session_id: int
    student_id: int
    start_time: datetime
    end_time: Optional[datetime]
    selection_strategy: str
    session_type: str
    current_item_pool: Optional[List[str]]
    metadata: Optional[Dict]

    class Config:
        from_attributes = True

class ResponseCreate(BaseModel):
    session_id: int = Field(..., gt=0)
    question_id: str = Field(..., max_length=50)
    student_id: int = Field(..., gt=0)
    chosen_answer: Union[int, List[int]] = Field(...) 
    is_correct: int = Field(..., ge=0, le=1)
    response_time_seconds: Optional[float] = None
    answered_at: Optional[datetime] = None
    theta_before: Optional[float] = None
    theta_after: Optional[float] = None
    theta_change: Optional[float] = None
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None
    item_parameters: Optional[Dict[str, float]] = None
    response_metadata: Optional[Dict] = None

    @field_validator('item_parameters')
    def validate_item_parameters(cls, v: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        if v and not all(key in v for key in {'a', 'b', 'c'}):
            raise ValueError('item_parameters must contain keys: a, b, c')
        return v

class ResponseOut(BaseModel):
    response_id: int
    student_id: int
    session_id: int
    question_id: str
    chosen_answer: List[int]  # This should also be List if storing multiple choices
    is_correct: int
    response_time_seconds: Optional[float] = None
    answered_at: datetime
    theta_before: Optional[float] = None
    theta_after: Optional[float] = None
    theta_change: Optional[float] = None
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None
    item_parameters: Optional[dict] = None
    response_metadata: Optional[dict] = None

    class Config:
        from_attributes = True



class BayesianAbilityEstimateCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    theta_mean: float = Field(..., ge=-5.0, le=5.0)
    theta_std: Optional[float] = None
    theta_samples: Optional[List[float]] = None
    posterior_summary: Optional[Dict] = None
    version: str = Field(default="bayesian_irt_v1", max_length=100)
    estimation_method: str = Field(default="mcmc", max_length=100)
    n_samples: Optional[int] = None
    convergence_diagnostics: Optional[Dict] = None

class BayesianAbilityEstimateOut(BaseModel):
    estimate_id: int
    student_id: int
    theta_mean: float
    theta_std: Optional[float]
    theta_samples: Optional[List[float]]
    posterior_summary: Optional[Dict]
    version: str
    estimation_method: str
    n_samples: Optional[int]
    convergence_diagnostics: Optional[Dict]
    updated_at: datetime

    class Config:
        from_attributes = True

class QuestionParameterCreate(BaseModel):
    question_id: str = Field(..., max_length=50)
    parameter_a_mean: Optional[float] = None
    parameter_a_std: Optional[float] = None
    parameter_b_mean: Optional[float] = None
    parameter_b_std: Optional[float] = None
    parameter_c_mean: Optional[float] = None
    parameter_c_std: Optional[float] = None
    parameter_samples: Optional[Dict] = None
    version: str = Field(default="bayesian_irt_v1", max_length=100)
    estimation_method: str = Field(default="mcmc", max_length=100)
    n_samples: Optional[int] = None
    convergence_diagnostics: Optional[Dict] = None

class QuestionParameterUpdate(BaseModel):
    parameter_a_mean: Optional[float] = None
    parameter_a_std: Optional[float] = None
    parameter_b_mean: Optional[float] = None
    parameter_b_std: Optional[float] = None
    parameter_c_mean: Optional[float] = None
    parameter_c_std: Optional[float] = None
    parameter_samples: Optional[Dict] = None
    version: Optional[str] = None
    estimation_method: Optional[str] = None
    n_samples: Optional[int] = None
    convergence_diagnostics: Optional[Dict] = None

class QuestionParameterOut(BaseModel):
    param_id: int
    question_id: str
    parameter_a_mean: Optional[float]
    parameter_a_std: Optional[float]
    parameter_b_mean: Optional[float]
    parameter_b_std: Optional[float]
    parameter_c_mean: Optional[float]
    parameter_c_std: Optional[float]
    parameter_samples: Optional[Dict]
    version: str
    estimation_method: str
    n_samples: Optional[int]
    convergence_diagnostics: Optional[Dict]
    updated_at: datetime

    class Config:
        from_attributes = True

# Lightweight summary without heavy parameter_samples to avoid large payloads
class QuestionParameterSummaryOut(BaseModel):
    param_id: int
    question_id: str
    parameter_a_mean: Optional[float]
    parameter_a_std: Optional[float]
    parameter_b_mean: Optional[float]
    parameter_b_std: Optional[float]
    parameter_c_mean: Optional[float]
    parameter_c_std: Optional[float]
    version: str
    estimation_method: str
    n_samples: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    question_id: str = Field(..., max_length=50)
    obtained_score: Optional[int] = None
    total_score: Optional[int] = None
    submitted_at: Optional[datetime] = None
    plagiarism: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=100)
    submission_url: Optional[str] = None
    selected_options: Optional[str] = None
    options_metadata: Optional[Dict] = None
    is_correct: Optional[int] = None
    theta_estimate: Optional[float] = None
    theta_change: Optional[float] = None

class SubmissionOut(BaseModel):
    submission_id: int
    student_id: int
    question_id: str
    obtained_score: Optional[int]
    total_score: Optional[int]
    submitted_at: Optional[datetime]
    plagiarism: Optional[str]
    status: Optional[str]
    submission_url: Optional[str]
    selected_options: Optional[str]
    options_metadata: Optional[Dict]
    is_correct: Optional[int]
    theta_estimate: Optional[float]
    theta_change: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class AbilityEstimateCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    theta_estimate: float = Field(..., ge=-5.0, le=5.0)
    theta_confidence_low: float = Field(..., ge=-5.0, le=5.0)
    theta_confidence_high: float = Field(..., ge=-5.0, le=5.0)
    percentile_score: float = Field(..., ge=0.0, le=100.0)
    theta_history: Optional[Dict[str, float]] = None
    irt_version: str = Field(..., max_length=50)

    @field_validator('theta_confidence_low', 'theta_confidence_high')
    def validate_confidence_bounds(cls, v: float, info) -> float:
        if info.data.get('theta_estimate') is not None:
            theta = info.data['theta_estimate']
            if info.field_name == 'theta_confidence_low' and v > theta:
                raise ValueError('Lower confidence bound must be less than or equal to theta_estimate')
            if info.field_name == 'theta_confidence_high' and v < theta:
                raise ValueError('Upper confidence bound must be greater than or equal to theta_estimate')
        return v

class AbilityEstimateOut(BaseModel):
    estimate_id: int
    student_id: int
    theta_estimate: float
    theta_confidence_low: float
    theta_confidence_high: float
    percentile_score: float
    theta_history: Optional[Dict[str, float]]
    irt_version: str
    updated_at: datetime

    class Config:
        from_attributes = True

class PerformanceFeedbackCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    final_grade: str = Field(..., max_length=10)
    strength_topics: Dict[str, str]
    weakness_topics: Dict[str, str]
    recommendations: Optional[str] = Field(None, max_length=1000)
    progress_over_time: Optional[Dict[str, str]] = None

    @field_validator('final_grade')
    def validate_final_grade(cls, v: str) -> str:
        valid_grades = {'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'}
        if v not in valid_grades:
            raise ValueError(f'final_grade must be one of {valid_grades}')
        return v

class PerformanceFeedbackOut(BaseModel):
    feedback_id: int
    student_id: int
    final_grade: str
    strength_topics: Dict[str, str]
    weakness_topics: Dict[str, str]
    recommendations: Optional[str]
    progress_over_time: Optional[Dict[str, str]]

    class Config:
        from_attributes = True

    