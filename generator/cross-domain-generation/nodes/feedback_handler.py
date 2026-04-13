from state import GraphState

def feedback_handler(state: GraphState) -> GraphState:
    attempts = state.get("student_attempts", [])

    return {
        **state,
        "question_feedback" : {
            "attempts" : attempts
        },
        "question_retry_count" : state.get("question_retry_count", 0) + 1
    }