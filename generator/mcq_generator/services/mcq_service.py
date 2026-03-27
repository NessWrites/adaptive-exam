#connect the repository to the ai engine
import random 

from typing import List, Optional
from sqlalchemy.orm import Session 
from generator.mcq_generator.db.repository import MCQRepository 
from generator.mcq_generator.core.ai_engine import MCQEngine 
from generator.mcq_generator.core.mcq_evaluator import MCQEvaluator
from generator.mcq_generator.services.distractor_bridge import DistractorBridge


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

# class MCQService: 
#     def __init__(self, db: Session): 
#         self.repo = MCQRepository(db)
#         self.ai_engine = MCQEngine()
        
    
#     async def convert_subjective_to_mcq(self, question_id: int, num_variants: int = 1, target_levels: Optional[List[int]] = None):
        
#         #fetch subjective question 
#         subjective_q = self.repo.get_subjective_questions(question_id)
        
#         if not subjective_q: 
#             raise ValueError(f"Subjective Question with id {question_id} not found")
        
#         #handle bloom level logic 
#         #user provides levels , otherwise pick "num_variants" unique random levels from [1,2,3,4]
#         VALID_BLOOM_LEVELS = {1,2,3,4}
        
#         if target_levels: 
#             seen = set() 
#             cleaned = []
#             invalid = []
            
#             for lvl in target_levels: 
#                 if lvl not in VALID_BLOOM_LEVELS: 
#                     invalid.append(lvl) 
#                 elif lvl not in seen: 
#                     seen.add(lvl)
#                     cleaned.append(lvl)
                    
#             if invalid: 
#                 raise ValueError(f" Invalid Bloom levels: {invalid}. Must be integers in [1,2,3,4].")
        
#             resolved_levels = cleaned 
            
#         else: 
#             count = min(num_variants, len(VALID_BLOOM_LEVELS))
#             resolved_levels = random.sample(sorted(VALID_BLOOM_LEVELS), count)
        
#     # resolved_levels is now guaranteed:
#     #   - no duplicates
#     #   - all values in {1, 2, 3, 4}
#     #   - length between 1 and 4
            
#         mark_scheme_str = str(subjective_q.mark_schema) if subjective_q.mark_schema else "No marking scheme provided"
#         # print("DEBUG: ABOUT TO CALL AI ENGINE",f"sending marking scheme to AI engine for qid {question_id}:{mark_scheme_str}") 
#         logger.info(f"sending marking scheme to AI engine for qid {question_id}:{mark_scheme_str}")
#             #single api call for the batch generation 
            
#         batch_results = await self.ai_engine.generate_mcq_batch(
#             domain= subjective_q.domain,
#             concept_tag= subjective_q.concept_tag,
#             question_text= subjective_q.question_text,
#             levels= resolved_levels,
#             mark_scheme= mark_scheme_str
#         )
        
        
#         results = []
        
#         #loop through the ai's generated batch and save each one using the repository code 
        
#         for mcq_item in batch_results.questions: 
            
#             #convert pydantic model to a dict 
#             mcq_dict = mcq_item.model_dump() 
            
#             new_mcq = self.repo.save_mcq(
#                 original_sub_q=subjective_q, 
#                 mcq_data = mcq_dict,
#                 target_bloom_level= mcq_item.bloom_level
#             )
            
#             results.append(new_mcq) 
            
        
#         return results 


