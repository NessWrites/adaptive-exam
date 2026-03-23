from sqlalchemy.orm import Session 
from backend.app.models.database_models import SubjectiveQuestion, MCQQuestion 


class MCQRepository: 
    def __init__(self, db: Session): 
        self.db = db 
        
    
    def get_subjective_questions(self, question_id: int) -> SubjectiveQuestion: 
        """fetch the original subjective question by id"""
        return self.db.query(SubjectiveQuestion).filter(SubjectiveQuestion.id == question_id).first()
    
    def save_mcq(self, original_sub_q: SubjectiveQuestion, mcq_data: dict, target_bloom_level: int) -> MCQQuestion: 
        
        """
        Persist an assembled MCQ to mcq_questions_converted.

        Expected mcq_data shape (post DistractorBridge):
          {
            "question_text": str,
            "options":         {"A": str, "B": str, "C": str, "D": str},
            "correct_answer":  {"key": str, "text": str},   # e.g. {"key": "B", "text": "O(n log n)"}
            "explanation":     str,
          }

        The `options` and `correct_answer` fields are stored as JSON
        in PostgreSQL and are queryable via SQLAlchemy's JSON operators.
        """
        required_keys = {"question_text", "options", "correct_answer", "explanation"}
        missing = required_keys - mcq_data.keys()
        if missing:
            raise ValueError(
                f"save_mcq called with incomplete mcq_data. Missing keys: {missing}"
            )

        
        
        new_mcq = MCQQuestion(
            domain = original_sub_q.domain,
            concept_tag = original_sub_q.concept_tag,
            question_text = mcq_data["question_text"],
            options = mcq_data["options"],
            correct_answer = mcq_data['correct_answer'],
            explanation = mcq_data["explanation"],
            validation_score = mcq_data.get("validation_score"),
            question_type = "mcq",
            a_values  = [0.0, 0.0],
            b_value = 0.0,
            calibration_status = "pretest",
            
            bloom_level = target_bloom_level, 
            derived_from_subjective_id = original_sub_q.id,
            
                    
        )
        
        self.db.add(new_mcq)
        self.db.commit()
        self.db.refresh(new_mcq)
        return new_mcq 
    