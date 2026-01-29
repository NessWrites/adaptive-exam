"""
Updated ExamService with Pretest Item Support
50 questions total: 40 operational + 10 pretest
"""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import random
from datetime import datetime

from backend.app.models.database_models import Question, ExamSession, Response
from backend.app.services.irt_engine import IRTEngine
from backend.app.core.config import get_settings

settings = get_settings()


class ExamService:
    """Business logic for adaptive examination with pretest items"""
    
    # EXAM CONFIGURATION
    TOTAL_QUESTIONS = 50          # Total questions in exam
    OPERATIONAL_QUESTIONS = 40    # Scored questions (adaptive)
    PRETEST_QUESTIONS = 10        # Unscored questions (random)
    
    def __init__(self, db: Session):
        self.db = db
        self.irt = IRTEngine()
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def create_session(self, user_id: Optional[str] = None, n_questions: int = 50) -> ExamSession:
        """Create a new exam session"""
        session = ExamSession(
            user_id=user_id,
            n_questions=n_questions,  # Always 50 now
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
    # ITEM SELECTION (MODIFIED FOR PRETEST)
    # ========================================================================
    
    def select_next_question(self, session_id: int) -> Optional[Question]:
        """
        Select next question - either operational (adaptive) or pretest (random).
        
        LOGIC:
        1. Count how many pretest items already given
        2. Decide if this position should be pretest
        3. If yes → select random pretest item
        4. If no → select adaptive operational item
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
        
        if should_be_pretest:
            print(f"[PRETEST] Position {session.current_question_num + 1}/50")
            return self._select_pretest_item(session_id)
        else:
            print(f"[OPERATIONAL] Position {session.current_question_num + 1}/50")
            return self._select_operational_item(session_id)
    
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
        5. Randomize ties (within 5% of max info)
        """
        
        session = self.get_session(session_id)
        used_ids = self._get_administered_items(session_id)
        
        # Query OPERATIONAL items only
        query = self.db.query(Question).filter(
            Question.calibration_status == 'operational'
        )
        
        if used_ids:
            query = query.filter(~Question.unique_id.in_(used_ids))
        
        # Content balancing
        target_math = self.OPERATIONAL_QUESTIONS // 2  # 20
        target_tech = self.OPERATIONAL_QUESTIONS // 2  # 20
        
        operational_count = self.db.query(Response).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id,
            Question.calibration_status == 'operational'
        ).count()
        
        remaining_operational = self.OPERATIONAL_QUESTIONS - operational_count
        math_needed = target_math - session.math_count
        tech_needed = target_tech - session.tech_count
        
        if tech_needed > 0 and math_needed == 0:
            query = query.filter(Question.domain == 'tech')
        elif math_needed > 0 and tech_needed == 0:
            query = query.filter(Question.domain == 'math')
        
        candidates = query.all()
        
        if not candidates:
            raise ValueError("No operational items available for selection")
        
        # Calculate Fisher Information for all candidates
        theta = np.array([session.theta_math, session.theta_tech])
        
        items_with_info = []
        for item in candidates:
            info = self.irt.fisher_information_matrix(theta, item.a_values, item.b_value)
            items_with_info.append((item, info))
        
        # Sort by Fisher Information (highest first)
        items_with_info.sort(key=lambda x: x[1], reverse=True)
        
        # Get max information
        max_info = items_with_info[0][1]
        
        # RANDOMIZE TIES: Select randomly from items within 5% of max info
        threshold = max_info * 0.95
        top_items = [(item, info) for item, info in items_with_info if info >= threshold]
        
        # Randomly select from top items
        selected_item, selected_info = random.choice(top_items)
        
        print(f"  → Selected operational Q{selected_item.unique_id} ({selected_item.concept_tag}), "
            f"Info={selected_info:.3f} (max={max_info:.3f}, ties={len(top_items)})")
        
        return selected_item
    
    # ========================================================================
    # THETA UPDATE (MODIFIED - IGNORE PRETEST)
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
            Response.is_correct.isnot(None),  # Answered (not -1)
            Question.calibration_status == 'operational'  # IGNORE PRETEST!
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
            # Create new response (shouldn't happen but handle it)
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
            
            # Update domain count (ONLY for operational)
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
    # RESULTS (MODIFIED - COUNT ONLY OPERATIONAL)
    # ========================================================================
    
    def get_results(self, session_id: int) -> Dict:
        """
        Calculate final results.
        
        Accuracy: Based on ALL 50 questions (40 operational + 10 pretest)
        Theta: Based on ONLY 40 operational questions (calibrated items)
        
        This gives students full transparency on their performance while
        ensuring ability estimates are based on validated items only.
        """
        
        session = self.get_session(session_id)
        
        # ========================================================================
        # OPERATIONAL ITEMS (for theta calculation)
        # ========================================================================
        
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
        
        # Operational accuracy (for reference, not returned)
        operational_accuracy = (operational_correct / operational_total * 100) if operational_total > 0 else 0
        
        # ========================================================================
        # ALL QUESTIONS (for overall accuracy)
        # ========================================================================
        
        # Count correct answers across ALL questions (operational + pretest)
        total_correct = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct == True
        ).count()
        
        # Total questions answered (should be 50)
        total_questions = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct.isnot(None)  # Only answered questions
        ).count()
        
        # Overall accuracy (all 50 questions)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # ========================================================================
        # RETURN RESULTS
        # ========================================================================
        
        return {
            'session_id': session_id,
            'total_questions': total_questions,  # 50 total
            'correct_answers': total_correct,    # Correct out of 50
            'accuracy': overall_accuracy,        # Percentage out of 50
            
            # Breakdown (optional - shows the split)
            'operational_questions': operational_total,    # 40
            'operational_correct': operational_correct,    # Correct operational
            
            
            # Ability estimates (based on 40 operational only)
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
        
        # Select first question (will be operational, not pretest)
        first_question = self.select_next_question(session.session_id)
        
        if not first_question:
            raise ValueError("No questions available")
        
        # Record that this question was served
        response = Response(
            session_id=session.session_id,
            question_id=first_question.unique_id,
            question_num=1,
            is_correct=None  # Not answered yet
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
        
        # Get next question
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