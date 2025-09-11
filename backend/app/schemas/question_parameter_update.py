from pydantic import BaseModel
from typing import Optional

class QuestionParameterBase(BaseModel):
    a: float
    b: float
    c: float

class QuestionParameterCreate(QuestionParameterBase):
    question_id: int   # link to a question

class QuestionParameterUpdate(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    c: Optional[float] = None

class QuestionParameterOut(QuestionParameterBase):
    param_id: int
    question_id: int

    class Config:
        orm_mode = True
