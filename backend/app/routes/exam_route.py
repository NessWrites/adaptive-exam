from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.postgresql.connection import get_db
from backend.app.services.exam_service import ExamService
from backend.app.schemas.exam_schema import (
     SubmitAnswerRequest,
    StartExamResponse,
    SubmitAnswerResponse,
    ResultsResponse,
    QuestionResponse,
    AnswerFeedback
)

router = APIRouter(prefix="/exam", tags=["Optimized Adaptive Exam"])


@router.get("/start", response_model=StartExamResponse)
def start_exam(db: Session = Depends(get_db)):
    """
    Start exam - GET request, no parameters needed.
    Questions fixed at 40, session auto-created.
    
    """
    
    exam_service = ExamService(db)
    
    try:
        # Fixed at 40 questions, no user_id
        result = exam_service.start_exam_with_first_question(
            user_id=None,
            n_questions=40  # Fixed
        )
        
        # Simplified response - just session_id and question
        return StartExamResponse(
            session_id=result['session']['session_id'],
            question=QuestionResponse(
                unique_id=result['question']['unique_id'],
                question_text=result['question']['question_text'],
                options=result['question']['options'],
                image_url=result['question']['image_url'],
                question_type=result['question']['question_type']
            )
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start exam: {str(e)}"
        )


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit answer and get next question.
    During the exam, theta estimates are not returned to avoid confusion.
    Only final results will include ability estimates.  
    """
    exam_service = ExamService(db)
    
    try:
        result = exam_service.submit_answer_and_get_next(
            session_id=request.session_id,
            user_answer=request.user_answer
        )
        
        # Simplified feedback - no theta during exam
        feedback = AnswerFeedback(
            is_correct=result['feedback']['is_correct'],
            correct_answer=result['feedback']['correct_answer'],
            question_num=result['feedback']['question_num']
            # Removed: theta_math, theta_tech, total_questions
        )
        
        # Next question (if any)
        next_question = None
        if result.get('next_question'):
            next_question = QuestionResponse(
                unique_id=result['next_question']['unique_id'],
                question_text=result['next_question']['question_text'],
                options=result['next_question']['options'],
                image_url=result['next_question']['image_url'],
                question_type=result['next_question']['question_type']
            )
        
        return SubmitAnswerResponse(
            feedback=feedback,
            next_question=next_question,
            exam_completed=result['exam_completed']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get("/results/{session_id}", response_model=ResultsResponse)
def get_results(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get final results for a completed exam session.
    """
    exam_service = ExamService(db)
    
    try:
        results = exam_service.get_results(session_id)
        return ResultsResponse(**results)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get results: {str(e)}"
        )