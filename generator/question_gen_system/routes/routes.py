from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from generator.question_gen_system.src.ingestion.schema_loader import get_schema
from generator.question_gen_system.src.core.generator import SkeletonGenerator
from generator.question_gen_system.src.agents.question_agent import HydrationAgent


#db imports 
from generator.question_gen_system.src.database import get_db, engine 
from generator.question_gen_system.src import models, crud 

#initialize db table if no table creates one does not work for migration 
models.Base.metadata.create_all(bind = engine)  #use alembic in prod

load_dotenv()

router = APIRouter()

schema = get_schema()
# init generator with schema
gen = SkeletonGenerator(schema)
agent = HydrationAgent(api_key = os.getenv("GEMINI_API_KEY"))

@router.get("/generator")
async def generator(
    domain: str = Query(..., example ="math"),
    unit: str = Query(..., example = "Calculus"),
    topic: str = Query(..., example = "Ordinary Derivatives"),
    level: int = Query(..., example = 3),
    save_to_db: bool = Query(True, description= "Save generated question to Postgres"),
    db: Session = Depends(get_db) ):
    try: 
        concept, skeleton = gen.generate_skeleton(domain, unit, topic, level)
    except ValueError as e: 
        raise HTTPException(status_code = 404, detail = str(e))
    
    #hydrate skeleton(ai)
    result = await agent.hydrate(domain, concept, level, skeleton)

    if "error" in result: 
        raise HTTPException(status_code = 500, detail = result['details'])
    
    saved_info = None 
    if save_to_db: 
        try: 
            db_record = crud.save_subjective_question(
                db = db, 
                domain= domain,
                unit= unit,
                topic= topic,
                level= level,
                concept_id = concept, 
                skeleton = skeleton, 
                ai_data = result,
            )
            saved_info = {"id": db_record.id,
                          "status": "Saved to subjective_questions table"}    
        
        except Exception as e: 
            print(f"DB error : {e}")
            saved_info = {"status": "Failed to save", "error": str(e)}
            
            
            
        
    return {
        "generated_content": {
            "domain": domain, 
            "topic": topic,
            "question": result
        },
        "database_log": saved_info
        }
