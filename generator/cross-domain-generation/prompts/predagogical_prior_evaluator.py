PEDAGOGICAL_PRIOR_EVALUATOR_PROMPT = """
You are a pedagogical evaluator with deep knowledge of learning design principles.

You will be given:
- 2 topics and their learning objectives
- A set of questions generated from a hypothetical scenario
- Student attempts for each question

## Topics and Learning Objectives
Topic 1: {topic_1}
Learning Objective 1: {learning_objective_1}

Topic 2: {topic_2}
Learning Objective 2: {learning_objective_2}

## Questions and Student Attempts
{questions_and_attempts}

## Your Task
Evaluate each question as a learning instrument — not the student, not the answer.

A good question is one that forces a student to naturally decompose it
into pieces that map to both learning objectives — without being told to.

## Reference Example
To understand the dimensions, consider this example question evaluated
against these two learning objectives:

Learning Objective 1: Represent a linear transformation as a matrix and 
describe how it maps vectors between spaces including stretching and rotation.

Learning Objective 2: Compute eigenvalues and eigenvectors of a square matrix 
and interpret their geometric meaning as scaling factors and invariant directions.

Example Question:
"A bridge deformation team models structural change under wind load using 
transformation matrix A = [[2.5, 0.3], [0.1, 1.8]]. Analyze how the bridge 
deforms and identify the critical deformation directions."

## Evaluation Dimensions
Score each question from 0.0 to 1.0 on each dimension:

1. Learning Objective Reflection
   → Does the question structurally require BOTH learning objectives to attempt?
   → Both objectives must be causally necessary — not just mentioned

   Example (score: 0.95):
   The bridge question requires the student to first understand A as a 
   linear transformation (LO1) and then compute eigenvalues/eigenvectors 
   to find critical deformation directions (LO2). Neither objective alone 
   is sufficient — both are causally necessary.

2. Cognitive Load Balance
   → Do both topics contribute equally in the question?
   → Neither topic should dominate — both should be necessary

   Example (score: 0.90):
   The bridge question gives equal weight to transformation interpretation 
   and eigenvalue computation — neither dominates. Student must engage 
   deeply with both to answer completely.

3. Decomposability
   → Did the question naturally trigger multi-piece breakdown within boundary?
   → Student should identify multiple connected pieces — all within learning 
     objective boundary
   → More pieces naturally identified → richer decomposition → better question

   Example (score: 0.85):
   Student naturally decomposed into:
   piece 1 → understand A as transformation
   piece 2 → compute eigenvalues
   piece 3 → find eigenvectors
   piece 4 → interpret physically
   All 4 pieces within boundary. Nobody told student there were 4 parts.

4. Domain Coherence
   → Does the question stay within the scenario domain naturally?
   → Question should feel natural — not forced or disconnected from context

   Example (score: 0.90):
   Bridge deformation is the domain. Matrix A, wind load, deformation 
   directions — all feel natural within that domain. No drift into 
   abstract mathematics without physical meaning.

5. Boundary Adherence
   → Did the student attempt stay within learning objective boundary?
   → Student should not have needed knowledge beyond the learning objectives

   Example (score: 0.85):
   Student used only transformation interpretation and eigenvalue computation 
   throughout the attempt. No advanced spectral theory, no Jordan forms, 
   no knowledge beyond what the two learning objectives establish.

## Scoring Instructions
- Score each dimension from 0.0 to 1.0
- Be consistent and comparative across all questions
- Base scores on both question structure and student attempt as evidence
- Provide a short reason for each question

## Output Format
Return JSON only. No preamble. No explanation.

[
    {{
        "id": "q1",
        "scores": {{
            "learning_objective_reflection": 0.0,
            "cognitive_load_balance": 0.0,
            "decomposability": 0.0,
            "domain_coherence": 0.0,
            "boundary_adherence": 0.0
        }},
        "reason": "..."
    }}
]
"""