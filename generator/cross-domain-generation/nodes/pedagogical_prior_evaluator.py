import json
from config import get_llm, update_token_usage
from state import GraphState
from prompts.predagogical_prior_evaluator import PEDAGOGICAL_PRIOR_EVALUATOR_PROMPT


llm=get_llm(temperature=0)

THRESHOLD = 0.7
MAX_RETRY = 3

WEIGHTS = {
    "learning_objective_reflection": 0.35,
    "cognitive_load_balance"       : 0.25,
    "decomposability"              : 0.20,
    "domain_coherence"             : 0.10,
    "boundary_adherence"           : 0.10
}

def compute_overall_score(scores: dict) -> float:
    return sum(scores[dim] * WEIGHTS[dim] for dim in WEIGHTS)

def format_questions_and_attempts(
    questions: list,
    attempts: list
) -> str:
    result = ""
    attempts_map = {a["question_id"]: a for a in attempts}

    for q in questions:
        attempt = attempts_map.get(q["id"], None)
        if not attempt:
            continue
        if not attempt["solvability"]["solvable"]:
            continue

        result += f"Question ID: {q['id']}\n"
        result += f"Question: {q['question']}\n\n"
        result += f"Student Thought Process:\n"
        for step in attempt["thought_process"]:
            result += f"  {step}\n"
        result += f"Student Attempt: {attempt['attempt']}\n"
        result += f"Student Conclusion: {attempt['conclusion']}\n"
        result += f"Student Confidence: {attempt['student_confidence']}\n\n"
        result += "---\n\n"

    return result


def pedagogical_prior_evaluator(state: GraphState) -> GraphState:
    questions = state["generated_questions"]
    attempts = state["student_attempts"]

    formatted = format_questions_and_attempts(questions, attempts)

    prompt=PEDAGOGICAL_PRIOR_EVALUATOR_PROMPT.format(
        topic_1=state["topic_1"],
        learning_objective_1=state["learning_objective_1"],
        topic_2=state["topic_2"],
        learning_objective_2=state["learning_objective_2"],
        questions_and_attempts = formatted
    )

    response = llm.invoke(prompt)
    update_token_usage("pedagogical_prior_evaluator", response)


    try:
        raw = response.content.strip()
        evaluations = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error":"Pedagogical prior evaluator returned invalid JSON",
            "question_retry_count": state.get("question_retry_count", 0) + 1
        }
    # compute overall score for each questions
    for evaluation in evaluations:
        evaluation["overall_score"] = compute_overall_score(evaluation["scores"])
    
    # rank by overall score
    ranked = sorted(
        evaluations, key=lambda x:x["overall_score"],
        reverse=True
    )
    best = ranked[0]


    # check threshold
    if best["overall_score"] < THRESHOLD:
        retry = state.get("question_retry_count", 0)+1
        if retry >=MAX_RETRY:
            return {
                **state,
                "error" : f"No question passed threshold {THRESHOLD} after {MAX_RETRY}",
                "question_retry_count" : retry
            }
        # feedback for pedagogical prior failure
        return {
            **state,
            "question_retry_count" : retry,
            "question_feedback": {
                "source": "pedagogical_prior",
                "attempts":attempts,
                "evaluations": evaluations

            },
            "error":""
        }
    # find best question
    best_question = next(
        (q for q in questions if q["id"] == best["id"]), None)
    
    # best student attempt
    best_attempt = next((a for a in attempts if a["question_id"]==best["id"]), None)

    return {
        **state,
        "evaluated_pairs" : [{
            "question": best_question,
            "student_attempt": best_attempt,
            "overall_score": best["overall_score"],
            "dimension_scores": best["scores"],
            "reason": best["reason"]
        }],
        "error":""
    }
