import json
from state import GraphState
from config import get_llm, update_token_usage
from prompts.scenario_generator import SCENARIO_GENERATOR_PROMPT



llm = get_llm()


def scenario_generator(state: GraphState) -> GraphState:
    prompt = SCENARIO_GENERATOR_PROMPT.format(
        topic_1=state["topic_1"],
        learning_objective_1=state["learning_objective_1"],
        topic_2=state["topic_2"],
        learning_objective_2=state["learning_objective_2"]
    )

    response = llm.invoke(prompt)
    update_token_usage("scenario_generator", response)

    try:
        raw = response.content.strip()
        scenarios = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error": "Scenario generator returned invalid JSON.",
            "scenario_retry_count": state.get("scenario_retry_count", 0) + 1
        }

    return {
        **state,
        "generated_scenarios": scenarios,
        "scenario_retry_count": state.get("scenario_retry_count", 0),
        "error": ""
    }