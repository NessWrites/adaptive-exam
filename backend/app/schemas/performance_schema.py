from pydantic import BaseModel
from datetime import datetime

class PerformanceSchema(BaseModel):
    student_id: int
    question_id: str
    difficulty: str
    correct: bool
    timestamp: datetime
