import uuid
from typing import Dict, Optional
from backend.app.services.mirt_cat import MIRT_CAT_Exam
from backend.app.core.exception import SessionNotFoundException

class SessionManager:
    """Manages exam sessions in memory."""
    
    def __init__(self):
        self._sessions: Dict[str, MIRT_CAT_Exam] = {}
    
    def create_session(self, item_bank_path: str, min_items: int, 
                      max_items: int, target_se: float) -> tuple[str, MIRT_CAT_Exam]:
        """Create a new exam session."""
        session_id = str(uuid.uuid4())
        exam = MIRT_CAT_Exam(
            item_bank_path=item_bank_path,
            min_items=min_items,
            max_items=max_items,
            target_se=target_se
        )
        self._sessions[session_id] = exam
        return session_id, exam
    
    def get_session(self, session_id: str) -> MIRT_CAT_Exam:
        """Get an exam session by ID."""
        if session_id not in self._sessions:
            raise SessionNotFoundException(session_id)
        return self._sessions[session_id]
    
    def delete_session(self, session_id: str) -> None:
        """Delete an exam session."""
        if session_id not in self._sessions:
            raise SessionNotFoundException(session_id)
        del self._sessions[session_id]
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in self._sessions
    
    def get_session_count(self) -> int:
        """Get the total number of active sessions."""
        return len(self._sessions)

# Global session manager instance
session_manager = SessionManager()