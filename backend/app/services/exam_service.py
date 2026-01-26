from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
from datetime import datetime

from backend.app.models.database_models import Question, ExamSession, Response
from backend.app.services.irt_engine import IRTEngine
from backend.app.core.config import get_settings

settings = get_settings()


class ExamService:
    """Business logic for adaptive examination"""
    
    def __init__(self, db: Session):
        self.db = db
        self.irt = IRTEngine()
    
    def create_session(self, user_id: Optional[str] = None, n_questions: int = 40) -> ExamSession:
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
    
    def get_administered_items(self, session_id: int) -> List[int]:
        """Get list of question IDs already administered"""
        responses = self.db.query(Response.question_id).filter(
            Response.session_id == session_id
        ).all()
        
        return [r.question_id for r in responses]
    
    def get_response_history(self, session_id: int) -> List[dict]:
        """Get response history with question details"""
        responses = self.db.query(Response, Question).join(
            Question, Response.question_id == Question.unique_id
        ).filter(
            Response.session_id == session_id
        ).order_by(Response.question_num).all()
        
        history = []
        for resp, question in responses:
            history.append({
                'response': resp.is_correct,
                'a_values': question.a_values,
                'b_value': question.b_value
            })
        
        return history
    
    def select_next_item(self, session: ExamSession) -> Optional[Question]:
        """
        Select next item using Maximum Fisher Information.
        Implements flexible content balancing.
        """
        # Check if exam is complete
        if session.current_question_num >= session.n_questions:
            return None
        
        # Get already administered items
        administered_ids = self.get_administered_items(session.session_id)
        
        # Build base query for remaining items
        query = self.db.query(Question).filter(
            ~Question.unique_id.in_(administered_ids) if administered_ids else True
        )
        
        candidate_items = query.all()
        
        # Check what domains are available in the database
        available_domains = set()
        for item in candidate_items:
            if item.domain:
                available_domains.add(item.domain)
        
        # Content balancing (only if both domains exist)
        has_both_domains = 'math' in available_domains and 'tech' in available_domains
        
        if has_both_domains:
            # Apply 50/50 balancing
            target_math = session.n_questions // 2
            target_tech = session.n_questions // 2
            
            math_needed = target_math - session.math_count
            tech_needed = target_tech - session.tech_count
            
            # Apply content constraints
            if tech_needed > 0 and math_needed == 0:
                query = self.db.query(Question).filter(
                    ~Question.unique_id.in_(administered_ids) if administered_ids else True,
                    Question.domain == 'tech'
                )
                candidate_items = query.all()
                constraint = 'tech-only'
            elif math_needed > 0 and tech_needed == 0:
                query = self.db.query(Question).filter(
                    ~Question.unique_id.in_(administered_ids) if administered_ids else True,
                    Question.domain == 'math'
                )
                candidate_items = query.all()
                constraint = 'math-only'
            else:
                constraint = 'balanced'
        else:
            # Single domain exam - no balancing needed
            constraint = f"{list(available_domains)[0] if available_domains else 'unknown'}-only exam"
        
        # DEBUG: Log selection details
        print(f"[DEBUG] Session {session.session_id}: Q{session.current_question_num + 1}/{session.n_questions}")
        print(f"[DEBUG] Math: {session.math_count}, Tech: {session.tech_count}")
        print(f"[DEBUG] Available domains: {available_domains}")
        print(f"[DEBUG] Constraint: {constraint}")
        print(f"[DEBUG] Candidates: {len(candidate_items)}")
        
        if not candidate_items:
            print(f"[ERROR] No questions available!")
            return None
        
        # Calculate Fisher Information for each candidate
        theta = np.array([session.theta_math, session.theta_tech])
        
        # First item: random from top 5
        if session.current_question_num == 0:
            item_info = [
                (item, self.irt.fisher_information_matrix(theta, item.a_values, item.b_value))
                for item in candidate_items
            ]
            item_info.sort(key=lambda x: x[1], reverse=True)
            
            top_items = item_info[:min(5, len(item_info))]
            selected_item, _ = top_items[np.random.randint(len(top_items))]
            
            return selected_item
        
        # Maximum information selection
        best_item = None
        max_info = -float('inf')
        
        for item in candidate_items:
            info = self.irt.fisher_information_matrix(theta, item.a_values, item.b_value)
            
            if info > max_info:
                max_info = info
                best_item = item
        
        return best_item
    
    def submit_answer(
        self, 
        session_id: int, 
        user_answer: str | List[str]
    ) -> Tuple[bool, Question, ExamSession]:
        """
        Submit answer and update session.
        
        Returns:
            (is_correct, question, updated_session)
        """
        session = self.get_session(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        if session.status != "in_progress":
            raise ValueError("Session is not active")
        
        # Get the current question
        last_response = self.db.query(Response).filter(
            Response.session_id == session_id
        ).order_by(Response.question_num.desc()).first()
        
        if not last_response:
            raise ValueError("No question to answer")
        
        question = self.db.query(Question).filter(
            Question.unique_id == last_response.question_id
        ).first()
        
        # Check if already answered
        if last_response.is_correct is not None:
            raise ValueError("Question already answered")
        
        # Check answer
        is_correct = self.irt.check_answer(
            user_answer, 
            question.correct_answer, 
            question.options
        )
        
        # Update response
        last_response.user_answer = user_answer
        last_response.is_correct = is_correct 
        
        # Update ability estimates
        history = self.get_response_history(session_id)
        
        if history:
            responses = [item['response'] for item in history]
            items = [{'a_values': item['a_values'], 'b_value': item['b_value']} 
                    for item in history]
            
            theta, theta_se = self.irt.update_theta_eap(responses, items)
            
            session.theta_math = float(theta[0])
            session.theta_tech = float(theta[1])
            session.theta_se_math = float(theta_se[0])
            session.theta_se_tech = float(theta_se[1])
        
        # Update theta in response
        last_response.theta_math_after = session.theta_math
        last_response.theta_tech_after = session.theta_tech
        
        # Update content count
        if question.domain == 'math':
            session.math_count += 1
        else:
            session.tech_count += 1
        
        # Update question count
        session.current_question_num += 1
        
        # Check if exam is complete
        if session.current_question_num >= session.n_questions:
            session.status = "completed"
            session.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        return is_correct, question, session
    
    def get_next_question(self, session_id: int) -> Optional[Question]:
        """
        Get next question for the session.
        Creates a response record for tracking.
        """
        session = self.get_session(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        if session.status != "in_progress":
            return None
        
        # Check if there's an unanswered question
        last_response = self.db.query(Response).filter(
            Response.session_id == session_id
        ).order_by(Response.question_num.desc()).first()
        
        if last_response and last_response.is_correct is None:
            # Return the unanswered question
            return self.db.query(Question).filter(
                Question.unique_id == last_response.question_id
            ).first()
        
        # Select next item
        next_item = self.select_next_item(session)
        
        if not next_item:
            return None
        
        # Create response record
        response = Response(
            session_id=session_id,
            question_id=next_item.unique_id,
            question_num=session.current_question_num + 1,
            is_correct=None  # Will be filled when answer is submitted
        )
        
        self.db.add(response)
        self.db.commit()
        
        return next_item
    
    def get_results(self, session_id: int) -> dict:
        """Get final exam results"""
        session = self.get_session(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        # Get all responses
        responses = self.db.query(Response).filter(
            Response.session_id == session_id,
            Response.is_correct.isnot(None)
        ).all()
        
        correct_count = sum(1 for r in responses if r.is_correct)
        total_count = len(responses)
        
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'session_id': session_id,
            'total_questions': total_count,
            'correct_answers': correct_count,
            'accuracy': accuracy,
            'math_ability': {
                'value': session.theta_math,
                'standard_error': session.theta_se_math,
                'interpretation': self.irt.interpret_ability(session.theta_math)
            },
            'tech_ability': {
                'value': session.theta_tech,
                'standard_error': session.theta_se_tech,
                'interpretation': self.irt.interpret_ability(session.theta_tech)
            },
            'completed_at': session.completed_at
        }
    
    # New combined methods for streamlined API
    
    def start_exam_with_first_question(
        self, 
        user_id: Optional[str] = None, 
        n_questions: int = 40
    ) -> Dict[str, Any]:
        """
        Start exam and return session with first question.
        
        Returns dict with 'session' and 'question' keys.
        """
        # Create session
        session = self.create_session(user_id, n_questions)
        
        # Get first question
        first_question = self.get_next_question(session.session_id)
        
        if not first_question:
            raise ValueError("No questions available in the database")
        
        return {
            'session': {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'status': session.status,
                'current_question_num': session.current_question_num,
                'n_questions': session.n_questions,
                'theta_math': session.theta_math,
                'theta_tech': session.theta_tech,
                'math_count': session.math_count,
                'tech_count': session.tech_count,
                'created_at': session.created_at
            },
            'question': {
                'unique_id': first_question.unique_id,
                'question_text': first_question.question_text,
                'options': first_question.options,
                'image_url': first_question.image_url,
                'question_type': first_question.question_type,
                'question_num': 1,
                'total_questions': session.n_questions
            }
        }
    
    def submit_answer_and_get_next(
        self, 
        session_id: int, 
        user_answer: str | List[str]
    ) -> Dict[str, Any]:
        """
        Submit answer and return feedback with next question (or completion status).
        
        Returns dict with 'feedback', 'next_question', and 'exam_completed' keys.
        """
        # Submit answer
        is_correct, question, session = self.submit_answer(session_id, user_answer)
        
        # Prepare feedback
        feedback = {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'theta_math': session.theta_math,
            'theta_tech': session.theta_tech,
            'question_num': session.current_question_num,
            'total_questions': session.n_questions
        }
        
        # Check if exam is complete
        exam_completed = session.status == "completed"
        
        # Get next question if not completed
        next_question = None
        if not exam_completed:
            next_q = self.get_next_question(session_id)
            if next_q:
                next_question = {
                    'unique_id': next_q.unique_id,
                    'question_text': next_q.question_text,
                    'options': next_q.options,
                    'image_url': next_q.image_url,
                    'question_type': next_q.question_type,
                    'question_num': session.current_question_num + 1,
                    'total_questions': session.n_questions
                }
        
        return {
            'feedback': feedback,
            'next_question': next_question,
            'exam_completed': exam_completed
        }
