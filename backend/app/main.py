from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import numpy as np
from scipy.stats import multivariate_normal
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # adjust depth
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="MIRT CAT Exam API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for exam sessions
exam_sessions = {}

# ============================================================
# PYDANTIC MODELS
# ============================================================

class StartExamRequest(BaseModel):
    item_bank_path: str = r"D:\Internship\IRT\adaptive-exam\data\2pl_mirt_cleaned.json"
    min_items: int = 10
    max_items: int = 40
    target_se: float = 0.30

class StartExamResponse(BaseModel):
    session_id: str
    message: str
    total_items: int
    config: Dict[str, Any]

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: Any  # Can be string (MCQ) or list (MSQ)

class QuestionResponse(BaseModel):
    session_id: str
    question_num: int
    item_id: str
    question_text: str
    options: Optional[List[str]]
    image_url: Optional[str]
    is_msq: bool
    progress: Dict[str, Any]
    current_theta: List[float]
    current_se: List[float]

class AnswerFeedback(BaseModel):
    is_correct: bool
    user_answer: Any
    correct_answer: Optional[Any]
    theta_before: List[float]
    theta_after: List[float]
    se_before: List[float]
    se_after: List[float]
    se_target_met: Dict[str, bool]
    next_question: Optional[QuestionResponse]
    test_completed: bool
    completion_reason: Optional[str]

class FinalResults(BaseModel):
    completion_reason: str
    questions_answered: int
    correct_responses: int
    accuracy: float
    final_theta_math: float
    final_theta_tech: float
    final_se_math: float
    final_se_tech: float
    se_target_achieved_math: bool
    se_target_achieved_tech: bool
    math_questions: int
    tech_questions: int

# ============================================================
# MIRT CAT EXAM CLASS (Modified for API)
# ============================================================

