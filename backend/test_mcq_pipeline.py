import asyncio
import os
import sys

from backend.app.database.postgresql.connection import SessionLocal
from generator.mcq_generator.services.mcq_service import MCQService
from generator.mcq_generator.services.distractor_bridge import DistractorBridge
from backend.app.models.database_models import SubjectiveQuestion

async def run_test():
    # Setup
    db = SessionLocal()
    distractor_bridge = DistractorBridge()
    service = MCQService(db=db, distractor_bridge=distractor_bridge)
    
    # Use any existing SubjectiveQuestion ID from DB
    subjective_q = db.query(SubjectiveQuestion).first()
    
    if not subjective_q:
        print("No subjective questions in database. Please add one to run this test.")
        db.close()
        return
        
    print(f"Testing generation for Subjective Question ID: {subjective_q.id}")
    try:
        results = await service.convert_subjective_to_mcq(
            question_id=subjective_q.id,
            num_variants=1,
            target_levels=[2] # Just generate one for speed
        )
        
        for idx, mcq in enumerate(results):
            print(f"\\n--- Generated MCQ {idx+1} ---")
            print(f"Stem: {mcq.question_text}")
            print(f"Options: {mcq.options}")
            print(f"Correct Answer: {mcq.correct_answer}")
            print(f"Explanation: {mcq.explanation}")
            print(f"Validation Score: {mcq.validation_score}")
        print("\\nSUCCESS!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
