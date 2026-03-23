from pydantic import BaseModel, Field 
from typing import Dict, List

# class MCQoutput(BaseModel):
#     """Schema for the LLM  output to guarantee valid JSON formatting"""
#     question_text: str = Field(description = "The reformulated multiple choice question text")
#     options: Dict[str, str] = Field(description = "Dictionary of 4 options, Key must be 'A', 'B','C','D'")
#     correct_answer: Dict[str,str] = Field(description= "Dictionary with key, and text of correct answer")
#     explanation: str = Field(description = "Detailed explanation of why the correct answer is right and distractors are wrong")
#     bloom_level: int = Field (description= "The specific bloom level this question targets")

# class MCQBatchOutput(BaseModel): 
#     """Wrapper schema to get multiple MCQs in one API call"""
#     questions: List[MCQoutput] = Field(description= "List of generated MCQs")
    
class MCQCoreLLMOutput(BaseModel):
    """
    Schema for the LLM output in the Hybrid Architecture.

    The LLM is responsible for ONLY THREE things:
      1. A high-quality question stem
      2. The single correct answer (plain text, no option letter)
      3. A pedagogical explanation

    Distractors are NOT generated here. That is the DistractorBridge's job.
    """
    question_text: str = Field(
        description="The reformulated MCQ stem. A clear, unambiguous question."
    )
    correct_answer: str = Field(
        description=(
            "The single correct answer as plain text only. "
            "Do NOT include an option letter (A/B/C/D). "
            "Example: 'O(n log n)' not 'A. O(n log n)'"
        )
    )
    explanation: str = Field(
        description=(
            "A pedagogical explanation of WHY the correct answer is right. "
            "Reference the Bloom level. Do NOT mention distractors or wrong options."
        )
    )
    bloom_level: int = Field(
        description="Bloom's Taxonomy level this question targets (1=Remember, 2=Understand, 3=Apply, 4=Analyze)"
    )


class MCQBatchOutput(BaseModel):
    """Wrapper schema to generate multiple MCQ cores in one API call."""
    questions: List[MCQCoreLLMOutput] = Field(
        description="List of generated MCQ cores. One per requested Bloom level."
    )