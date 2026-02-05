"""
Updated ExamService with QPool Integration
Supports paraphrasing, scenario generation, and distractor generation on-the-fly
"""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import random
from datetime import datetime

from backend.app.models.database_models import Question, ExamSession, Response
from backend.app.services.irt_engine import IRTEngine
from backend.app.services.qpool_services import QPoolService
from backend.app.core.config import get_settings

settings = get_settings()


class ExamService:
    """Business logic for adaptive examination with pretest items and QPool integration"""
    
    # EXAM CONFIGURATION
    TOTAL_QUESTIONS = 50          # Total questions in exam
    OPERATIONAL_QUESTIONS = 40    # Scored questions (adaptive)
    PRETEST_QUESTIONS = 10        # Unscored questions (random)
    
    # QPOOL CONFIGURATION
    # USE_QPOOL = True              # Enable/disable QPool paraphrasing
    USE_QPOOL = False            # Enable/disable QPool paraphrasing
    QPOOL_PROBABILITY = 0.5       # Probability of using QPool (0.5 = 50% of tech questions)
    QPOOL_TECH_ONLY = True        # Only apply QPool to tech questions (not math)
    
    # TRANSFORMATION CONFIGURATION
    TRANSFORMATION_WEIGHTS = {
        "paraphrase": 0.5,        # 50% paraphrase
        "scenario": 0.5           # 50% scenario
    }
    
    SCENARIO_DOMAINS = [
        "education",
        "healthcare",
        "finance"
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.irt = IRTEngine()
        self.qpool = QPoolService()  # Initialize QPool service
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def create_session(self, user_id: Optional[str] = None, n_questions: int = 50) -> ExamSession:
        """Create a new exam session"""
        session = ExamSession(
            user_id=user_id,
            n_questions=n_questions,
            status="in_progress",
            current_question_num=0,
            theta_math=0.0,
            theta_tech=0.0,
            theta_se_math=1.0,
            theta_se_tech=1.0,
            math_count=0,
            tech_count=0
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_session(self, session_id: int) -> Optional[ExamSession]:
        """Get exam session by ID"""
        return self.db.query(ExamSession).filter(
            ExamSession.session_id == session_id
        ).first()
    
    # ========================================================================
    # QPOOL INTEGRATION 
    # ========================================================================
    
    def _should_paraphrase(self, question: Question) -> bool:
        """
        Decide whether to use QPool transformation for this question
        
        RULE: Only transform TECH questions with 50% probability
        Math questions are NEVER transformed
        
        Returns:
            bool: True if should use QPool, False otherwise
        """
        if not self.USE_QPOOL:
            return False
        
        
        if self.QPOOL_TECH_ONLY and question.domain != 'tech':
            return False
        
        return random.random() < self.QPOOL_PROBABILITY
    
    def _select_transformation_type(self) -> str:
        """
        Randomly select transformation type based on configured weights
        
        Returns:
            str: "paraphrase" or "scenario"
        """
        transformations = list(self.TRANSFORMATION_WEIGHTS.keys())
        weights = list(self.TRANSFORMATION_WEIGHTS.values())
        
        selected = random.choices(transformations, weights=weights, k=1)[0]
        return selected
    
    def _select_scenario_domains(self, num_domains: int = 1) -> List[str]:
        """
        Randomly select scenario domains from available domains
        
        Args:
            num_domains: Number of domains to select
        
        Returns:
            List[str]: Selected scenario domains
        """
        return random.sample(self.SCENARIO_DOMAINS, min(num_domains, len(self.SCENARIO_DOMAINS)))
    
    def _transform_question(self, question: Question) -> Question:
        """
        Transform a question using QPool API (paraphrase OR scenario)
        
        Args:
            question: Original question from database
        
        Returns:
            Question: Modified question object with transformed content
                     (NOT saved to database, just modified in memory)
        """
        
        try:
            # Prepare concept tags
            concept_tags = [question.concept_tag] if question.concept_tag else []
            
            # Map difficulty from IRT b_value
            difficulty = self._map_difficulty(question.b_value)
            
            # Select transformation type
            transformation_type = self._select_transformation_type()
            
            # Prepare transformation-specific parameters
            if transformation_type == "scenario":
                # Select random scenario domains
                scenario_domains = self._select_scenario_domains(num_domains=1)
                transformations = ["scenario"]
                print(f"[QPOOL] Generating SCENARIO for Q{question.unique_id} (domain: {scenario_domains[0]})...")
            else:
                # Paraphrase
                scenario_domains = None
                transformations = ["paraphrase"]
                print(f"[QPOOL] PARAPHRASING Q{question.unique_id}...")
            
            # Call QPool API
            result = self.qpool.paraphrase_question_sync(
                question_id=f"Q_{question.unique_id}",
                base_stem=question.question_text,
                base_answer=question.correct_answer,
                difficulty=difficulty,
                concept_tags=concept_tags,
                transformations=transformations,
                scenario_domains=scenario_domains,
                variants=1,  # Generate 1 variant
                generate_distractors=True
            )
            
            # Parse QPool response
            variants = result.get('variants', [])
            
            if not variants:
                print(f"[QPOOL] ✗ No variants returned, using original")
                return question
            
            # Select first variant (or random if multiple)
            selected_variant = variants[0] if len(variants) == 1 else random.choice(variants)
            
            # Extract transformed content
            transformed_stem = selected_variant.get('variant_stem') or selected_variant.get('stem', question.question_text)
            transformed_answer = selected_variant.get('answer', question.correct_answer)
            distractors = selected_variant.get('distractors', [])
            lineage = selected_variant.get('lineage', {})
            
            # Log transformation details
            if lineage:
                print(f"[QPOOL] Lineage: {lineage}")
            
            # Build new options: correct answer + distractors
            if distractors:
                # Get the original correct answer index
                original_correct = question.correct_answer
                original_index = self._get_correct_answer_index(original_correct, question.options)
                
                print(f"[QPOOL] Original correct answer at index: {original_index}")
                
                # Shuffle distractors
                shuffled_distractors = distractors.copy()
                random.shuffle(shuffled_distractors)
                
                # Build options with correct answer at SAME position
                total_options_needed = len(distractors) + 1  # distractors + correct answer
                transformed_options = []
                distractor_idx = 0
                
                for i in range(total_options_needed):
                    if i == original_index:
                        # Put correct answer at its original position
                        transformed_options.append(transformed_answer)
                    else:
                        # Put shuffled distractor
                        if distractor_idx < len(shuffled_distractors):
                            transformed_options.append(shuffled_distractors[distractor_idx])
                            distractor_idx += 1
                
                # Keep correct_answer unchanged - it still points to the same index
                final_correct_answer = question.correct_answer
                
                print(f"[QPOOL] Kept correct answer at original position {original_index}")
                print(f"[QPOOL] Shuffled {len(shuffled_distractors)} distractors into other positions")
            else:
                # No distractors provided, use original options
                transformed_options = question.options
                final_correct_answer = question.correct_answer
            
            # Create a modified copy of the question (in-memory only)
            modified_question = Question(
                unique_id=question.unique_id,
                domain=question.domain,
                concept_tag=question.concept_tag,
                question_text=transformed_stem,      # Transformed text
                options=transformed_options,          # New options with distractors
                correct_answer=final_correct_answer,  # Index unchanged
                image_url=question.image_url,
                question_type=question.question_type,
                a_values=question.a_values,          # Keep IRT parameters
                b_value=question.b_value,            # Keep IRT parameters
                calibration_status=question.calibration_status
            )
            
            # Debug logging
            print(f"[QPOOL] ✓ Successfully transformed Q{question.unique_id} ({transformation_type.upper()})")
            print(f"[QPOOL]   Original: {question.question_text[:80]}...")
            print(f"[QPOOL]   Transformed: {transformed_stem[:80]}...")
            print(f"[QPOOL]   Options: {transformed_options}")
            
            return modified_question
            
        except Exception as e:
            # If QPool fails, fall back to original question
            print(f"[QPOOL] ✗ Failed to transform Q{question.unique_id}: {str(e)}")
            print(f"[QPOOL] Falling back to original question")
            return question
    
    def _get_correct_answer_index(self, correct_answer, options: List[str]) -> int:
        """
        Determine the index of the correct answer
        
        Args:
            correct_answer: The correct answer (can be index, letter, or text)
            options: List of answer options
        
        Returns:
            int: Index of the correct answer
        """
        if isinstance(correct_answer, int):
            # Direct index
            return correct_answer
        elif isinstance(correct_answer, str) and len(correct_answer) == 1:
            # Letter like "A", "B", "C"
            return ord(correct_answer.upper()) - ord('A')
        elif isinstance(correct_answer, str):
            # Text - find it in original options
            try:
                return options.index(correct_answer)
            except ValueError:
                # Can't find it, default to 0
                print(f"[QPOOL]   Could not find original answer in options, defaulting to index 0")
                return 0
        elif isinstance(correct_answer, list):
            # List format - use first element
            if correct_answer and isinstance(correct_answer[0], str) and len(correct_answer[0]) == 1:
                return ord(correct_answer[0].upper()) - ord('A')
            else:
                return 0
        else:
            return 0
    
    def _map_difficulty(self, b_value: float) -> str:
        """
        Map IRT b-value to difficulty string for QPool
        
        Args:
            b_value: IRT difficulty parameter
        
        Returns:
            str: "easy", "medium", or "hard"
        """
        if b_value < -0.5:
            return "easy"
        elif b_value < 0.5:
            return "medium"
        else:
            return "hard"
    
    # ========================================================================
    # ITEM SELECTION 
    # ========================================================================
    
    def select_next_question(self, session_id: int) -> Optional[Question]:
        """
        Select next question - either operational (adaptive) or pretest (random).
        Optionally transform using QPool (paraphrase or scenario).
        
        LOGIC:
        1. Count how many pretest items already given
        2. Decide if this position should be pretest
        3. Select either pretest or operational item
        4. Optionally transform using QPool (paraphrase OR scenario)
        """
        
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Count pretest items already administered
        pretest_count = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Question.calibration_status == 'pretest'
        ).count()
        
        # Decide if this should be a pretest item
        should_be_pretest = self._should_insert_pretest(
            session.current_question_num,
            pretest_count
        )
        
        # Select base question
        if should_be_pretest:
            print(f"[PRETEST] Position {session.current_question_num + 1}/50")
            base_question = self._select_pretest_item(session_id)
        else:
            print(f"[OPERATIONAL] Position {session.current_question_num + 1}/50")
            base_question = self._select_operational_item(session_id)
        
        # Decide whether to transform
        if self._should_paraphrase(base_question):
            return self._transform_question(base_question)
        else:
            print(f"[QPOOL] Skipping transformation for Q{base_question.unique_id}")
            return base_question
    
    def _should_insert_pretest(self, current_q_num: int, pretest_given: int) -> bool:
        """
        Decide if current position should be a pretest item.
        
        STRATEGY: Random insertion throughout exam
        - Need to give 10 pretest out of 50 total
        - Ensure we get all 10 by end
        - Don't put in first 3 questions (build theta first)
        """
        
        # Already gave all 10 pretest items?
        if pretest_given >= self.PRETEST_QUESTIONS:
            return False
        
        # Don't give pretest in first 3 questions (need to build initial theta)
        if current_q_num < 3:
            return False
        
        # Calculate probability
        remaining_questions = self.TOTAL_QUESTIONS - current_q_num
        remaining_pretest = self.PRETEST_QUESTIONS - pretest_given
        
        if remaining_pretest <= 0:
            return False
        
        # Force pretest if running out of space
        if remaining_pretest >= remaining_questions:
            return True
        
        # Random insertion with adaptive probability
        probability = remaining_pretest / remaining_questions
        return random.random() < probability
    
    def _select_pretest_item(self, session_id: int) -> Question:
        """
        Select a PRETEST item (not scored, random selection).
        
        CRITERIA:
        1. calibration_status = 'pretest'
        2. Not already used in this session
        3. Random selection (NOT adaptive)
        """
        
        # Get already used items
        used_ids = self._get_administered_items(session_id)
        
        # Query pretest items
        query = self.db.query(Question).filter(
            Question.calibration_status == 'pretest'
        )
        
        if used_ids:
            query = query.filter(~Question.unique_id.in_(used_ids))
        
        candidates = query.all()
        
        if not candidates:
            print("[WARNING] No pretest items available, falling back to operational")
            return self._select_operational_item(session_id)
        
        # RANDOM selection (not adaptive!)
        selected = random.choice(candidates)
        print(f"  → Selected pretest Q{selected.unique_id} ({selected.concept_tag})")
        
        return selected
    
    def _select_operational_item(self, session_id: int) -> Question:
        """
        Select an OPERATIONAL item (scored, adaptive selection).
        
        CRITERIA:
        1. calibration_status = 'operational'
        2. Not already used in this session
        3. Maximum Fisher Information (adaptive)
        4. Content balancing (50/50 math/tech)
        """
        
        session = self.get_session(session_id)
        used_ids = self._get_administered_items(session_id)
        
        # Query OPERATIONAL items only
        query = self.db.query(Question).filter(
            Question.calibration_status == 'operational'
        )
        
        if used_ids:
            query = query.filter(~Question.unique_id.in_(used_ids))
        
        # Content balancing (for operational items only)
        target_math = self.OPERATIONAL_QUESTIONS // 2  # 20
        target_tech = self.OPERATIONAL_QUESTIONS // 2  # 20
        
        # Count OPERATIONAL items given so far
        operational_count = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Question.calibration_status == 'operational'
        ).count()
        
        remaining_operational = self.OPERATIONAL_QUESTIONS - operational_count
        math_needed = target_math - session.math_count
        tech_needed = target_tech - session.tech_count
        
        # Apply domain constraint if needed
        if tech_needed > 0 and math_needed == 0:
            query = query.filter(Question.domain == 'tech')
        elif math_needed > 0 and tech_needed == 0:
            query = query.filter(Question.domain == 'math')
        
        candidates = query.all()
        
        if not candidates:
            raise ValueError("No operational items available for selection")
        
        # Select by maximum Fisher Information (adaptive)
        theta = np.array([session.theta_math, session.theta_tech])
        
        best_item = None
        max_info = -float('inf')
        
        for item in candidates:
            info = self.irt.fisher_information_matrix(theta, item.a_values, item.b_value)
            if info > max_info:
                max_info = info
                best_item = item
        
        print(f"  → Selected operational Q{best_item.unique_id} ({best_item.concept_tag}), Info={max_info:.3f}")
        
        return best_item
    
    # ========================================================================
    # THETA UPDATE 
    # ========================================================================
    
    def update_theta(self, session_id: int):
        """
        Update ability estimates using EAP.
        
        CRITICAL: Only use OPERATIONAL items for scoring!
        Pretest items are completely ignored in theta calculation.
        """
        
        session = self.get_session(session_id)
        
        # Get responses for OPERATIONAL items ONLY
        responses = self.db.query(Response, Question).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Response.is_correct.isnot(None),
            Question.calibration_status == 'operational'
        ).all()
        
        if not responses:
            print(f"[THETA] No operational responses yet")
            return
        
        # Extract response pattern and item parameters
        response_pattern = [r.is_correct for r, q in responses]
        items = [
            {'a_values': q.a_values, 'b_value': q.b_value}
            for r, q in responses
        ]
        
        # Calculate theta using ONLY operational items
        theta, theta_se = self.irt.update_theta_eap(response_pattern, items)
        
        # Update session
        session.theta_math = float(theta[0])
        session.theta_tech = float(theta[1])
        session.theta_se_math = float(theta_se[0])
        session.theta_se_tech = float(theta_se[1])
        
        self.db.commit()
        
        print(f"[THETA] Updated using {len(responses)} operational items: "
              f"θ_math={theta[0]:.2f}, θ_tech={theta[1]:.2f}")
    
    # ========================================================================
    # ANSWER PROCESSING 
    # ========================================================================
    
    def submit_answer(self, session_id: int, question_id: int, user_answer) -> Dict:
        """
        Submit answer and get feedback.
        Works for both operational and pretest items.
        """
        
        session = self.get_session(session_id)
        question = self.db.query(Question).get(question_id)
        
        # Check answer
        is_correct = self.irt.check_answer(user_answer, question.correct_answer, question.options)
        
        # Find the response record
        response = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.question_id == question_id
        ).first()
        
        if response:
            # Update existing response
            response.user_answer = user_answer
            response.is_correct = is_correct
        else:
            # Create new response
            response = Response(
                session_id=session_id,
                question_id=question_id,
                question_num=session.current_question_num + 1,
                user_answer=user_answer,
                is_correct=1 if is_correct else 0
            )
            self.db.add(response)
        
        # Update theta (ONLY if operational item)
        if question.calibration_status == 'operational':
            self.update_theta(session_id)
            
            # Update domain count
            if question.domain == 'math':
                session.math_count += 1
            else:
                session.tech_count += 1
        else:
            print(f"[PRETEST] Q{question_id} not used for scoring")
        
        # Save theta snapshot
        response.theta_math_after = session.theta_math
        response.theta_tech_after = session.theta_tech
        
        # Update progress
        session.current_question_num += 1
        
        self.db.commit()
        
        return {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'question_num': session.current_question_num
        }
    
    # ========================================================================
    # RESULTS 
    # ========================================================================
    
    def get_results(self, session_id: int) -> Dict:
        """Calculate final results"""
        
        session = self.get_session(session_id)
        
        # Count correct operational items
        operational_correct = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Response.is_correct == True,
            Question.calibration_status == 'operational'
        ).count()
        
        # Total operational items answered
        operational_total = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Question.calibration_status == 'operational'
        ).count()
        
        # Count correct answers across ALL questions
        total_correct = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct == True
        ).count()
        
        # Total questions answered
        total_questions = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct.isnot(None)
        ).count()
        
        # Overall accuracy
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'session_id': session_id,
            'total_questions': total_questions,
            'correct_answers': total_correct,
            'accuracy': overall_accuracy,
            'operational_questions': operational_total,
            'operational_correct': operational_correct,
            'math_ability': {
                'value': session.theta_math,
                'standard_error': session.theta_se_math,
                'interpretation': self._interpret_theta(session.theta_math)
            },
            'tech_ability': {
                'value': session.theta_tech,
                'standard_error': session.theta_se_tech,
                'interpretation': self._interpret_theta(session.theta_tech)
            },
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        }
    
    # ========================================================================
    # HELPER METHODS 
    # ========================================================================
    
    def _get_administered_items(self, session_id: int) -> List[int]:
        """Get list of question IDs already used in this session"""
        return [
            r.question_id for r in 
            self.db.query(Response.question_id).filter(
                Response.session_id == session_id
            ).all()
        ]
    
    def _interpret_theta(self, theta: float) -> str:
        """Convert theta value to human-readable interpretation"""
        if theta > 1.5:
            return "Exceptional"
        elif theta > 0.5:
            return "Above Average"
        elif theta > -0.5:
            return "Average"
        elif theta > -1.5:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    # ========================================================================
    # COMPLETE EXAM WORKFLOW 
    # ========================================================================
    
    def start_exam_with_first_question(self, user_id: Optional[str] = None, n_questions: int = 50):
        """Start exam and return session + first question"""
        
        # Create session
        session = self.create_session(user_id, n_questions)
        
        # Select first question (may be transformed by QPool)
        first_question = self.select_next_question(session.session_id)
        
        if not first_question:
            raise ValueError("No questions available")
        
        # Record that this question was served
        response = Response(
            session_id=session.session_id,
            question_id=first_question.unique_id,
            question_num=1,
            is_correct=None
        )
        self.db.add(response)
        self.db.commit()
        
        return {
            'session': session,
            'question': first_question
        }
    
    def submit_answer_and_get_next(self, session_id: int, user_answer):
        """Submit answer and get next question or completion status"""
        
        session = self.get_session(session_id)
        
        # Get current unanswered question
        current_response = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct.is_(None)
        ).order_by(Response.response_id.desc()).first()
        
        if not current_response:
            raise ValueError("No unanswered question found")
        
        # Submit answer
        feedback = self.submit_answer(session_id, current_response.question_id, user_answer)
        
        # Check if exam complete
        if session.current_question_num >= session.n_questions:
            session.status = 'completed'
            session.completed_at = datetime.now()
            self.db.commit()
            
            return {
                'feedback': feedback,
                'next_question': None,
                'exam_completed': True
            }
        
        # Get next question (may be transformed by QPool)
        next_question = self.select_next_question(session_id)
        
        if next_question:
            # Record next question
            next_response = Response(
                session_id=session_id,
                question_id=next_question.unique_id,
                question_num=session.current_question_num + 1,
                is_correct=None
            )
            self.db.add(next_response)
            self.db.commit()
        
        return {
            'feedback': feedback,
            'next_question': next_question,
            'exam_completed': False
        }