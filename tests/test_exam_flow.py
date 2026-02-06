from unittest.mock import MagicMock
from backend.app.services.exam_service import ExamService
from backend.app.models.database_models import ExamSession, Question, Response

def test_full_exam_cycle_mocked(mock_qpool, mocker):
    """
    Simulates a user starting an exam and submitting an answer 
    WITHOUT needing a real database or LLM.
    """
    
    # 1. Mock the Database Session
    mock_db = MagicMock()
    
    # --- FIX 1: Add status="in_progress" and missing theta_se fields ---
    mock_session = ExamSession(
        session_id=123, 
        current_question_num=0, 
        n_questions=50,
        math_count=0, 
        tech_count=0,
        theta_math=0.0,
        theta_tech=0.0,
        theta_se_math=1.0,  
        theta_se_tech=1.0,  
        status="in_progress" # <--- FIXED: Prevents ValueError
    )
    # -----------------------------------------------------

    # --- UPDATE: More realistic question with 4 options ---
    mock_question = Question(
        unique_id=1, 
        question_text="Which of the following is a transactional database property?", 
        correct_answer="A",  # Corresponds to index 0 ('Atomicity')
        options=[
            "Atomicity",      # A
            "Scalability",    # B
            "Latency",        # C
            "Throughput"      # D
        ],
        a_values=[1.0, 0.0],
        b_value=0.0,
        calibration_status='operational',
        domain='tech'
    )
    
    # Setup Service with mocked DB
    service = ExamService(mock_db)
    
    # Mock specific DB queries used in start_exam
    mocker.patch.object(service, 'create_session', return_value=mock_session)
    mocker.patch.object(service, 'select_next_question', return_value=mock_question)
    
    # --- ACTION 1: START EXAM ---
    result = service.start_exam_with_first_question()
    
    assert result['session'].session_id == 123
    assert result['question'].unique_id == 1
    # Verify we have 4 options now
    assert len(result['question'].options) == 4 
    
    # --- ACTION 2: SUBMIT ANSWER ---
    # Mock finding the session 
    mocker.patch.object(service, 'get_session', return_value=mock_session)
    
    # Mock finding the open response
    mock_response_obj = Response(response_id=5, question_id=1)
    
    # Complex mocking for the chain: db.query().filter().order_by().first()
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_response_obj
    
    # Mock question lookup 
    def query_side_effect(*args):
        query_mock = MagicMock()
        
        # Case 1: db.query(Question)
        if len(args) == 1 and args[0] == Question:
            # FIX 2: Mock filter().first() used in submit_answer_and_get_next
            query_mock.filter.return_value.first.return_value = mock_question
            query_mock.get.return_value = mock_question
            
        # Case 2: db.query(Response)
        elif len(args) == 1 and args[0] == Response:
            # For response lookup
            query_mock.filter.return_value.order_by.return_value.first.return_value = mock_response_obj
            # For response counting (in get_results or checks)
            query_mock.join.return_value.filter.return_value.count.return_value = 0
            query_mock.filter.return_value.count.return_value = 0
            
        # Case 3: db.query(Response, Question) - Used in update_theta
        elif len(args) == 2 and args[0] == Response and args[1] == Question:
            query_mock.join.return_value.filter.return_value.all.return_value = []
            
        return query_mock

    mock_db.query.side_effect = query_side_effect
    
    # Perform submission
    # User submits "A", which matches correct_answer "A" in the mock_question
    submit_result = service.submit_answer_and_get_next(session_id=123, user_answer="A")
    
    assert submit_result['feedback']['is_correct'] is True
    assert submit_result['exam_completed'] is False