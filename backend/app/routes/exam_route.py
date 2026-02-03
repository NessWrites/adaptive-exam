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
            n_questions=50  # 40 operational + 10 pretest = 50 total
        )
        
        # result = {
        #     'session': <ExamSession object>,
        #     'question': <Question object>
        # }
        
        # Extract session (it's an ORM object, not a dict)
        session = result['session']
        question = result['question']
        
        
        return StartExamResponse(
            session_id=session.session_id,  
            question=QuestionResponse(
                unique_id=question.unique_id,
                question_text=question.question_text,
                options=question.options,
                image_url=question.image_url,
                question_type=question.question_type
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
        
        # result = {
        #     'feedback': dict,
        #     'next_question': <Question object> or None,
        #     'exam_completed': bool
        # }
        
        # Build feedback (feedback is already a dict)
        feedback = AnswerFeedback(
            is_correct=result['feedback']['is_correct'],
            correct_answer=result['feedback']['correct_answer'],
            question_num=result['feedback']['question_num']
        )
        
        # Build next question if exists (it's an ORM object)
        next_question = None
        if result.get('next_question'):
            q = result['next_question']
            next_question = QuestionResponse(
                unique_id=q.unique_id,
                question_text=q.question_text,
                options=q.options,
                image_url=q.image_url,
                question_type=q.question_type
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
        # results is already a dict with the correct structure
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