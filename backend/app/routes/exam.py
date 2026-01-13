from fastapi import APIRouter, HTTPException
from backend.app.schemas.exam import (
    StartExamRequest, StartExamResponse,
    QuestionResponse, SubmitAnswerRequest,
    AnswerFeedback, FinalResults, SessionDeleteResponse
)
from backend.app.services.session import session_manager
from backend.app.services.mirt_cat import MIRT_CAT_Exam
from backend.app.core.config import settings
from backend.app.core.exception import (
    SessionNotFoundException, TestCompletedException,
    NoCurrentQuestionException, TestNotCompletedException,
    NoMoreItemsException, ItemBankLoadException
)

router = APIRouter(prefix="/exam", tags=["exam"])

@router.post("/start", response_model=StartExamResponse)
async def start_exam(request: StartExamRequest):
    """Start a new exam session."""
    try:
        # Use default path if not provided or empty
        item_bank_path = request.item_bank_path
        if not item_bank_path or item_bank_path.strip() == "":
            item_bank_path = settings.DEFAULT_ITEM_BANK_PATH
        
        # Validate path exists
        from pathlib import Path
        if not Path(item_bank_path).exists():
            raise HTTPException(
                status_code=400, 
                detail=f"Item bank file not found at: {item_bank_path}"
            )
        
        # Create new exam session
        session_id, exam = session_manager.create_session(
            item_bank_path=item_bank_path,
            min_items=request.min_items,
            max_items=request.max_items,
            target_se=request.target_se
        )
        
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
    except ValueError as e:
        raise ItemBankLoadException(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next", response_model=QuestionResponse)
async def get_next_question(session_id: str):
    """Get the next question for the session."""
    exam = session_manager.get_session(session_id)
    
    if exam.test_completed:
        raise TestCompletedException()
    
    # Select next item
    item, reason = exam.select_next_item()
    
    if item is None:
        raise NoMoreItemsException(reason or "Unknown reason")
    
    # Store current item
    exam.current_item = item
    
    # Check if MSQ
    is_msq = MIRT_CAT_Exam.is_msq_item(item)
    
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

@router.post("/submit", response_model=AnswerFeedback)
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer and get feedback."""
    exam = session_manager.get_session(request.session_id)
    
    if exam.current_item is None:
        raise NoCurrentQuestionException()
    
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
            is_msq = MIRT_CAT_Exam.is_msq_item(item)
            
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

@router.get("/results/{session_id}", response_model=FinalResults)
async def get_results(session_id: str):
    """Get final results for a completed session."""
    exam = session_manager.get_session(session_id)
    
    if not exam.test_completed:
        raise TestNotCompletedException()
    
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

@router.delete("/session/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(session_id: str):
    """Delete a session from memory."""
    session_manager.delete_session(session_id)
    return SessionDeleteResponse(message="Session deleted successfully")