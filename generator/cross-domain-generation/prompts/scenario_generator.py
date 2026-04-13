SCENARIO_GENERATOR_PROMPT = """
You are a hypothetical scenario generator for an advanced learning system.

You are given 2 topics and their learning objectives.

## Input
Topic 1: {topic_1}
Learning Objective 1: {learning_objective_1}

Topic 2: {topic_2}
Learning Objective 2: {learning_objective_2}

## What is a Hypothetical Scenario
A hypothetical scenario is a structured narrative that places the given 
learning objectives as active, causally necessary mechanisms within a 
coherent context.

The scenario:
- Does not need to be real or proven. It can be:
  * Currently real and happening
  * Plausible but unexplored
  * Purely speculative or theoretical
- Can be set in ANY most suitable domain
- Must structurally collapse if any single learning objective 
  is removed
- Must be numerically fertile — it must contain or naturally 
  imply measurable quantities, parameters, variables, or 
  computable structures that can be expressed mathematically
- Learning objectives are not background context — they are 
  the active working steps inside the scenario

## Constraints
1. Every learning objective must be a causally necessary step 
   in the scenario — not decoration
2. The domain is free but the mathematical structure is fixed 
   by the learning objectives
3. Generate exactly 3 scenarios — each must be distinct in 
   domain or approach
4. Do not explain what the topics are — assume the reader has 
   mastered all learning objectives
5. Do not generate tutorials, use cases, or exam questions

## Output Format
Return a JSON array only. No preamble. No explanation.

[
  {{
    "id": "s1",
    "title": "...",
    "domain": "...",
    "scenario": "...",
    "steps": [
      {{
        "topic": "...",
        "learning_objective": "...",
        "role_in_scenario": "..."
      }}
    ],
    "numerical_entry_points": [
      "..."
    ]
  }}
]
"""