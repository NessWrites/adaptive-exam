from typing import Union

from sqlalchemy.orm import Session 
from backend.app.models.database_models import (
    Question,
    SubjectiveQuestion,
    CodeQuestion,
    MCQQuestion,
)


class MCQRepository: 
    def __init__(self, db: Session): 
        self.db = db 
        
    
    def get_subjective_questions(self, question_id: int) -> SubjectiveQuestion: 
        """fetch the original subjective question by id"""
        return self.db.query(SubjectiveQuestion).filter(SubjectiveQuestion.id == question_id).first()

    def get_code_question(self, question_id: int) -> CodeQuestion:
        """Fetch a code question by id."""
        return self.db.query(CodeQuestion).filter(CodeQuestion.id == question_id).first()

    def get_any_source_question(self, question_id: int) -> Union[SubjectiveQuestion, CodeQuestion, None]:
        """
        Fetch a source question (subjective OR code) by its base-table unique_id.
        Returns the polymorphic child instance so all child columns are available.
        """
        q = self.db.query(Question).filter(Question.unique_id == question_id).first()
        if q is None:
            return None
        if q.question_type == "subjective":
            return self.db.query(SubjectiveQuestion).filter(SubjectiveQuestion.id == question_id).first()
        if q.question_type == "code":
            return self.db.query(CodeQuestion).filter(CodeQuestion.id == question_id).first()
        return None

    def save_mcq(
        self,
        source_question: Union[SubjectiveQuestion, CodeQuestion],
        mcq_data: dict,
        target_bloom_level: int,
    ) -> MCQQuestion: 
        
        """
        Persist an assembled MCQ to mcq_questions_converted.

        Works for BOTH subjective and code source questions.
        The correct foreign-key (derived_from_subjective_id or derived_from_code_id)
        is set automatically based on the source's question_type.

        Expected mcq_data shape (post DistractorBridge):
          {
            "question_text": str,
            "options":         {"A": str, "B": str, "C": str, "D": str},
            "correct_answer":  {"key": str, "text": str},
            "explanation":     str,
          }
        """
        required_keys = {"question_text", "options", "correct_answer", "explanation"}
        missing = required_keys - mcq_data.keys()
        if missing:
            raise ValueError(
                f"save_mcq called with incomplete mcq_data. Missing keys: {missing}"
            )

        # Determine which FK to populate
        derived_sub_id = source_question.id if source_question.question_type == "subjective" else None
        derived_code_id = source_question.id if source_question.question_type == "code" else None

        new_mcq = MCQQuestion(
            domain = source_question.domain,
            concept_tag = source_question.concept_tag,
            question_text = mcq_data["question_text"],
            options = mcq_data["options"],
            correct_answer = mcq_data['correct_answer'],
            explanation = mcq_data["explanation"],
            validation_score = mcq_data.get("validation_score"),
            mcq_category = mcq_data.get("mcq_category", "text"),
            stem_code = mcq_data.get("stem_code"),
            question_type = "mcq",
            a_values  = [0.0, 0.0],
            b_value = 0.0,
            calibration_status = "pretest",
            
            bloom_level = target_bloom_level, 
            derived_from_subjective_id = derived_sub_id,
            derived_from_code_id = derived_code_id,
        )
        
        self.db.add(new_mcq)
        self.db.commit()
        self.db.refresh(new_mcq)
        return new_mcq 
    