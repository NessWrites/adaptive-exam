from typing import Annotated
from typing_extensions import TypedDict

# create state to capture the messages
class GraphState(TypedDict):
    # input
    topic_1: str
    topic_2: str
    learning_objective_1: str
    learning_objective_2: str

    # scenario generation
    generated_scenarios: list[dict]
    scenario_retry_count: int

    # scenario selection
    top_scenario: dict

    # question type
    question_type: str
    question_type_reason: str

    # question generation
    generated_questions: list[dict]
    question_retry_count: int

    # student attempts and evaluation
    student_attempts: list[dict]
    evaluated_pairs: list[dict]
    question_feedback: dict

    # final output and errors
    final_output: dict
    error: str
    stratum: str # same, adjacent, distant
