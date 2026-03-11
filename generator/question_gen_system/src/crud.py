from sqlalchemy.orm import Session 
from backend.app.models.database_models import SubjectiveQuestion

def save_subjective_question(
    db: Session, 
    domain: str, 
    unit: str, 
    topic: str, 
    level: int,
    question: str,
    total_marks: int
) -> SubjectiveQuestion: 
    """parse llm output and save to subjective_questions table"""
    
    concept_tag = f"{unit} / {topic}"
    
    #create the db record 
    new_question = SubjectiveQuestion(
        domain=domain,
        bloom_level=level, 
        concept_tag=concept_tag, 
        question_text=question,
        mark_schema=None,
        correct_answer=None,
        a_values=[0,0],
        b_value=0,
        calibration_status="pretest",
        question_type="subjective",
        total_marks = total_marks
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question) 
    
    return new_question