import importlib.util
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator


def _load_cross_domain_graph():
    """Load graph from the hyphenated folder using importlib."""
    root_dir = Path(__file__).resolve().parents[3]
    cross_domain_dir = root_dir / "generator" / "cross-domain-generation"
    graph_file = cross_domain_dir / "graph.py"

    if str(cross_domain_dir) not in sys.path:
        sys.path.insert(0, str(cross_domain_dir))

    spec = importlib.util.spec_from_file_location("cross_domain_graph", graph_file)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load cross-domain graph module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.graph


graph = _load_cross_domain_graph()

router = APIRouter(prefix="/cross-domain", tags=["Cross Domain Generation"])


class CrossDomainRequest(BaseModel):
    topic_1: str = Field(..., min_length=1)
    topic_2: str = Field(..., min_length=1)
    stratum: str = ""

    @field_validator("topic_1", "topic_2", "stratum", mode="before")
    @classmethod
    def normalize_lower(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value


@router.post("/generate")
async def generate_cross_domain(payload: CrossDomainRequest):
    initial_state = {
        "topic_1": payload.topic_1,
        "topic_2": payload.topic_2,
        "learning_objective_1": "",
        "learning_objective_2": "",
        "generated_scenarios": [],
        "scenario_retry_count": 0,
        "top_scenario": {},
        "question_type": "",
        "question_type_reason": "",
        "generated_questions": [],
        "question_retry_count": 0,
        "question_feedback": None,
        "student_attempts": [],
        "evaluated_pairs": [],
        "final_output": {},
        "error": "",
        "stratum": payload.stratum,
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {exc}") from exc

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    best_question = None
    student_confidence = None
    if result.get("evaluated_pairs"):
        pair = result["evaluated_pairs"][0]
        best_question = pair.get("question", {}).get("question")
        student_confidence = pair.get("student_attempt", {}).get("student_confidence")

    return {
        "top_scenario": result.get("top_scenario", {}),
        "question_type": result.get("question_type", ""),
        "best_question": best_question,
        "student_confidence": student_confidence,
    }
