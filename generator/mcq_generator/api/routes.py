#expose the conversion logic as an endpoint 

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from backend.app.database.postgresql.connection import get_db 
from generator.mcq_generator.services.mcq_service import MCQService 


router = APIRouter(prefix = "/generator/mcq", tags = ["MCQ Generator"])

@router.post("/convert/{question_id}") 

async def convert_question(question_id: int, db: Session = Depends(get_db)): 
    """takes an existing subjective qid , converts it into an mcq via gemini and saves it to mcq table"""
    service = MCQService(db) 
    try: 
        new_mcq = await service.convert_subjective_to_mcq(question_id)
        return {
            "status": "success" ,
            "message": "Subjective question successfully converted to mcq",
            "data" : {
                "mcq_id": new_mcq.unique_id,
                "question_text": new_mcq.question_text, 
                "options": new_mcq.options,
                "correct_answer": new_mcq.correct_answer,
                "explanation": new_mcq.explanation
            }
        }
    
    except ValueError as e: 
        raise HTTPException(status_code= 404, detail = str(e))
    
    except Exception as e: 
        raise HTTPException(status_code= 500, detail = f"conversion failed: {str(e)}")
    