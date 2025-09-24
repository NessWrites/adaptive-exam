from pydantic import BaseModel
from typing import List, Optional, Union

class QuestionSchema(BaseModel):
    question_text: str
    difficulty: str
    question_type: str
    sub_topic: str
    options: Optional[List[str]] = None
    answer: Optional[Union[str, List[str]]] = None  # Changed to support both single and multiple answers
    tags: Optional[List[str]] = None