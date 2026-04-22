#expose the conversion logic as an endpoint 

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session 
from backend.app.database.postgresql.connection import get_db 
from generator.mcq_generator.services.mcq_service import MCQService 
from generator.mcq_generator.services.distractor_bridge import DistractorBridge
from generator.mcq_generator.services.distractor_config_adapter import get_distractor_config
from typing import List

router = APIRouter(prefix = "/generator/mcq", tags = ["MCQ Generator"])


def get_distractor_bridge() -> DistractorBridge:
    """
    FastAPI dependency that provides a DistractorBridge instance.
    The bridge uses a singleton DistractorConfigAdapter (via lru_cache),
    so DistractorManager is only instantiated once per process.
    """
    return DistractorBridge(config=get_distractor_config())




@router.post("/convert/{question_id}") 

async def convert_question(question_id: int, 
                            num_variants: int = Query(1,ge=1, le=4),
                            target_bloom_levels: List[int] = Query(None), #optional list
                            db: Session = Depends(get_db),
                            distractor_bridge: DistractorBridge = Depends(get_distractor_bridge),): 
    """Takes an existing question (subjective or code) by ID, converts it into MCQ(s) via Gemini and saves to mcq table."""
    service = MCQService(db=db, distractor_bridge= distractor_bridge) 
    
    if target_bloom_levels and len(target_bloom_levels) > 4 : 
        raise HTTPException(
            status_code= 422,
            detail="cannot request more than 4 bloom "
        )
    try: 
        # Auto-detects question type (subjective or code)
        new_mcqs = await service.convert_to_mcq(
            question_id=question_id, 
            num_variants=num_variants, 
            target_levels= target_bloom_levels
        )
        
        return {
            "status": "success",
            "count": len(new_mcqs),
            "data": [{"id": m.id, "bloom": m.bloom_level} for m in new_mcqs],
        }
        
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))