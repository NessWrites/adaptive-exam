import json
from config import get_llm, update_token_usage
from state import GraphState
from prompts.question_type_classifier import QUESTION_TYPE_CLASSIFIER_PROMPT

llm = get_llm(temperature=0)

def question_type_classifier(state: GraphState) -> GraphState:
    top_scenario = state["top_scenario"]

    prompt = QUESTION_TYPE_CLASSIFIER_PROMPT.format(
        topic_1=state['topic_1'],
        learning_objective_1=state["learning_objective_1"],
        topic_2=state["topic_2"],
        learning_objective_2=state["learning_objective_2"],
        scenario=top_scenario["scenario"],
        numerical_entry_points=json.dumps(top_scenario["numerical_entry_points"], indent=2)
    )

    response = llm.invoke(prompt)
    update_token_usage("question_type_classifier", response)

    try:
        raw = response.content.strip()
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error": "Question type classifier returned invalid JSON."
        }
    valid_types = ["numerical", "conceptual", "mixed"]
    if result["question_type"] not in valid_types:
        return {
            **state,
            "error": f"Invalid question type returned: {result["question_type"]}"
        }
    return {
        **state,
        "question_type": result["question_type"],
        "question_type_reason" : result["reason"],
        "error":""
    }