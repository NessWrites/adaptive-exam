#connect the repository to the ai engine
import random 
from typing import List, Optional
from sqlalchemy.orm import Session 
from generator.mcq_generator.db.repository import MCQRepository 
from generator.mcq_generator.core.ai_engine import MCQEngine 


import logging 

# logger = logging.getLogger(__name__)

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)
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
        VALID_BLOOM_LEVELS = {1,2,3,4}
        
        if target_levels: 
            seen = set() 
            cleaned = []
            invalid = []
            
            for lvl in target_levels: 
                if lvl not in VALID_BLOOM_LEVELS: 
                    invalid.append(lvl) 
                elif lvl not in seen: 
                    seen.add(lvl)
                    cleaned.append(lvl)
                    
            if invalid: 
                raise ValueError(f" Invalid Bloom levels: {invalid}. Must be integers in [1,2,3,4].")
        
            resolved_levels = cleaned 
            
        else: 
            count = min(num_variants, len(VALID_BLOOM_LEVELS))
            resolved_levels = random.sample(sorted(VALID_BLOOM_LEVELS), count)
        
    # resolved_levels is now guaranteed:
    #   - no duplicates
    #   - all values in {1, 2, 3, 4}
    #   - length between 1 and 4
            
        mark_scheme_str = str(subjective_q.mark_schema) if subjective_q.mark_schema else "No marking scheme provided"
        # print("DEBUG: ABOUT TO CALL AI ENGINE",f"sending marking scheme to AI engine for qid {question_id}:{mark_scheme_str}") 
        logger.info(f"sending marking scheme to AI engine for qid {question_id}:{mark_scheme_str}")
            #single api call for the batch generation 
            
        batch_results = await self.ai_engine.generate_mcq_batch(
            domain= subjective_q.domain,
            concept_tag= subjective_q.concept_tag,
            question_text= subjective_q.question_text,
            levels= resolved_levels,
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
