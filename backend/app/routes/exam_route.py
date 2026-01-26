from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.postgresql.connection import get_db
from backend.app.services.exam_service import ExamService
from backend.app.schemas.exam_schema import (
    SessionCreateRequest,
    AnswerSubmitRequest,
    StartExamResponse,
    SubmitAnswerResponse,
    ResultsResponse
)

router = APIRouter(prefix="/exam", tags=["Adaptive Exam"])


@router.post("/start", response_model=StartExamResponse, status_code=status.HTTP_201_CREATED)
async def start_exam(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new adaptive exam session and get the first question.
    
    - **user_id**: Optional identifier for the user
    - **n_questions**: Number of adaptive questions (default: 40)
    
    Returns session information, initial ability estimates, and the first question.
    """
    exam_service = ExamService(db)
    
    try:
        result = exam_service.start_exam_with_first_question(
            user_id=request.user_id,
            n_questions=request.n_questions
        )
        
        return StartExamResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start exam: {str(e)}"
        )


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit answer for the current question.
    
    - **session_id**: Exam session ID
    - **user_answer**: User's answer (single letter or list of letters)
    
    Returns feedback with correctness, updated ability estimates, and the next question.
    If exam is complete, returns completion status instead of next question.
    """
    exam_service = ExamService(db)
    
    try:
        result = exam_service.submit_answer_and_get_next(
            session_id=request.session_id,
            user_answer=request.user_answer
        )
        
        return SubmitAnswerResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get("/results/{session_id}", response_model=ResultsResponse)
async def get_results(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get final exam results and ability estimates.
    
    Returns detailed results including accuracy, ability estimates, and interpretations.
    Only available after exam is completed.
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
