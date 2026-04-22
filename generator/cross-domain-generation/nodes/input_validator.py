import json
from state import GraphState

def load_topics(path: str = "generator/cross-domain-generation/data/topics.json")-> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return {item["topic"]: item["learning_objective"] for item in data}


def input_validator(state: GraphState)-> GraphState:
    topic_1 = state["topic_1"]
    topic_2 = state['topic_2']

    topics_dict = load_topics()

    # check if same topic
    if topic_1 == topic_2:
        return {
            **state,
            "error" : f"topic_1 and topic_2 cannot be same: '{topic_1}'"
        }
    
    # check if topic_1 exists
    if topic_1 not in topics_dict:
        return {
            **state,
            "error" : f"'{topic_1}' not found in topics dictionary"
        }
    # check if topic_2 exists
    if topic_2 not in topics_dict:
        return {
            **state,
            "error" : f"'{topic_2}' not found in topics dictionary"
        }
    
    # all valid
    return {
        **state,
        "learning_objective_1" : topics_dict[topic_1],
        "learning_objective_2" : topics_dict[topic_2],
        "error" : ""
    }