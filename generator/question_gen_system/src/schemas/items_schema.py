from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4

# llm response
class LLMQuestionResponse(BaseModel):
    questions: List[str]



# cleaned question row schema
class QuestionRow(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    domain: str
    unit: str
    topic: str
    context: str | None = None
    bloom_level: int
    question: str

    bloom_score: float | None = None
    context_score: float | None = None
    reason: str | None = None
    total_marks: int | None = None