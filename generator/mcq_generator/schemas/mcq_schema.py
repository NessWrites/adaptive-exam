from pydantic import BaseModel, Field 
from typing import Dict 

class MCQoutput(BaseModel):
    """Schema for the LLM  output to guarantee valid JSON formatting"""
    question_text: str = Field(description = "The reformulated multiple choice question text")
    options: Dict[str, str] = Field(description = "Dictionary of 4 options, Key must be 'A', 'B','C','D'")
    correct_answer: Dict[str,str] = Field(description= "Dictionary with key, and text of correct answer")
    explanation: str = Field(description = "Detailed explanation of why the correct answer is right and distractors are wrong")
    
