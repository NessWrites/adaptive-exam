import json
import os
from config import token_usage
from state import GraphState

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


def file_output(state: GraphState) -> GraphState:
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        topic_1 = state["topic_1"]
        topic_2 = state["topic_2"]
        pair = state["evaluated_pairs"][0]

        output = {
            "run_info": {
                "topic_1": topic_1,
                "topic_2": topic_2,
                "learning_objective_1": state["learning_objective_1"],
                "learning_objective_2": state["learning_objective_2"],
                "stratum": state.get("stratum", ""),
                "question_type": state["question_type"],
                "scenario_retry_count": state["scenario_retry_count"],
                "question_retry_count": state["question_retry_count"],
                "success": True
            },
            "top_scenario": {
                "title": state["top_scenario"]["title"],
                "domain": state["top_scenario"]["domain"],
                "scenario": state["top_scenario"]["scenario"],
                "overall_score": state["top_scenario"]["overall_score"],
                "dimension_scores": state["top_scenario"]["dimension_scores"],
                "reason": state["top_scenario"]["reason"]
            },
            "best_question": {
                "question": pair["question"]["question"],
                "expected_concepts": pair["question"]["expected_concepts"],
                "overall_score": pair["overall_score"],
                "dimension_scores": pair["dimension_scores"],
                "reason": pair["reason"]
            },
            "student_attempt": {
                "thought_process": pair["student_attempt"]["thought_process"],
                "attempt": pair["student_attempt"]["attempt"],
                "conclusion": pair["student_attempt"]["conclusion"],
                "student_confidence": pair["student_attempt"]["student_confidence"],
                "solvability": pair["student_attempt"]["solvability"]
            },
            "token_usage": {
                "per_node": {
                    "scenario_generator": token_usage["scenario_generator"],
                    "scenario_evaluator": token_usage["scenario_evaluator"],
                    "question_type_classifier": token_usage["question_type_classifier"],
                    "question_generator": token_usage["question_generator"],
                    "student_agent": token_usage["student_agent"],
                    "pedagogical_prior_evaluator": token_usage["pedagogical_prior_evaluator"]
                },
                "total": token_usage["total"]
            }
        }

        filename = os.path.join(OUTPUT_DIR, f"{topic_1}__{topic_2}.json")
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)

        return {
            **state,
            "final_output": output,
            "error": ""
        }

    except Exception as e:
        return {
            **state,
            "error": f"File output failed: {str(e)}"
        }