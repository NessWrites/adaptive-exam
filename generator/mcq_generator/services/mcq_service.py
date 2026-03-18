#connect the repository to the ai engine
import random 
from typing import List, Optional
from sqlalchemy.orm import Session 
from generator.mcq_generator.db.repository import MCQRepository 
from generator.mcq_generator.core.ai_engine import MCQEngine 

# class MCQService: 
#     def __init__(self, db: Session): 
#         self.repo = MCQRepository(db)
#         self.ai_engine = MCQEngine() 
        
#     async def convert_subjective_to_mcq(self, question_id: int, num_variants: int =1, target_levels: list[int]): 
#         #fetch subjective question 
#         subjective_q = self.repo.get_subjective_questions(question_id)
#         if not subjective_q: 
#             raise ValueError(f"SubjectiveQuestion with id {question_id} not found.")
        
#         #extracting marking scheme (handle cases where it might be empty or NOne)
#         mark_scheme_str = str(subjective_q.mark_schema) if subjective_q.mark_schema else "No marking scheme provided"
#         #run ai conversion 
        
#         results = []
        
#         for _ in range(num_variants):
#             mcq_result = await self.ai_engine.generate_mcq(
#                 domain=subjective_q.domain,
#                 concept_tag = subjective_q.concept_tag,
#                 question_text = subjective_q.question_text,
#                 bloom_level= int()
#             )
        
#         #3 save to db 
#         mcq_dict = mcq_result.model_dump() 
#         new_mcq = self.repo.save_mcq(subjective_q, mcq_dict) 
        
        
#         return new_mcq

class MCQService: 
    def __init__(self, db: Session): 
        self.repo = MCQRepository(db)
        self.ai_engine = MCQEngine()
        
    
    async def convert_subjective_to_mcq(self, question_id: int, num_variants: int = 1, target_levels: Optional[List[int]] = None):
        
        #fetch subjective question 
        subjective_q = self.repo.get_subjective_questions(question_id)
        
        if not subjective_q: 
            raise ValueError(f"Subjective Question with id {question_id} not found")
        
        #handle bloom level logic 
        #user provides levels , otherwise pick "num_variants" unique random levels from [1,2,3,4]
        
        if not target_levels: 
            available_levels = [1,2,3,4]
            
            count = min(num_variants,4) 
            target_levels = random.sample(available_levels, count) 
            
        mark_scheme_str = str(subjective_q.mark_schema) if subjective_q.mark_schema else "No marking scheme provided"
            
            #single api call for the batch generation 
            
        batch_results = await self.ai_engine.generate_mcq_batch(
            domain= subjective_q.domain,
            concept_tag= subjective_q.concept_tag,
            question_text= subjective_q.question_text,
            levels= target_levels,
            mark_scheme= mark_scheme_str
        )
        
        
        results = []
        
        #loop through the ai's generated batch and save each one using the repository code 
        
        for mcq_item in batch_results.questions: 
            
            #convert pydantic model to a dict 
            mcq_dict = mcq_item.model_dump() 
            
            new_mcq = self.repo.save_mcq(
                original_sub_q=subjective_q, 
                mcq_data = mcq_dict,
                target_bloom_level= mcq_item.bloom_level
            )
            
            results.append(new_mcq) 
            
        
        return results 
