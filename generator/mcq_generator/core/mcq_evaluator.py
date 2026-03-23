import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from generator.mcq_generator.schemas.evaluator_schema import MCQEvaluationOutput

logger = logging.getLogger(__name__)

class MCQEvaluator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,  # Low temperature for objective judging
            api_key=os.getenv("GEMINI_API_KEY"),
        ).with_structured_output(MCQEvaluationOutput)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an advanced AI assessment judge and pedagogy expert.
Your task is to evaluate a generated Multiple Choice Question (MCQ) based on its original subjective question, marking scheme, and the targeted Bloom's level.

You must score the MCQ based on the following three axes:
1. Hallucination (Score from 1 to 5: 1=Hallucinated/Contradicts marking scheme, 5=Perfectly aligns)
2. Trickiness (Score from 1 to 5: 1=Trivial/Obvious, 5=Deep, witty, clever distractors)
3. Bloom Alignment (Score exactly 0 or 1: 1=Perfectly matches intended Bloom level requested, 0=Targets a different level than requested)

Provide a brief 'feedback' string justifying the scores.
"""
            ),
            (
                "human",
                """Original Subjective Question:
{question_text}

Original Marking Scheme:
{mark_scheme}

Targeted Bloom Level: {bloom_level}

---
Generated MCQ Structure to Evaluate:
Stem: {mcq_stem}
Correct Answer: {correct_answer}
Distractors: {distractors}
Explanation provided by generator: {explanation}

Evaluate this MCQ out of 5 for hallucination, trickiness, and Bloom alignment."""
            ),
        ])

    async def evaluate_mcq(
        self,
        question_text: str,
        mark_scheme: str,
        bloom_level: int,
        mcq_stem: str,
        correct_answer: str,
        distractors: list[str],
        explanation: str
    ) -> dict:
        """Run the LLM judge on the generated MCQ."""
        chain = self.prompt | self.llm
        
        try:
            result = await chain.ainvoke({
                "question_text": question_text,
                "mark_scheme": str(mark_scheme) if mark_scheme else "Not provided",
                "bloom_level": bloom_level,
                "mcq_stem": mcq_stem,
                "correct_answer": correct_answer,
                "distractors": distractors,
                "explanation": explanation
            })
            return result.model_dump()
        except Exception as e:
            logger.error(f"Failed to evaluate MCQ: {e}", exc_info=True)
            # Return a default/fallback object if evaluation fails
            return {
                "hallucination_score": 0,
                "trickiness_score": 0,
                "bloom_alignment_score": 0,
                "feedback": f"Evaluation failed: {str(e)}"
            }