class MCQService:
    def __init__(self, db: Session, distractor_bridge: DistractorBridge):
        """
        Args:
            db:                 SQLAlchemy session (injected by FastAPI).
            distractor_bridge:  DistractorBridge instance (injected by FastAPI).
                                Injecting it (rather than constructing inside)
                                allows easy mocking in tests.
        """
        self.repo = MCQRepository(db)
        self.ai_engine = MCQEngine()
        self.evaluator = MCQEvaluator()
        self.distractor_bridge = distractor_bridge

    # ------------------------------------------------------------------ #
    # UNIFIED ENTRY POINT                                                  #
    # ------------------------------------------------------------------ #

    async def convert_to_mcq(
        self,
        question_id: int,
        num_variants: int = 1,
        target_levels: Optional[List[int]] = None,
    ) -> list:
        """
        Auto-detect source question type (subjective / code) and convert to MCQ.
        """
        # --- 1. Fetch source question (any type) ---
        source_q = self.repo.get_any_source_question(question_id)
        if not source_q:
            raise ValueError(
                f"Question with id {question_id} not found "
                f"(must be 'subjective' or 'code' type)."
            )

        # --- 2. Determine Bloom levels ---
        if not target_levels:
            count = min(num_variants, 4)
            target_levels = random.sample([1, 2, 3, 4], count)

        # --- 3. Branch on question type for LLM call ---
        if source_q.question_type == "subjective":
            batch_result = await self._generate_from_subjective(source_q, target_levels)
            # For the evaluator: use mark_schema as the reference context
            evaluator_context = (
                str(source_q.mark_schema)
                if source_q.mark_schema
                else "Not provided"
            )
        elif source_q.question_type == "code":
            batch_result = await self._generate_from_code(source_q, target_levels)
            # For the evaluator: use test cases as the reference context
            evaluator_context = str(source_q.markscheme) if source_q.markscheme else "Not provided"
        else:
            raise ValueError(
                f"Unsupported question_type '{source_q.question_type}' for MCQ conversion."
            )

        # --- 4. For each LLM core, run Distractors → Evaluate → Save ---
        results = []
        for mcq_core in batch_result.questions:
            try:
                options_dict, correct_answer_dict = (
                    await self.distractor_bridge.build_options_dict(
                        stem=mcq_core.question_text,
                        correct_answer=mcq_core.correct_answer,
                        concept_tag=source_q.concept_tag,
                        domain=source_q.domain,
                    )
                )
            except Exception as exc:
                logger.error(
                    "DistractorBridge failed for bloom level %d: %s",
                    mcq_core.bloom_level,
                    exc,
                    exc_info=True,
                )
                continue

            # --- 5. Evaluate the generated MCQ ---
            distractors_list = [v for k, v in options_dict.items() if k != correct_answer_dict["key"]]
            eval_score = await self.evaluator.evaluate_mcq(
                question_text=source_q.question_text,
                mark_scheme=evaluator_context,
                bloom_level=mcq_core.bloom_level,
                mcq_stem=mcq_core.question_text,
                correct_answer=correct_answer_dict["text"],
                distractors=distractors_list,
                explanation=mcq_core.explanation
            )

            # --- 6. Assemble the final dict for the repository ---
            mcq_data = {
                "question_text": mcq_core.question_text,
                "options": options_dict,
                "correct_answer": correct_answer_dict,
                "explanation": mcq_core.explanation,
                "validation_score": eval_score,
            }

            new_mcq = self.repo.save_mcq(
                source_question=source_q,
                mcq_data=mcq_data,
                target_bloom_level=mcq_core.bloom_level,
            )
            results.append(new_mcq)

        if not results:
            raise RuntimeError(
                f"MCQ conversion for question {question_id} produced zero saved records. "
                "Check DistractorBridge logs."
            )

        return results

    # ------------------------------------------------------------------ #
    # BACKWARD-COMPATIBLE ALIAS                                            #
    # ------------------------------------------------------------------ #

    async def convert_subjective_to_mcq(
        self,
        question_id: int,
        num_variants: int = 1,
        target_levels: Optional[List[int]] = None,
    ) -> list:
        """Legacy method — delegates to the unified convert_to_mcq."""
        return await self.convert_to_mcq(question_id, num_variants, target_levels)

    # ------------------------------------------------------------------ #
    # PRIVATE: TYPE-SPECIFIC LLM CALLS                                     #
    # ------------------------------------------------------------------ #

    async def _generate_from_subjective(self, source_q, target_levels):
        """Call the subjective-specific LLM prompt."""
        mark_scheme_str = (
            str(source_q.mark_schema) if source_q.mark_schema else "Not provided"
        )
        return await self.ai_engine.generate_mcq_batch(
            domain=source_q.domain,
            concept_tag=source_q.concept_tag,
            question_text=source_q.question_text,
            levels=target_levels,
            mark_scheme=mark_scheme_str,
        )

    async def _generate_from_code(self, source_q, target_levels):
        """Call the code-specific LLM prompt, serializing code question fields."""
        import json

        # Serialize test cases for the prompt (hide hidden flag from LLM, show I/O)
        test_cases_raw = source_q.markscheme or []
        test_cases_str = json.dumps(test_cases_raw, indent=2)

        configurations_str = json.dumps(source_q.configurations or {}, indent=2)

        return await self.ai_engine.generate_mcq_batch_from_code(
            domain=source_q.domain,
            concept_tag=source_q.concept_tag,
            question_text=source_q.question_text,
            function_name=source_q.function_name,
            placeholder=source_q.placeholder or "",
            test_cases=test_cases_str,
            configurations=configurations_str,
            levels=target_levels,
        )