from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.services.session import session_manager

router = APIRouter(tags=["health"])

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "endpoints": {
            "POST /exam/start": "Start a new exam session",
            "POST /exam/next": "Get the next question",
            "POST /exam/submit": "Submit an answer",
            "GET /exam/results/{session_id}": "Get final results",
            "DELETE /exam/session/{session_id}": "Delete a session",
            "GET /health": "Health check"
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_session_count()
    }