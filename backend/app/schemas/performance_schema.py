from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Dict, Optional, Any
from datetime import date, datetime
import json

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10, pattern=r'^(Male|Female|Other)?$')
    school_class: Optional[str] = Field(None, max_length=50)

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError('Name must contain at least one letter')
        return v.strip()

class StudentOut(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    date_of_birth: Optional[date]
    gender: Optional[str]
    school_class: Optional[str]
    enrollment_date: date

    class Config:
        from_attributes = True  # Updated for Pydantic v2 compatibility

    def model_dump_json(self, *args, **kwargs) -> str:
        return super().model_dump_json(*args, **kwargs)

class AbilityEstimateCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    theta_estimate: float = Field(..., ge=-5.0, le=5.0)
    theta_confidence_low: float = Field(..., ge=-5.0, le=5.0)
    theta_confidence_high: float = Field(..., ge=-5.0, le=5.0)
    percentile_score: float = Field(..., ge=0.0, le=100.0)
    theta_history: Optional[Dict[str, float]] = None
    irt_model_version: str = Field(..., max_length=50)

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
    irt_model_version: str
    updated_at: datetime

    class Config:
        from_attributes = True

class TestSessionCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    selection_strategy: str = Field(..., max_length=100)
    current_item_pool: Optional[List[str]] = None
    fisher_info_history: Optional[Dict[str, float]] = None

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
    current_item_pool: Optional[List[str]]
    fisher_info_history: Optional[Dict[str, float]]

    class Config:
        from_attributes = True

class ResponseCreate(BaseModel):
    session_id: int = Field(..., gt=0)
    item_id: str = Field(..., max_length=50)
    item_parameters: Dict[str, float]
    is_correct: bool
    response_time_seconds: float = Field(..., ge=0.0)
    answered_at: Optional[datetime] = None

    @field_validator('item_parameters')
    def validate_item_parameters(cls, v: Dict[str, float]) -> Dict[str, float]:
        required_keys = {'a', 'b', 'c'}
        if not all(key in v for key in required_keys):
            raise ValueError('item_parameters must contain keys: a, b, c')
        return v

class ResponseOut(BaseModel):
    response_id: int
    session_id: int
    item_id: str
    item_parameters: Dict[str, float]
    is_correct: bool
    response_time_seconds: float
    answered_at: datetime

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

    def model_dump_json(self, *args, **kwargs) -> str:
        return super().model_dump_json(*args, **kwargs)