# backend/app/routes/test_sessions_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=schemas.TestSessionOut, status_code=status.HTTP_201_CREATED)
def create_test_session(session: schemas.TestSessionCreate, db: Session = Depends(get_db)) -> schemas.TestSessionOut:
    db_session = models.TestSession(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return schemas.TestSessionOut.model_validate(db_session)

# Optional: Add GET endpoints if needed
@router.get("/", response_model=List[schemas.TestSessionOut])
def get_test_sessions(db: Session = Depends(get_db)) -> List[schemas.TestSessionOut]:
    sessions = db.query(models.TestSession).all()
    return [schemas.TestSessionOut.model_validate(session) for session in sessions]

@router.get("/{session_id}", response_model=schemas.TestSessionOut)
def get_test_session(session_id: int, db: Session = Depends(get_db)) -> schemas.TestSessionOut:
    session = db.query(models.TestSession).filter(models.TestSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test session not found")
    return schemas.TestSessionOut.model_validate(session)