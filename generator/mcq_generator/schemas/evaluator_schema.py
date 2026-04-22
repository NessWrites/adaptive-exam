from pydantic import BaseModel, Field

class MCQEvaluationOutput(BaseModel):
    hallucination_score: int = Field(
        ...,
        description="Score from 1 to 5 evaluating if the correct answer aligns with the marking scheme and course material without making up false facts (5 being perfectly aligned, 1 being completely hallucinated or conflicting)."
    )
    trickiness_score: int = Field(
        ...,
        description="Score from 1 to 5 evaluating the depth and cleverness of the question. Does it require deep reasoning instead of surface-level pattern matching? Are the distractors tricky and plausible? (5 being highly tricky/witty, 1 being too obvious)."
    )
    bloom_alignment_score: int = Field(
        ...,
        description="Binary score of 1 if the MCQ correctly targets the intended Bloom's Taxonomy level requested by the user, and 0 if it aligns with a different Bloom level."
    )
    feedback: str = Field(
        ...,
        description="Brief explanation justifying the scores, noting specific strengths or flaws in the question."
    )
