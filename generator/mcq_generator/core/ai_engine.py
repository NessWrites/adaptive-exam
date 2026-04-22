import os 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from generator.mcq_generator.schemas.mcq_schema import MCQBatchOutput, MCQCoreLLMOutput, CodeMCQBatchOutput

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
        self.code_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,
            api_key=os.getenv("GEMINI_API_KEY"),
        ).with_structured_output(CodeMCQBatchOutput)

        self.code_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert AI educator specializing in computer science and data structure/algorithm assessment design.

YOUR SOLE TASK: Transform a CODING PROBLEM into a comprehensive code-specific MCQ.
You will generate the ENTIRE MCQ including the stem code, the question text, the correct answer, AND 3 distractors (wrong options).

STRICT RULES — VIOLATIONS WILL BREAK THE PIPELINE:
1.  You must choose one of these categories for `mcq_category`: 
    - `code_fill_blank`: The `stem_code` has missing parts (e.g. `???`). The `options` are code snippets to fill in.
    - `code_find_bug`: The `stem_code` has a bug. The `options` are code lines to fix it.
    - `code_implementation`: The `stem_code` is null. The `options` are complete function implementations.
2.  Generate exactly EXACTLY 4 options in the `options` dictionary, with keys 'A', 'B', 'C', 'D'.
3.  The values in `options` MUST be raw code snippets. Do not include option letters in the values.
4.  Generate EXACTLY one CodeMCQLLMOutput per requested Bloom level.
5.  Distractors (wrong options) MUST be plausible mistakes (e.g. off-by-one errors, missing base cases, wrong variable names).
6.  Bloom levels: 1=Remember, 2=Understand, 3=Apply, 4=Analyze.
7.  MAKE IT TRICKY & WITTY: probe deep algorithmic understanding, edge-case reasoning, complexity analysis, or trace-through logic.

STRATEGIES PER BLOOM LEVEL:
- Level 1/2 (Remember/Understand): Fill-in-the-blank for a crucial line of code (e.g., base case of recursion, loop condition).
- Level 3 (Apply): Find the bug in the given implementation.
- Level 4 (Analyze): Which full implementation correctly optimally solves the problem? Give 1 correct and 3 flawed implementations."""
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

Generate exactly one CodeMCQLLMOutput per Bloom level listed above.
Ensure `options` dict has 'A','B','C','D' as keys and code strings as values."""
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

    async def generate_code_mcq_batch(
        self,
        domain: str,
        concept_tag: str,
        question_text: str,
        function_name: str,
        placeholder: str,
        test_cases: str,
        configurations: str,
        levels: list[int],
    ) -> CodeMCQBatchOutput:
        """Generate MCQ batch from a CODE source question, bypassing distractor bridge."""
        chain = self.code_prompt | self.code_llm
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