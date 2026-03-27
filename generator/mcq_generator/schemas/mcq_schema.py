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


class CodeMCQLLMOutput(BaseModel):
    """
    Schema for the LLM output for code-specific questions.
    The LLM generates ALL 4 OPTIONS (correct answer + 3 distractors) for coding MCQs
    because generating plausible buggy code distractors requires understanding the full context.
    """
    mcq_category: str = Field(
        description="Must be exactly one of: 'code_fill_blank', 'code_find_bug', or 'code_implementation'"
    )
    question_text: str = Field(
        description="The human-readable question prompt."
    )
    stem_code: str | None = Field(
        default=None,
        description="Code block for the stem (e.g. code with ??? or bugs). Null if category is 'code_implementation' and no stem code is needed."
    )
    options: Dict[str, str] = Field(
        description="Dictionary of exactly 4 options. Keys MUST be 'A', 'B', 'C', 'D'. Values must be code snippets or lines of code."
    )
    correct_answer_key: str = Field(
        description="The key of the correct option: 'A', 'B', 'C', or 'D'."
    )
    explanation: str = Field(
        description="A pedagogical explanation of WHY the correct option is right and why the distractors are wrong."
    )
    bloom_level: int = Field(
        description="Bloom's Taxonomy level this question targets (1=Remember, 2=Understand, 3=Apply, 4=Analyze)."
    )


class CodeMCQBatchOutput(BaseModel):
    """Wrapper schema to generate multiple full code MCQs in one API call."""
    questions: List[CodeMCQLLMOutput] = Field(
        description="List of generated code MCQs. One per requested Bloom level."
    )