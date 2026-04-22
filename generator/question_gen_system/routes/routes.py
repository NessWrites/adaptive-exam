from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from generator.question_gen_system.src.ingestion.schema_loader import get_schema
from generator.question_gen_system.src.core.generator import SkeletonGenerator
from generator.question_gen_system.src.agents.question_agent import HydrationAgent
from generator.question_gen_system.src.schemas.items_schema import LLMQuestionResponse
from generator.question_gen_system.src.services.processer import split_question
from generator.question_gen_system.src.services.validator import validate_batch
from generator.question_gen_system.src.pipeline.batch_buffer import add_to_buffer, current_buffer_size

from generator.question_gen_system.src import crud
from backend.app.models import database_models as models

from backend.app.database.postgresql.connection import get_db, engine

#initialize db table if no table creates one does not work for migration 
# models.Base.metadata.create_all(bind = engine)  #use alembic in prod

#the above line created problem for generating alembic migrations, this skipped table creation
#alembic is notorious for not catching checkconstraints but not create tables!!


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
    unit: str = Query(..., example = "Linear Algebra"),
    topic: str = Query(..., example = "Transformations"),
    level: int = Query(..., example = 2),
    num_questions: int = Query(..., example = 4),
    db: Session = Depends(get_db)):

    try: 
        concept, skeleton, context = gen.generate_skeleton(domain, unit, topic, level)
    except ValueError as e: 
        raise HTTPException(status_code = 404, detail = str(e))
    
    result = await agent.hydrate(domain, concept, level, skeleton, num_questions)
    
    if "error" in result:
        raise HTTPException(
            status_code = 500,
            detail=f"{result.get('error')} — {result.get('details', 'no details')}"
        )
    
    parsed = LLMQuestionResponse.model_validate(result)

    question_rows = split_question(parsed, domain, unit, topic,context, level)

    batch = add_to_buffer(question_rows)

    validator_response = None
    saved_info = []
    success_length = 0
    validator_length = 0
    
    if batch:
        validator_response = validate_batch(batch)

    
    if validator_response:
         
        for item in validator_response:
            if item["bloom_score"] == item["context_score"] == 1:
                try:
                    db_record = crud.save_subjective_question(
                        db=db,
                        domain=item['domain'],
                        unit=item['unit'],
                        topic=item['topic'],
                        level=item['bloom_level'],
                        question=item['question'],
                        total_marks=item['total_marks']
                    )
                    saved_info.append({
                        "id" : db_record.id,
                        "status" : "saved to subjective_questions table"
                    })
                except Exception as e:
                    print(f"DB error: {e}")
                    saved_info.append({
                        "status" : "Failed to save",
                        "error" : str(e)
                    })

        success_length = len([s for s in saved_info if "id" in s])
        validator_length = len(validator_response)

    return {
        "generated_content": {
            "generated_questions" : [row.model_dump() for row in question_rows], 
            "topic": topic,
            "buffer_size" : current_buffer_size(),
            "batch_sent_to_validator": batch is not None,
            "validator_result": validator_response,
        },
        "log" : f"Saved: {success_length}/{validator_length}",
        "database_log": saved_info
        }