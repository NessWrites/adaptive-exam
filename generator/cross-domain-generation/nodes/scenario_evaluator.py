import json
from config import get_llm, update_token_usage
from state import GraphState
from prompts.scenario_evaluator import SCENARIO_EVALUATOR_PROMPT

llm = get_llm(temperature=0)

THRESHOLD = 0.7
MAX_RETRY = 3

WEIGHTS = {
    "learning_objective_fidelity": 0.30,
    "cognitive_load_balance"     : 0.20,
    "numerical_fertility"        : 0.20,
    "conceptual_depth"           : 0.20,
    "domain_coherence"           : 0.10
}

def compute_overall_score(scores: dict) -> float:
    return sum(scores[dim]*WEIGHTS[dim] for dim in WEIGHTS)



def scenario_evaluator(state: GraphState) -> GraphState:
    prompt = SCENARIO_EVALUATOR_PROMPT.format(
        topic_1 = state["topic_1"],
        learning_objective_1=state["learning_objective_1"],
        topic_2=state["topic_2"],
        learning_objective_2=state["learning_objective_2"],
        generated_scenarios=json.dumps(state["generated_scenarios"], indent=2)
    )

    response = llm.invoke(prompt)
    update_token_usage("scenario_evaluator", response)

    try:
        raw = response.content.strip()
        evaluations = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error":"Scenario evaluator returned invalid JSON.",
            "scenario_retry_count": state.get("scenario_retry_count", 0) + 1
        }
    
    for evaluation in evaluations:
        evaluation["overall_score"] = compute_overall_score(evaluation["scores"])
    
    # rank by overall score
    ranked = sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)
    best = ranked[0]

    # check threshold
    if best["overall_score"] < THRESHOLD:
        retry = state.get("scenario_retry_count", 0) + 1
        if retry >= MAX_RETRY:
            return {
                **state,
                "error" : f"No Scenario passed threshold {THRESHOLD} after {MAX_RETRY} retries.",
                "scenario_retry_count" : retry
            }
        return {
            **state,
            "scenario_retry_count": retry,
            "error":""
        }
    
    # find best scenario object from generated list
    best_scenario = next(
        (s for s in state["generated_scenarios"] if s["id"] == best["id"]),
        None
    )

    return {
        **state,
        "top_scenario": {
            **best_scenario,
            "overall_score": best["overall_score"],
            "dimension_scores":best["scores"],
            "reason": best["reason"]
        },
        "scenario_retry_count":state.get("scenario_retry_count",0),
        "error":""
    }
    

