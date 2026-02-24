from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Literal
from datetime import datetime, timezone
import uuid

DomainType = Literal["math", "tech"]
QuestionType = Literal["mcqs", "subjectives", "codes", "fill_in_the_blanks"]
CalibrationStatus = Literal["pretest", "operational"]


class DatabaseLog(BaseModel):
    id : Optional[int] = None 
    status: str 
    error: Optional[str] = None 
    
class QuestionContent(BaseModel):
    scenario_expansion: str 
    final_question: str 
    solution_steps: List[str]
    final_answer: str 
    
class GeneratedContentWrapper(BaseModel): 
    domain: str 
    unit: str 
    topic: str 
    skeleton: str 
    question: QuestionContent 
    
class GeneratorResponse(BaseModel): 
    generated_content: GeneratedContentWrapper
    database_log: Optional[DatabaseLog] = None 
    

# below is old schema for reference: 
class QuestionSchema(BaseModel):
    # --- DB COLUMNS ---
    unique_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: DomainType
    
    # RELATION: module + sub-module combination
    concept_tag: str = Field(..., description="Format: 'Module Name / Sub-module Name'")
    
    options: Optional[Dict[str, str, str, str]] = Field(None, description="e.g., {'A': '...', 'B': '...', 'C':'...', 'D': '...'}")
    correct_answer: str = Field(..., description="Answer key or string")
    image_url: Optional[str] = None
    question_type: QuestionType = "subjective"
    
    a_values: float = 1.0
    b_value: float = 0.0
    
    calibration_status: CalibrationStatus = "pretest"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # --- CONTENT FIELDS ---
    question_text: str = Field(..., description="The actual question text")
    explanation: str = Field(..., description="Why the answer is correct")

    @field_validator('concept_tag')
    @classmethod
    def validate_tag_format(cls, v: str):
        if " / " not in v:
            raise ValueError("concept_tag must follow the 'Module / Sub-module' format")
        return v