import json
from config import get_llm,update_token_usage
from state import GraphState
from prompts.student_agent import STUDENT_AGENT_PROMPT

llm = get_llm(temperature=0.5)

def student_agent(state: GraphState) -> GraphState:
    questions = state["generated_questions"]

    # formatted_questions
    formatted_questions=""
    for q in questions:
        formatted_questions += f"Question ID: {q['id']}\n"
        formatted_questions += f"Question: {q['question']}\n\n"
    prompt = STUDENT_AGENT_PROMPT.format(
        questions=formatted_questions
    )
    
    response=llm.invoke(prompt)
    update_token_usage("student_agent", response)
    try:
        raw = response.content.strip()
        attempts = json.loads(raw)
    except json.JSONDecodeError:
        return {
            **state,
            "error": "Student agent returned invalid JSON."
        }
    return {
        **state,
        "student_attempts":attempts,
        "error":""
    }