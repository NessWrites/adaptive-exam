from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from generator.question_gen_system.src.ingestion.schema_loader import get_schema
from generator.question_gen_system.src.core.generator import SkeletonGenerator
from generator.question_gen_system.src.agents.question_agent import HydrationAgent
from generator.question_gen_system.utils.csv_handler import dump_to_csv

load_dotenv()

router = APIRouter()

schema = get_schema()

# init generator with schema
gen = SkeletonGenerator(schema)

agent = HydrationAgent(api_key = os.getenv("GEMINI_API_KEY"))

@router.get("/generator")
async def generator(
    background_tasks: BackgroundTasks,
    domain: str = Query(..., example ="math"),
    unit: str = Query(..., example = "Calculus"),
    topic: str = Query(..., example = "Ordinary Derivatives"),
    level: int = Query(..., example = 3),
    num_questions: int = Query(..., example = 5)):
    concept, skeleton, context = gen.generate_skeleton(domain, unit, topic, level)

    result = await agent.hydrate(domain, concept, level, skeleton, num_questions)

    log_data = {
        "Domain" :domain,
        "Topic" :topic,
        "Context" : context,
        "Level" : level,
        "Response" : result,
    }
    background_tasks.add_task(dump_to_csv, log_data)
    return {
        "domain" : domain,
        "skeleton": skeleton,
        "question": result
    }
