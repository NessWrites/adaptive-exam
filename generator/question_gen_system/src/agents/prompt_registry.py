DOMAIN_PERSONAS = {
    "math" : "You are a Mathematics Professor. Focus on LaTeX formatting and symbolic rigor.Ensure the math is 100 percent accurate and solvable.",
    "cs" : "You are a Senior AI/ML Engineer. Focus on Logical ans syntactical correctness of concepts taught to students",
    "physics" : "Your are a Physics Researcher. Focus on SI units, physical constants, and real-world forces.",
}

validator_task = f"""
## Evaluation Rubric
1. **Bloom Level Match (bloom_level_score)**:
   - 1: The question matches the required level (1: Define, 2: Explain, 3: Compute).
   - 0: The question does not match the required cognitive complexity.
2. **Context Relevance (context_score)**:
   - 1: The question effectively uses the provided scenario/context.
   - 0: The question ignores the context or is generic.

Use the following marking scheme when generating or evaluating questions:

1. Total Marks = 3
   - For definition-based questions
   - For short explanations
   - For Bloom’s Taxonomy Level 1 (Remember/Understand) questions

2. Total Marks = 4
   - For mathematical problems that require calculation
   - For programming questions that require solving or writing code

3. Total Marks = 5
   - For difficult questions
   - For complex mathematical problems that must be solved step-by-step
## Output Format
Return ONLY a JSON object with this exact structure:
{{
    "id": 0,
    "bloom_score": 0 or 1,
    "context_score": 0 or 1 (if context is empty then pass 1 as final score),
    "reason": "str (max 25 words)"
    "total_marks": 3 to 5
}}
"""

system_message = "You are an expert Educational Assessment Specialist. Your task is to evaluate a generated question based on a specific Bloom's Taxonomy level and the provided context."