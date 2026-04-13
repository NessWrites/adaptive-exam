import json
from unittest import result
from graph import graph


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run(topic_1: str, topic_2: str, stratum: str =""):
    initial_state = {
        "topic_1": topic_1,
        "topic_2": topic_2,
        "learning_objective_1": "",
        "learning_objective_2": "",
        "generated_scenarios": [],
        "scenario_retry_count": 0,
        "top_scenario": {},
        "question_type": "",
        "question_type_reason": "",
        "generated_questions": [],
        "question_retry_count": 0,
        "question_feedback": None,
        "student_attempts": [],
        "evaluated_pairs": [],
        "final_output": {},
        "error": "",
        "stratum": stratum
    }

    result = graph.invoke(initial_state)

    if result["error"]:
        print("\n❌ ERROR:", result["error"])
        return

    # ── Input Validator ────────────────────────────────────
    print_separator("INPUT VALIDATOR")
    print(f"Topic 1             : {result['topic_1']}")
    print(f"Topic 2             : {result['topic_2']}")
    print(f"Learning Objective 1: {result['learning_objective_1']}")
    print(f"Learning Objective 2: {result['learning_objective_2']}")

    # ── Scenario Generator ─────────────────────────────────
    print_separator("SCENARIO GENERATOR")
    print(f"Total Generated     : {len(result['generated_scenarios'])}")
    for s in result["generated_scenarios"]:
        print(f"\n  [{s['id']}] {s['title']}")
        print(f"  Domain   : {s['domain']}")
        print(f"  Scenario : {s['scenario']}.")
        print(f"  Numerical Entry Points:")
        for point in s["numerical_entry_points"]:
            print(f"    - {point}")

    # ── Scenario Evaluator ─────────────────────────────────
    print_separator("SCENARIO EVALUATOR")
    print(f"Retry Count         : {result['scenario_retry_count']}")
    print(f"\nTop Scenario:")
    print(f"  Title             : {result['top_scenario']['title']}")
    print(f"  Domain            : {result['top_scenario']['domain']}")
    print(f"  Overall Score     : {result['top_scenario']['overall_score']:.2f}")
    print(f"  Reason            : {result['top_scenario']['reason']}")
    print(f"  Scenario          : {result['top_scenario']['scenario']}")
    print(f"\n  Dimension Scores:")
    for dim, score in result['top_scenario']['dimension_scores'].items():
        print(f"    {dim}: {score:.2f}")

    # ── Question Type Classifier ───────────────────────────
    print_separator("QUESTION TYPE CLASSIFIER")
    print(f"Question Type       : {result['question_type']}")
    print(f"Reason              : {result['question_type_reason']}")

    # ── Question Generator ─────────────────────────────────
    print_separator("QUESTION GENERATOR")
    if result["question_retry_count"] > 0:
        print(f"⚠️  Regenerated      : {result['question_retry_count']} time(s)")
    else:
        print(f"✅ Generated on first attempt")
    print(f"\nGenerated Questions:")
    for q in result["generated_questions"]:
        print(f"\n  [{q['id']}]")
        print(f"  Question         : {q['question']}")
        print(f"  Expected Concepts:")
        for concept in q["expected_concepts"]:
            print(f"    - {concept}")

    # ── Student Agent ──────────────────────────────────────
    print_separator("STUDENT AGENT")
    for attempt in result["student_attempts"]:
        print(f"\n  [{attempt['question_id']}]")
        print(f"  Thought Process:")
        for step in attempt["thought_process"]:
            print(f"    {step}")
        print(f"  Attempt          : {attempt['attempt']}.")
        print(f"  Conclusion       : {attempt['conclusion']}")
        print(f"  Confidence       : {attempt['student_confidence']:.2f}")
        print(f"  Solvable         : {attempt['solvability']['solvable']}")
        print(f"  Solvability Reason: {attempt['solvability']['reason']}")

    # ── Pedagogical Prior Evaluator ────────────────────────
    print_separator("PEDAGOGICAL PRIOR EVALUATOR")
    if result["evaluated_pairs"]:
        pair = result["evaluated_pairs"][0]
        print(f"Best Question      : {pair['question']['question']}")
        print(f"Overall Score      : {pair['overall_score']:.2f}")
        print(f"Reason             : {pair['reason']}")
        print(f"\nDimension Scores:")
        for dim, score in pair['dimension_scores'].items():
            print(f"  {dim}: {score:.2f}")
        print(f"\nStudent Thought Process:")
        for step in pair['student_attempt']['thought_process']:
            print(f"  {step}")
        print(f"Student Confidence : {pair['student_attempt']['student_confidence']:.2f}")
    else:
        print("No evaluated pairs found.")

if __name__ == "__main__":
    run(
        topic_1="conditional_probability",
        topic_2="information_theory_and_entropy",
        stratum="same"
    )