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

        # ── Prompt for SUBJECTIVE → MCQ ──
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

        # ── Prompt for CODE → MCQ ──
        self.code_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert AI educator specializing in computer science and data structure/algorithm assessment design.

YOUR SOLE TASK: Transform a CODING PROBLEM into MCQ stems and correct answers only.
The student should NOT need to write code to answer the MCQ. Instead, test their conceptual understanding of the algorithm, data structure, time/space complexity, edge cases, or expected output for given inputs.

STRICT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1.  DO NOT generate distractors, wrong options, or any options labeled A/B/C/D.
2.  DO NOT include option letters in the correct_answer field.
3.  DO NOT produce a dictionary of options. The `options` field does not exist in your output schema.
4.  Generate EXACTLY one MCQCoreLLMOutput per requested Bloom level.
5.  The `correct_answer` must be a plain text string (e.g., "O(n log n)", not "A. O(n log n)").
6.  The `explanation` must justify the correct answer pedagogically at the specified Bloom level.
7.  Bloom levels: 1=Remember, 2=Understand, 3=Apply, 4=Analyze.
8.  MAKE IT TRICKY & WITTY: questions should probe deep algorithmic understanding, edge-case reasoning, complexity analysis, or trace-through logic — not simple recall.

STRATEGIES PER BLOOM LEVEL:
- Level 1 (Remember): Ask about the data structure / algorithm name, basic property, or definition relevant to the problem.
- Level 2 (Understand): Ask what the function returns for a specific input, or explain why a particular approach works.
- Level 3 (Apply): Present a new input and ask for the expected output, or ask which approach solves the problem optimally.
- Level 4 (Analyze): Ask about time/space complexity, tradeoffs, edge cases, or why an alternative approach would fail.

A separate specialized engine will generate all distractors. Your output is the foundation layer only."""
            ),
            (
                "human",
                """Domain: {domain}
Concept Tag: {concept_tag}
Target Bloom Levels for this batch: {levels_list}

Coding Problem:
{question_text}

Function Signature: {function_name}

Code Template:
{placeholder}

Test Cases (input → expected output):
{test_cases}

Allowed Imports / Data Type Context:
{configurations}

Generate exactly one MCQCoreLLMOutput per Bloom level listed above.
Remember: correct_answer is plain text only — no option letters, no distractors.
The MCQ should test conceptual understanding of the coding problem, NOT ask the student to write code."""
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
        """Generate MCQ batch from a SUBJECTIVE source question."""
        chain = self.prompt | self.llm
        result = await chain.ainvoke({
            "domain": domain,
            "concept_tag": concept_tag,
            "question_text": question_text,
            "levels_list": levels,
            "mark_schema": str(mark_scheme) if mark_scheme else "Not provided",
        })
        return result

    async def generate_mcq_batch_from_code(
        self,
        domain: str,
        concept_tag: str,
        question_text: str,
        function_name: str,
        placeholder: str,
        test_cases: str,
        configurations: str,
        levels: list[int],
    ) -> MCQBatchOutput:
        """Generate MCQ batch from a CODE source question."""
        chain = self.code_prompt | self.llm
        result = await chain.ainvoke({
            "domain": domain,
            "concept_tag": concept_tag,
            "question_text": question_text,
            "function_name": function_name,
            "placeholder": placeholder,
            "test_cases": test_cases,
            "configurations": configurations,
            "levels_list": levels,
        })
        return result