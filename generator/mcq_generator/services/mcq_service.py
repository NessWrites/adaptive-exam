#connect the repository to the ai engine

from sqlalchemy.orm import Session 
from generator.mcq_generator.db.repository import MCQRepository 
from generator.mcq_generator.core.ai_engine import MCQEngine 

class MCQService: 
    def __init__(self, db: Session): 
        self.repo = MCQRepository(db)
        self.ai_engine = MCQEngine() 
        
    async def convert_subjective_to_mcq(self, question_id: int): 
        #fetch subjective question 
        subjective_q = self.repo.get_subjective_questions(question_id)
        if not subjective_q: 
            raise ValueError(f"SubjectiveQuestion with id {question_id} not found.")
        
        #run ai conversion 
        mcq_result = await self.ai_engine.generate_mcq(
            domain=subjective_q.domain,
            concept_tag = subjective_q.concept_tag,
            question_text = subjective_q.question_text,
        )
        
        #3 save to db 
        mcq_dict = mcq_result.model_dump() 
        new_mcq = self.repo.save_mcq(subjective_q, mcq_dict) 
        
        
        return new_mcq