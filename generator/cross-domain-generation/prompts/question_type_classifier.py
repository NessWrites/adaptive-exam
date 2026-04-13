QUESTION_TYPE_CLASSIFIER_PROMPT = """
You are a question type classifier for an advanced learning system.

You will be given a hypothetical scenario generated from 2 topics and their learning objectives.

## Topics and Learning Objectives
Topic 1: {topic_1}
Learning Objective 1: {learning_objective_1}

Topic 2: {topic_2}
Learning Objective 2: {learning_objective_2}

## Scenario
{scenario}

## Numerical Entry Points
{numerical_entry_points}

## Your Task
Decide which question type best fits this scenario naturally:

- numerical: scenario has clear computable structures, 
  measurable quantities, and mathematical parameters. 
  A student can compute, calculate, and derive answers.

- conceptual: scenario is rich in ideas, relationships, 
  and reasoning but does not naturally produce computable 
  structures. A student explains, interprets, and analyzes.

- mixed: scenario has both computable structures AND 
  rich conceptual reasoning. A student computes and interprets.

## Rules
- Let the scenario decide — do not force a type
- If numerical_entry_points are strong and concrete → lean numerical
- If numerical_entry_points are weak or abstract → lean conceptual
- If both are present equally → mixed

## Output Format
Return JSON only. No preamble. No explanation.

{{
    "question_type": "numerical",
    "reason": "..."
}}
"""