import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm(temperature: float = 1):
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key = os.getenv("GROQ_API_KEY")
    )


token_usage = {
    "scenario_generator": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "scenario_evaluator": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "question_type_classifier": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "question_generator": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "student_agent": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "pedagogical_prior_evaluator": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
    "total": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0}
}


def update_token_usage(node: str, response):
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        input_tokens = response.usage_metadata.get("input_tokens", 0)
        output_tokens = response.usage_metadata.get("output_tokens", 0)
        total_tokens = response.usage_metadata.get("total_tokens", 0)

        token_usage[node]["input_tokens"] += input_tokens
        token_usage[node]["output_tokens"] += output_tokens
        token_usage[node]["total_tokens"] += total_tokens
        token_usage[node]["requests"]+= 1

        token_usage["total"]["input_tokens"] += input_tokens
        token_usage["total"]["output_tokens"] += output_tokens
        token_usage["total"]["total_tokens"] += total_tokens
        token_usage["total"]["requests"]+= 1


def reset_token_usage():
    for key in token_usage:
        token_usage[key] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0}