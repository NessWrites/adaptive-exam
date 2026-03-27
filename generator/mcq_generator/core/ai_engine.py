import os 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from generator.mcq_generator.schemas.mcq_schema import MCQBatchOutput, MCQCoreLLMOutput

class MCQEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,   # Lower temp → more deterministic stems/answers
            api_key=os.getenv("GEMINI_API_KEY"),
        ).with_structured_output(MCQBatchOutput)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert AI educator specializing in computer science and mathematics assessment design.

YOUR SOLE TASK: Transform a subjective question into MCQ stems and correct answers only.

STRICT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1.  DO NOT generate distractors, wrong options, or any options labeled A/B/C/D.
2.  DO NOT include option letters in the correct_answer field.
3.  DO NOT produce a dictionary of options. The `options` field does not exist in your output schema.
4.  Generate EXACTLY one MCQCoreLLMOutput per requested Bloom level.
5.  The `correct_answer` must be a plain text string (e.g., "O(n log n)", not "A. O(n log n)").
6.  The `explanation` must justify the correct answer pedagogically at the specified Bloom level.
7. Bloom levels: 1=Remember, 2=Understand, 3=Apply, 4=Analyze.
8.  MAKE IT TRICKY & WITTY: The question stem and correct answer should require deep reasoning, not just surface-level rote memorization. Add depth, clever wording, and theoretical nuance based on the marking schema.

A separate specialized engine will generate all distractors. Your output is the foundation layer only."""
            ),
            (
                "human",
                """Domain: {domain}
Concept Tag: {concept_tag}
Target Bloom Levels for this batch: {levels_list}
Original Subjective Question:
{question_text}

Original Marking Scheme (use to ensure correct_answer accuracy):
{mark_schema}

Generate exactly one MCQCoreLLMOutput per Bloom level listed above.
Remember: correct_answer is plain text only — no option letters, no distractors."""
            ),
        ])

    async def generate_mcq_batch(
        self,
        domain: str,
        concept_tag: str,
        question_text: str,
        levels: list[int],
        mark_scheme: str = "Not provided",
    ) -> MCQBatchOutput:
        chain = self.prompt | self.llm
        result = await chain.ainvoke({
            "domain": domain,
            "concept_tag": concept_tag,
            "question_text": question_text,
            "levels_list": levels,
            "mark_schema": str(mark_scheme) if mark_scheme else "Not provided",
        })
        return result