class MIRT_CAT_Exam:
    """
    2 Dimensional MIRT CAT Exam System - API Version
    """
    
    def __init__(self, item_bank_path, min_items=10, max_items=40, target_se=0.30):
        # Load JSON file
        with open(item_bank_path, 'r', encoding='utf-8') as f:
            self.item_bank = json.load(f)
        
        # Initialize test state
        self.remaining_items = self.item_bank.copy()
        self.administered_items = []
        self.responses = []
        
        # Initialize 2D ability estimates
        self.theta_se = np.array([1.0, 1.0])
        self.theta = np.array([0.0, 0.0])
         
        # Test length parameters
        self.min_items = min_items
        self.max_items = max_items
        self.target_se = target_se
        
        # Content tracking
        self.math_count = 0
        self.tech_count = 0
        
        # Test completion tracking
        self.test_completed = False
        self.completion_reason = None
        
        self.log = []
        self.current_item = None
        
    def mirt_2pl_probability(self, theta, item):
        """Calculate probability of correct response using 2PL MIRT model."""
        a = item['a']
        a1 = a[0]
        a2 = a[1]
        b = item['b']
        
        exponent = a1 * theta[0] + a2 * theta[1] - b
        probability = 1 / (1 + np.exp(-exponent))
        
        return np.clip(probability, 1e-9, 1-1e-9)
    
    def fisher_information_matrix(self, theta, item):
        """Calculate Fisher Information for item selection."""
        p = self.mirt_2pl_probability(theta, item)
        q = 1 - p
        
        a_vector = item['a']
        scaling = p * q
        information_matrix = scaling * np.outer(a_vector, a_vector)
        
        return np.trace(information_matrix)
    
    def likelihood(self, theta, responses, items):
        """Calculate likelihood of responses given theta."""
        log_likelihood = 1.0
        
        for response, item in zip(responses, items):
            p = self.mirt_2pl_probability(theta, item)
            if response == 1:
                log_likelihood *= p
            else:
                log_likelihood *= (1 - p)
                
        return log_likelihood
    
    def update_theta_eap(self):
        """Update ability estimates using Expected A Posteriori (EAP)."""
        if not self.responses:
            return
        
        n_samples = 2000
        
        # Prior: N(0, Σ) with correlation
        prior_mean = np.array([0, 0])
        prior_cov = np.array([[1.0, 0.5],
                              [0.5, 1.0]])
        
        # Generate samples
        theta_samples = np.random.multivariate_normal(
            mean=prior_mean, cov=prior_cov, size=n_samples
        )
        
        # Calculate likelihoods
        likelihoods = np.array([
            self.likelihood(theta_sample, self.responses, self.administered_items) 
            for theta_sample in theta_samples
        ])
        
        # Prior densities        
        prior_densities = multivariate_normal.pdf(
            theta_samples, mean=prior_mean, cov=prior_cov
        )
        
        # Posterior weights
        posterior = likelihoods * prior_densities
        weights = posterior / np.sum(posterior)
        
        # EAP estimate
        self.theta = np.sum(theta_samples * weights.reshape(-1, 1), axis=0)
        
        # Standard error
        deviation = theta_samples - self.theta
        variance = np.sum(weights.reshape(-1, 1) * (deviation ** 2), axis=0)
        self.theta_se = np.sqrt(variance)
    
    def check_stopping_rule(self):
        """Check if test should stop based on SE targets."""
        n_items = len(self.administered_items)
        
        if n_items < self.min_items:
            return False, None
        
        if n_items >= self.max_items:
            return True, f"Maximum {self.max_items} items reached"
        
        math_se_met = self.theta_se[0] <= self.target_se
        tech_se_met = self.theta_se[1] <= self.target_se
        
        if math_se_met and tech_se_met:
            return True, f"SE targets achieved: Math SE={self.theta_se[0]:.3f}, Tech SE={self.theta_se[1]:.3f}"
        
        return False, None
        
    def select_next_item(self):
        """Select next item based on maximum Fisher Information."""
        should_stop, reason = self.check_stopping_rule()
        if should_stop:
            self.test_completed = True
            self.completion_reason = reason
            return None, reason
        
        if not self.remaining_items:
            self.test_completed = True
            self.completion_reason = "No more items available"
            return None, "No more items available"
        
        # Content balancing
        n_items = len(self.administered_items)
        
        if n_items < self.min_items:
            projected_total = self.min_items
        else:
            projected_total = min(n_items + 10, self.max_items)
        
        target_math = projected_total // 2
        target_tech = projected_total // 2
        
        math_needed = target_math - self.math_count
        tech_needed = target_tech - self.tech_count
        
        # Filter items based on content needs
        if tech_needed > 0 and math_needed == 0:
            candidate_items = [item for item in self.remaining_items if item['a'][0] == 0]
        elif math_needed > 0 and tech_needed == 0:
            candidate_items = [item for item in self.remaining_items if item['a'][1] == 0]
        else:
            candidate_items = self.remaining_items
        
        if not candidate_items:
            return None, "No items available for required content"
        
        # Calculate information for each candidate
        item_info = []
        for item in candidate_items:
            info = self.fisher_information_matrix(self.theta, item)
            item_info.append((item, info))
        
        # Sort by information (descending)
        item_info.sort(key=lambda x: x[1], reverse=True)
        
        # First item: random from top 5
        if len(self.administered_items) == 0:
            top_items = item_info[:min(5, len(item_info))]
            selected_item, info = top_items[np.random.randint(len(top_items))]
        else:
            selected_item, info = item_info[0]
        
        return selected_item, None
    
    def normalize_string(self, text):
        """Normalize string for comparison."""
        if not isinstance(text, str):
            return str(text)
        return ''.join(text.split()).lower()
    
    def check_answer(self, user_answer, item):
        """Check if user's answer is correct."""
        if 'correct_answer' not in item or 'options' not in item:
            return None
        
        correct_answer = item['correct_answer']
        options = item['options']
        
        # Determine if this is MSQ
        if isinstance(correct_answer, list):
            correct_answers = correct_answer
            is_msq = len(correct_answers) > 1
        elif isinstance(correct_answer, str) and ',' in correct_answer:
            correct_answers = [ans.strip() for ans in correct_answer.split(',')]
            is_msq = len(correct_answers) > 1
        else:
            correct_answers = [correct_answer]
            is_msq = False
        
        # Handle MSQ
        if is_msq and isinstance(user_answer, list):
            try:
                user_option_texts = []
                for letter in user_answer:
                    user_index = ['A', 'B', 'C', 'D'].index(letter)
                    if user_index >= len(options):
                        return None
                    user_option_texts.append(options[user_index])
                
                user_normalized = set(self.normalize_string(text) for text in user_option_texts)
                correct_normalized = set(self.normalize_string(text) for text in correct_answers)
                
                return user_normalized == correct_normalized
                
            except (ValueError, IndexError):
                return None
        
        # Handle MCQ
        elif not is_msq and isinstance(user_answer, str):
            try:
                user_index = ['A', 'B', 'C', 'D'].index(user_answer)
                if user_index >= len(options):
                    return None
                user_option_text = options[user_index]
            except (ValueError, IndexError):
                return None
            
            user_normalized = self.normalize_string(user_option_text)
            correct_normalized = self.normalize_string(correct_answers[0])
            
            return user_normalized == correct_normalized
        else:
            return False
    
    def record_response(self, user_answer, is_correct):
        """Record response and update abilities."""
        if self.current_item is None:
            return
        
        theta_before = self.theta.copy()
        se_before = self.theta_se.copy()
        
        # Store response
        self.administered_items.append(self.current_item)
        self.responses.append(1 if is_correct else 0)
        
        # Update content counts
        if self.current_item['a'][1] == 0:
            self.math_count += 1
        else:
            self.tech_count += 1
        
        # Remove from remaining
        item_id = self.current_item.get('unique_id', self.current_item.get('item'))
        self.remaining_items = [i for i in self.remaining_items if i.get('unique_id', i.get('item')) != item_id]
        
        # Update ability estimates
        self.update_theta_eap()
        
        # Log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': self.current_item.get('unique_id', self.current_item.get('item')),
            'response': 'Correct' if is_correct else 'Incorrect',
            'user_answer': user_answer,
            'correct_answer': self.current_item.get('correct_answer', 'N/A'),
            'theta_before': theta_before.tolist(),
            'theta_after': self.theta.tolist(),
            'se_before': se_before.tolist(),
            'se_after': self.theta_se.tolist(),
        }
        
        self.log.append(log_entry)
        
        return theta_before, se_before

# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "MIRT CAT Exam API",
        "version": "1.0.0",
        "endpoints": {
            "POST /start": "Start a new exam session",
            "POST /next": "Get the next question",
            "POST /submit": "Submit an answer",
            "GET /results/{session_id}": "Get final results"
        }
    }

@app.post("/start", response_model=StartExamResponse)
async def start_exam(request: StartExamRequest):
    """Start a new exam session."""
    try:
        # Create new exam instance
        exam = MIRT_CAT_Exam(
            item_bank_path=request.item_bank_path,
            min_items=request.min_items,
            max_items=request.max_items,
            target_se=request.target_se
        )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store session
        exam_sessions[session_id] = exam
        
        return StartExamResponse(
            session_id=session_id,
            message="Exam session started successfully",
            total_items=len(exam.item_bank),
            config={
                "min_items": request.min_items,
                "max_items": request.max_items,
                "target_se": request.target_se
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/next", response_model=QuestionResponse)
async def get_next_question(session_id: str):
    """Get the next question for the session."""
    if session_id not in exam_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exam = exam_sessions[session_id]
    
    if exam.test_completed:
        raise HTTPException(status_code=400, detail="Test already completed")
    
    # Select next item
    item, reason = exam.select_next_item()
    
    if item is None:
        raise HTTPException(status_code=400, detail=f"No more items: {reason}")
    
    # Store current item
    exam.current_item = item
    
    # Check if MSQ
    is_msq = False
    if 'correct_answer' in item:
        correct_answer = item['correct_answer']
        if isinstance(correct_answer, list) and len(correct_answer) > 1:
            is_msq = True
        elif isinstance(correct_answer, str) and ',' in correct_answer:
            answers = [ans.strip() for ans in correct_answer.split(',')]
            if len(answers) > 1:
                is_msq = True
    
    return QuestionResponse(
        session_id=session_id,
        question_num=len(exam.administered_items) + 1,
        item_id=str(item.get('unique_id', item.get('item'))),
        question_text=item['question_text'],
        options=item.get('options'),
        image_url=item.get('image_url'),
        is_msq=is_msq,
        progress={
            "current": len(exam.administered_items),
            "min_items": exam.min_items,
            "max_items": exam.max_items,
            "math_count": exam.math_count,
            "tech_count": exam.tech_count
        },
        current_theta=exam.theta.tolist(),
        current_se=exam.theta_se.tolist()
    )

@app.post("/submit", response_model=AnswerFeedback)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer and get feedback."""
    if request.session_id not in exam_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exam = exam_sessions[request.session_id]
    
    if exam.current_item is None:
        raise HTTPException(status_code=400, detail="No current question. Call /next first.")
    
    # Check answer
    is_correct = exam.check_answer(request.answer, exam.current_item)
    
    if is_correct is None:
        is_correct = False
    
    # Record response and get theta before
    theta_before, se_before = exam.record_response(request.answer, is_correct)
    
    # Prepare feedback
    feedback = AnswerFeedback(
        is_correct=is_correct,
        user_answer=request.answer,
        correct_answer=exam.current_item.get('correct_answer'),
        theta_before=theta_before.tolist(),
        theta_after=exam.theta.tolist(),
        se_before=se_before.tolist(),
        se_after=exam.theta_se.tolist(),
        se_target_met={
            'math': exam.theta_se[0] <= exam.target_se,
            'tech': exam.theta_se[1] <= exam.target_se
        },
        next_question=None,
        test_completed=False,
        completion_reason=None
    )
    
    # Clear current item
    exam.current_item = None
    
    # Check if test should continue
    should_stop, reason = exam.check_stopping_rule()
    
    if should_stop or not exam.remaining_items:
        exam.test_completed = True
        exam.completion_reason = reason or "No more items available"
        feedback.test_completed = True
        feedback.completion_reason = exam.completion_reason
    else:
        # Get next question automatically
        item, _ = exam.select_next_item()
        if item:
            exam.current_item = item
            
            # Check if MSQ
            is_msq = False
            if 'correct_answer' in item:
                correct_answer = item['correct_answer']
                if isinstance(correct_answer, list) and len(correct_answer) > 1:
                    is_msq = True
                elif isinstance(correct_answer, str) and ',' in correct_answer:
                    answers = [ans.strip() for ans in correct_answer.split(',')]
                    if len(answers) > 1:
                        is_msq = True
            
            feedback.next_question = QuestionResponse(
                session_id=request.session_id,
                question_num=len(exam.administered_items) + 1,
                item_id=str(item.get('unique_id', item.get('item'))),
                question_text=item['question_text'],
                options=item.get('options'),
                image_url=item.get('image_url'),
                is_msq=is_msq,
                progress={
                    "current": len(exam.administered_items),
                    "min_items": exam.min_items,
                    "max_items": exam.max_items,
                    "math_count": exam.math_count,
                    "tech_count": exam.tech_count
                },
                current_theta=exam.theta.tolist(),
                current_se=exam.theta_se.tolist()
            )
    
    return feedback

@app.get("/results/{session_id}", response_model=FinalResults)
async def get_results(session_id: str):
    """Get final results for a completed session."""
    if session_id not in exam_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    exam = exam_sessions[session_id]
    
    if not exam.test_completed:
        raise HTTPException(status_code=400, detail="Test not completed yet")
    
    return FinalResults(
        completion_reason=exam.completion_reason or "Unknown",
        questions_answered=len(exam.administered_items),
        correct_responses=sum(exam.responses),
        accuracy=sum(exam.responses) / len(exam.responses) if exam.responses else 0,
        final_theta_math=float(exam.theta[0]),
        final_theta_tech=float(exam.theta[1]),
        final_se_math=float(exam.theta_se[0]),
        final_se_tech=float(exam.theta_se[1]),
        se_target_achieved_math=exam.theta_se[0] <= exam.target_se,
        se_target_achieved_tech=exam.theta_se[1] <= exam.target_se,
        math_questions=exam.math_count,
        tech_questions=exam.tech_count
    )

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session from memory."""
    if session_id not in exam_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del exam_sessions[session_id]
    return {"message": "Session deleted successfully"}

