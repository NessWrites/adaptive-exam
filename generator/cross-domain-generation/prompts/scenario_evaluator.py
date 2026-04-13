SCENARIO_EVALUATOR_PROMPT = """
You are a pedagogical evaluator with deep knowledge of learning design principles.

You will be given 3 hypothetical scenarios generated from these 2 topics and their learning objectives:

Topic 1: {topic_1}
Learning Objective 1: {learning_objective_1}

Topic 2: {topic_2}
Learning Objective 2: {learning_objective_2}

## Scenarios
{generated_scenarios}

## Evaluation Criteria
Evaluate all 3 scenarios based on:

1. Learning Objective Fidelity
   → Are both learning objectives causally necessary mechanisms — not background decoration?

2. Cognitive Load Balance
   → Do both topics contribute equally to the scenario or does one dominate?

3. Numerical Fertility
   → Does the scenario naturally imply measurable, computable structures?

4. Conceptual Depth
   → Does the intersection of the two topics reveal something non obvious?

5. Domain Coherence
   → Does the domain make the mathematical structure feel natural?

## Scoring Instructions
- Score each dimension from 0.0 to 1.0 for each scenario
- Be consistent and comparative across all 3 scenarios
- Provide a short reason for each scenario

## Output Format
Return JSON only. No preamble. No explanation.

[
    {{
        "id": "s1",
        "scores": {{
            "learning_objective_fidelity": 0.0,
            "cognitive_load_balance": 0.0,
            "numerical_fertility": 0.0,
            "conceptual_depth": 0.0,
            "domain_coherence": 0.0
        }},
        "reason": "..."
    }}
]
"""