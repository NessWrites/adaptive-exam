"""
Updated ExamService with QPool Integration and Response Placeholder Fix
Supports paraphrasing, scenario generation, and distractor generation on-the-fly
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from backend.app.models.database_models import ExamSession, Question, Response
from backend.app.services.irt_engine import IRTEngine
from backend.app.services.qpool_services import QPoolService
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import random
import numpy as np 

logger = logging.getLogger(__name__)


class ExamService:
    """Business logic for adaptive examination with pretest items and QPool integration"""
    
    # =========================================================================
    # EXAM CONFIGURATION
    # =========================================================================
    TOTAL_QUESTIONS = 50          # Total questions in exam
    OPERATIONAL_QUESTIONS = 40    # Scored questions (adaptive)
    PRETEST_QUESTIONS = 10        # Unscored questions (random)
    
    # =========================================================================
    # QPOOL CONFIGURATION - TOGGLE ON/OFF
    # =========================================================================
    USE_QPOOL = False             # ⚙️ Set to True to enable QPool transformations
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
        self.irt_engine = IRTEngine()
        self.qpool = QPoolService()  # Initialize QPool service

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def create_session(self, user_id: Optional[str], n_questions: int) -> ExamSession:
        """Create new exam session with proper initialization"""
        session = ExamSession(
            user_id=user_id,
            n_questions=n_questions,
            current_question_num=0,
            status="in_progress",
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
        logger.info(f"Created session {session.session_id}")
        return session

    def get_session(self, session_id: int) -> ExamSession:
        """Retrieve session by ID with validation"""
        session = self.db.query(ExamSession).filter(
            ExamSession.session_id == session_id
        ).first()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    # =========================================================================
    # QUESTION SELECTION WITH QPOOL INTEGRATION
    # =========================================================================
    
    def select_next_question(self, session: ExamSession, question_num: int) -> Question:
        """
        Select next question using Fisher Information.
        Handles both operational and pretest questions.
        Optionally transforms using QPool if USE_QPOOL = True.
        """
        
        # Get already asked question IDs
        asked_ids = [
            r.question_id for r in 
            self.db.query(Response.question_id)
            .filter(Response.session_id == session.session_id)
            .all()
        ]
        
        # Count pretest items already given
        pretest_count = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session.session_id,
            Question.calibration_status == 'pretest'
        ).count()
        
        # Decide if this should be operational or pretest
        should_be_pretest = self._should_insert_pretest(question_num, pretest_count)
        
        # Select base question
        if should_be_pretest:
            logger.info(f"Session {session.session_id} Q{question_num}: PRETEST question")
            base_question = self._select_pretest_item(asked_ids)
        else:
            logger.info(f"Session {session.session_id} Q{question_num}: OPERATIONAL question")
            theta = [session.theta_math, session.theta_tech]
            base_question = self._select_operational_item(asked_ids, theta, session)
        
        if not base_question:
            raise ValueError("No available questions in pool")
        
        # Apply QPool transformation if enabled
        if self.USE_QPOOL and self._should_transform_question(base_question):
            logger.info(f"Applying QPool transformation to Q{base_question.unique_id}")
            return self._transform_question(base_question)
        else:
            return base_question

    def _should_insert_pretest(self, current_q_num: int, pretest_given: int) -> bool:
        """
        Decide if current position should be a pretest item.
        
        STRATEGY: Random insertion throughout exam
        - Need to give 10 pretest out of 50 total
        - Don't put in first 3 questions (build theta first)
        """
        
        # Already gave all 10 pretest items?
        if pretest_given >= self.PRETEST_QUESTIONS:
            return False
        
        # Don't give pretest in first 3 questions
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

    def _select_pretest_item(self, exclude_ids: List[int]) -> Question:
        """Select a PRETEST item (not scored, random selection)"""
        
        query = self.db.query(Question).filter(
            Question.calibration_status == 'pretest'
        )
        
        if exclude_ids:
            query = query.filter(~Question.unique_id.in_(exclude_ids))
        
        candidates = query.all()
        
        if not candidates:
            logger.warning("No pretest items available")
            return None
        
        # Random selection (not adaptive)
        selected = random.choice(candidates)
        logger.debug(f"Selected pretest Q{selected.unique_id}")
        
        return selected

    def _select_operational_item(self, exclude_ids: List[int], theta: List[float], session: ExamSession) -> Question:
        """
        Select an OPERATIONAL item using Fisher Information (adaptive).
        Includes content balancing (50/50 math/tech).
        """
        
        query = self.db.query(Question).filter(
            Question.calibration_status == 'operational'
        )
        
        if exclude_ids:
            query = query.filter(~Question.unique_id.in_(exclude_ids))
        
        candidates = query.all()
        
        if not candidates:
            logger.warning("No operational items available")
            return None
        
        # Apply content balancing
        math_ratio = session.math_count / max(session.current_question_num, 1)
        tech_ratio = session.tech_count / max(session.current_question_num, 1)
        
        # Prefer domain that's behind
        if math_ratio < 0.45:
            domain_candidates = [q for q in candidates if q.domain == 'math']
            if domain_candidates:
                candidates = domain_candidates
        elif tech_ratio < 0.45:
            domain_candidates = [q for q in candidates if q.domain == 'tech']
            if domain_candidates:
                candidates = domain_candidates
        
        # Calculate Fisher Information for each candidate
        best_question = None
        max_info = -1
        
        for question in candidates:
            # FIX: Convert list to numpy array and pass raw values
            info = self.irt_engine.fisher_information_matrix(
                np.array(theta), 
                question.a_values, 
                question.b_value
            )
            if info > max_info:
                max_info = info
                best_question = question
        
        logger.debug(f"Selected operational Q{best_question.unique_id} (Fisher Info: {max_info:.2f})")
        return best_question

    # =========================================================================
    # QPOOL TRANSFORMATION
    # =========================================================================
    
    def _should_transform_question(self, question: Question) -> bool:
        """
        Decide whether to transform this question with QPool.
        
        Rules:
        - If QPOOL_TECH_ONLY = True, only transform tech questions
        - Apply transformation with QPOOL_PROBABILITY chance
        """
        if not self.USE_QPOOL:
            return False
        
        # Tech-only filtering
        if self.QPOOL_TECH_ONLY and question.domain != 'tech':
            return False
        
        # Probabilistic application
        return random.random() < self.QPOOL_PROBABILITY

    def _transform_question(self, question: Question) -> Question:
        """
        Transform a question using QPool (paraphrase OR scenario).
        Falls back to original if transformation fails.
        """
        try:
            # Choose transformation type
            transformation_type = random.choices(
                list(self.TRANSFORMATION_WEIGHTS.keys()),
                weights=list(self.TRANSFORMATION_WEIGHTS.values())
            )[0]
            
            logger.info(f"Transforming Q{question.unique_id} using {transformation_type}")
            
            if transformation_type == "paraphrase":
                result = self.qpool.paraphrase_question(
                    stem=question.question_text,
                    correct_answer=self._get_correct_option_text(question),
                    domain=question.domain,
                    difficulty=self._map_difficulty(question.b_value)
                )
            else:  # scenario
                scenario = random.choice(self.SCENARIO_DOMAINS)
                result = self.qpool.generate_scenario(
                    stem=question.question_text,
                    correct_answer=self._get_correct_option_text(question),
                    scenario=scenario,
                    domain=question.domain,
                    difficulty=self._map_difficulty(question.b_value)
                )
            
            # Extract transformed content
            transformed_stem = result.get('transformed_stem', question.question_text)
            transformed_answer = result.get('transformed_answer', self._get_correct_option_text(question))
            distractors = result.get('distractors', [])
            
            # Build new options maintaining correct answer position
            if distractors:
                original_correct = question.correct_answer
                original_index = self._get_correct_answer_index(original_correct, question.options)
                
                # Shuffle distractors
                shuffled_distractors = distractors.copy()
                random.shuffle(shuffled_distractors)
                
                # Build options with correct answer at same position
                total_options_needed = len(distractors) + 1
                transformed_options = []
                distractor_idx = 0
                
                for i in range(total_options_needed):
                    if i == original_index:
                        transformed_options.append(transformed_answer)
                    else:
                        if distractor_idx < len(shuffled_distractors):
                            transformed_options.append(shuffled_distractors[distractor_idx])
                            distractor_idx += 1
                
                final_correct_answer = question.correct_answer
            else:
                transformed_options = question.options
                final_correct_answer = question.correct_answer
            
            # Create modified question (in-memory only, IRT parameters preserved)
            modified_question = Question(
                unique_id=question.unique_id,
                domain=question.domain,
                concept_tag=question.concept_tag,
                question_text=transformed_stem,
                options=transformed_options,
                correct_answer=final_correct_answer,
                image_url=question.image_url,
                question_type=question.question_type,
                a_values=question.a_values,  # Keep IRT parameters
                b_value=question.b_value,    # Keep IRT parameters
                calibration_status=question.calibration_status
            )
            
            logger.info(f"✓ Successfully transformed Q{question.unique_id}")
            return modified_question
            
        except Exception as e:
            logger.error(f"✗ Failed to transform Q{question.unique_id}: {str(e)}")
            logger.info("Falling back to original question")
            return question

    def _get_correct_option_text(self, question: Question) -> str:
        """Extract the text of the correct answer"""
        correct_answer = question.correct_answer
        options = question.options
        
        if isinstance(correct_answer, int):
            return options[correct_answer]
        elif isinstance(correct_answer, str) and len(correct_answer) == 1:
            # Letter like "A", "B"
            index = ord(correct_answer.upper()) - ord('A')
            return options[index]
        elif isinstance(correct_answer, str):
            # Text match
            return correct_answer
        else:
            return options[0]

    def _get_correct_answer_index(self, correct_answer, options: List[str]) -> int:
        """Determine the index of the correct answer"""
        if isinstance(correct_answer, int):
            return correct_answer
        elif isinstance(correct_answer, str) and len(correct_answer) == 1:
            return ord(correct_answer.upper()) - ord('A')
        elif isinstance(correct_answer, str):
            try:
                return options.index(correct_answer)
            except ValueError:
                return 0
        else:
            return 0

    def _map_difficulty(self, b_value: float) -> str:
        """Map IRT b-value to difficulty string for QPool"""
        if b_value < -0.5:
            return "easy"
        elif b_value < 0.5:
            return "medium"
        else:
            return "hard"

    # =========================================================================
    # 🔧 FIX: CREATE RESPONSE WHEN QUESTION IS PRESENTED
    # =========================================================================
    
    def create_response_placeholder(self, session_id: int, question: Question, question_num: int) -> Response:
        """
        Create a response record when question is presented to user.
        This will be updated when user submits their answer.
        """
        response = Response(
            session_id=session_id,
            question_id=question.unique_id,
            question_num=question_num,
            user_answer=None,  # Will be filled when submitted
            is_correct=None,   # Will be calculated when submitted
            theta_math_after=None,
            theta_tech_after=None
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        logger.info(f"Created response placeholder for session {session_id}, question {question.unique_id}")
        return response

    # =========================================================================
    # EXAM WORKFLOW
    # =========================================================================
    
    def start_exam_with_first_question(
        self, 
        user_id: Optional[str] = None, 
        n_questions: int = 50
    ) -> Dict[str, Any]:
        """
        Start exam and return first question.
        Now creates the response placeholder immediately.
        """
        # Create session
        session = self.create_session(user_id=user_id, n_questions=n_questions)
        
        # Select first question (question_num = 1)
        first_question = self.select_next_question(session, question_num=1)
        
        # 🔧 FIX: Create response placeholder for first question
        self.create_response_placeholder(
            session_id=session.session_id,
            question=first_question,
            question_num=1
        )
        
        # Update session state
        session.current_question_num = 1
        self.db.commit()
        
        return {
            'session': session,
            'question': first_question
        }

    def submit_answer_and_get_next(
        self, 
        session_id: int, 
        user_answer
    ) -> Dict[str, Any]:
        """
        Process answer submission and return next question.
        
        🔧 FIXED: Now properly finds and updates the existing response placeholder.
        """
        
        # Get session
        session = self.get_session(session_id)
        
        if session.status != "in_progress":
            raise ValueError("Exam already completed or invalid session")
        
        # 🔧 FIX: Find the most recent response with NULL user_answer (the placeholder)
        open_response = (
            self.db.query(Response)
            .filter(
                Response.session_id == session_id,
                Response.user_answer == None  # Find unanswered placeholder
            )
            .order_by(Response.response_id.desc())
            .first()
        )
        
        if not open_response:
            raise ValueError(f"No pending question found for session {session_id}")
        
        # Get the question details
        question = self.db.query(Question).filter(
            Question.unique_id == open_response.question_id
        ).first()
        
        if not question:
            raise ValueError(f"Question {open_response.question_id} not found")
        
        # 🔧 FIX: Update the response with user's answer
        is_correct = self._check_answer(user_answer, question.correct_answer)
        
        open_response.user_answer = user_answer
        open_response.is_correct = is_correct
        
        # Update theta ONLY if this is an operational question
        if question.calibration_status == 'operational':
            self.update_theta(session)
            
            # Store theta values in response
            open_response.theta_math_after = session.theta_math
            open_response.theta_tech_after = session.theta_tech
        
        self.db.commit()
        
        # Build feedback
        feedback = {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'question_num': open_response.question_num
        }
        
        # Check if exam completed
        exam_completed = (session.current_question_num >= session.n_questions)
        
        next_question = None
        
        if not exam_completed:
            # Get next question
            next_question_num = session.current_question_num + 1
            next_question = self.select_next_question(session, next_question_num)
            
            # 🔧 FIX: Create response placeholder for next question
            self.create_response_placeholder(
                session_id=session.session_id,
                question=next_question,
                question_num=next_question_num
            )
            
            # Update session
            session.current_question_num = next_question_num
            self.db.commit()
        else:
            # Mark exam as completed
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Session {session_id} completed")
        
        return {
            'feedback': feedback,
            'next_question': next_question,
            'exam_completed': exam_completed
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _check_answer(self, user_answer, correct_answer) -> bool:
        """Check if answer is correct (handles both MCQ and MSQ)"""
        if isinstance(correct_answer, list):
            # MSQ: compare sorted lists
            return sorted(user_answer) == sorted(correct_answer)
        else:
            # MCQ: direct comparison
            return user_answer == correct_answer

    def update_theta(self, session: ExamSession):
        """
        Update theta estimates using ONLY operational questions.
        Pretest questions are ignored in ability estimation.
        """
        
        # Get all OPERATIONAL responses so far (join with Question table)
        responses = (
            self.db.query(Response, Question)
            .join(Question, Response.question_id == Question.unique_id)
            .filter(
                Response.session_id == session.session_id,
                Response.user_answer != None,  # Only answered questions
                Question.calibration_status == 'operational'  # ONLY operational
            )
            .all()
        )
        
        if not responses:
            # No operational questions answered yet, keep initial theta
            return
        
        # Extract response patterns and questions
        response_pattern = [int(r.Response.is_correct) for r in responses]
        questions_answered = [r.Question for r in responses]
        
        # Calculate new theta using IRT engine
        try:
            theta_est = self.irt_engine.estimate_theta_eap(
                response_pattern=response_pattern,
                questions=questions_answered
            )
            
            # Update session with new estimates
            session.theta_math = theta_est['theta'][0]
            session.theta_tech = theta_est['theta'][1]
            session.theta_se_math = theta_est['SE'][0]
            session.theta_se_tech = theta_est['SE'][1]
            
            # Update domain counts
            session.math_count = sum(1 for q in questions_answered if q.domain == 'math')
            session.tech_count = sum(1 for q in questions_answered if q.domain == 'tech')
            
            logger.debug(f"Updated theta for session {session.session_id}: "
                        f"Math={session.theta_math:.2f}, Tech={session.theta_tech:.2f}")
        
        except Exception as e:
            logger.error(f"Failed to update theta: {e}")
            # Don't fail the exam, just keep previous theta

    # =========================================================================
    # RESULTS
    # =========================================================================
    
    def get_results(self, session_id: int) -> Dict[str, Any]:
        """
        Get final results with proper operational/pretest separation.
        """
        session = self.get_session(session_id)
        
        if session.status != "completed":
            raise ValueError("Exam not yet completed")
        
        # Get ALL responses (operational + pretest)
        all_responses = (
            self.db.query(Response, Question)
            .join(Question, Response.question_id == Question.unique_id)
            .filter(Response.session_id == session_id)
            .all()
        )
        
        # Separate operational and pretest
        operational_responses = [
            r for r in all_responses 
            if r.Question.calibration_status == 'operational'
        ]
        
        pretest_responses = [
            r for r in all_responses 
            if r.Question.calibration_status == 'pretest'
        ]
        
        # Calculate statistics
        total_questions = len(all_responses)
        total_correct = sum(1 for r in all_responses if r.Response.is_correct)
        
        operational_questions = len(operational_responses)
        operational_correct = sum(1 for r in operational_responses if r.Response.is_correct)
        
        # Accuracy (out of all 50 questions)
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0.0
        
        return {
            'session_id': session_id,
            'total_questions': total_questions,
            'correct_answers': total_correct,
            'accuracy': round(accuracy, 2),
            'operational_questions': operational_questions,
            'operational_correct': operational_correct,
            'math_ability': {
                'value': round(session.theta_math, 2),
                'standard_error': round(session.theta_se_math, 2),
                'interpretation': self._interpret_theta(session.theta_math)
            },
            'tech_ability': {
                'value': round(session.theta_tech, 2),
                'standard_error': round(session.theta_se_tech, 2),
                'interpretation': self._interpret_theta(session.theta_tech)
            },
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        }

    def _interpret_theta(self, theta: float) -> str:
        """Interpret theta value"""
        if theta < -1.5:
            return "Below Average"
        elif theta < -0.5:
            return "Low Average"
        elif theta < 0.5:
            return "Average"
        elif theta < 1.5:
            return "Above Average"
        else:
            return "Superior"