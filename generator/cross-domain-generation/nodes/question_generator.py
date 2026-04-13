import json
from config import get_llm, update_token_usage
from state import GraphState
from prompts.question_generator import QUESTION_GENERATOR_PROMPT


llm = get_llm(temperature=1)

def format_feedback(feedback: dict) -> str:
    if not feedback:
        return "No feedback. Generate questions normally."

    source = feedback.get("source", "solvability")

    if source == "solvability":
        attempts = feedback.get("attempts", [])
        formatted = "Previous questions failed solvability check.\n"
        formatted += "Student attempts showing where and why each question failed:\n\n"
        for attempt in attempts:
            formatted += f"Question ID: {attempt['question_id']}\n"
            formatted += f"Thought Process:\n"
            for step in attempt["thought_process"]:
                formatted += f"  {step}\n"
            formatted += f"Attempt: {attempt['attempt']}\n"
            formatted += f"Conclusion: {attempt['conclusion']}\n"
            formatted += f"Solvability Reason: {attempt['solvability']['reason']}\n\n"
        formatted += "Regenerate questions addressing these specific failures."
        return formatted

    if source == "pedagogical_prior":
        evaluations = feedback.get("evaluations", [])
        formatted = "Previous questions failed pedagogical prior evaluation.\n"
        formatted += "Evaluation results showing why each question was rejected:\n\n"
        for evaluation in evaluations:
            formatted += f"Question ID: {evaluation['id']}\n"
            formatted += f"Overall Score: {evaluation['overall_score']:.2f}\n"
            formatted += f"Dimension Scores:\n"
            for dim, score in evaluation["scores"].items():
                formatted += f"  {dim}: {score}\n"
            formatted += f"Reason: {evaluation['reason']}\n\n"
        formatted += "Regenerate questions addressing these specific weaknesses."
        return formatted

def question_generator(state: GraphState) -> GraphState:
    top_scenario = state["top_scenario"]
    feedback = state.get("question_feedback", None)

    prompt = QUESTION_GENERATOR_PROMPT.format(
        topic_1=state["topic_1"],
        learning_objective_1=state["learning_objective_1"],
        topic_2=state["topic_2"],
        learning_objective_2=state["learning_objective_2"],
        scenario=top_scenario["scenario"],
        numerical_entry_points=json.dumps(
            top_scenario["numerical_entry_points"], indent=2
        ),
        question_type=state["question_type"],
        feedback=format_feedback(feedback)
    )

    response = llm.invoke(prompt)
    update_token_usage("question_generator", response)
    try:
        raw = response.content.strip()
        questions = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error": "Question generator returned invalid JSON.",
            "question_retry_count": state.get("question_retry_count", 0) + 1
        }

    return {
        **state,
        "generated_questions": questions,
        "question_retry_count": state.get("question_retry_count", 0),
        "error": ""
    }