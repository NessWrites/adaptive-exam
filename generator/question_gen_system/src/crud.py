from sqlalchemy.orm import Session 
from generator.question_gen_system.src.models import SubjectiveQuestion

import json 

def save_subjective_question(
    db: Session, 
    domain: str, 
    unit: str, 
    topic: str, 
    level: int, 
    concept_id: str, 
    skeleton: str, 
    ai_data: dict,
) -> SubjectiveQuestion: 
    """parse llm output and save to subjective_questions table"""
    
    #construct student facing question text 
    scenario = ai_data.get("scenario_expansion","")
    final_q = ai_data.get("final_question", "") 
    full_text = f"{scenario}\n\n{final_q}"
    
    
    steps = ai_data.get("solution_steps", [])
    final_ans = ai_data.get("final_answer", "")
    
    #create the db record 
    new_question = SubjectiveQuestion(
        domain = domain,
        unit = unit, 
        topic = topic, 
        bloom_level = level, 
        question_text = full_text, 
        concept_id = concept_id, 
        skeleton_used = skeleton, 
        correct_answer = final_ans, 
        solution_steps = steps, 
        
        a_value = 1.0, 
        b_value = 0.0,
        calibration_status = "pretest"
        
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question) 
    
    return new_question