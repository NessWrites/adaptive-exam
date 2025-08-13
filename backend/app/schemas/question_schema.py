from pydantic import BaseModel
from typing import List, Optional

class QuestionSchema(BaseModel):
    question_text: str
    difficulty: str
    question_type: str
    sub_topic: str
    options: Optional[List[str]] = None
    answer: Optional[List[str]] = None
    tags: Optional[List[str]] = None
