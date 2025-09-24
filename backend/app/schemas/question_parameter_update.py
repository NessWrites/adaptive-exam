from pydantic import BaseModel
from typing import Optional, List, Union

class QuestionParameterBase(BaseModel):
    a: float
    b: float
    c: float

class QuestionParameterCreate(QuestionParameterBase):
    question_id: str  # Changed from int to str to match your database schema

class QuestionParameterUpdate(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None

class QuestionParameterOut(QuestionParameterBase):
    param_id: int
    question_id: str  # Changed from int to str to match your database schema

    class Config:
        from_attributes = True  # Updated for Pydantic v2