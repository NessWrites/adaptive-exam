from sqlalchemy.orm import Session 
from backend.app.models.database_models import SubjectiveQuestion, MCQQuestion 


class MCQRepository: 
    def __init__(self, db: Session): 
        self.db = db 
        
    
    def get_subjective_questions(self, question_id: int) -> SubjectiveQuestion: 
        """fetch the original subjective question by id"""
        return self.db.query(SubjectiveQuestion).filters(SubjectiveQuestion.id == question_id).first()
    
    def save_mcq(self, original_sub_q: SubjectiveQuestion, mcq_data: dict) -> MCQQuestion: 
        """Save the newly generated MCQ utilizing you existing MCQQUESTION table mapping """
        
        new_mcq = MCQQuestion(
            domain = original_sub_q.domain,
            concept_tag = original_sub_q.concept_tag,
            question_text = mcq_data["question_text"],
            options = mcq_data["options"],
            explanations = mcq_data["explanation"],
            question_type = "mcq",
            a_values  = [0.0, 0.0],
            b_values = 0.0,
            calibration_status = "pretest"
                    
        )
        
        self.db.add(new_mcq)
        self.db.commit()
        self.db.refresh(new_mcq)
        return new_mcq 
    