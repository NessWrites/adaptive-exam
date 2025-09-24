# backend/app/routes/submissions_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SubmissionOut, status_code=status.HTTP_201_CREATED)
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)) -> schemas.SubmissionOut:
    db_submission = models.Submission(**submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return schemas.SubmissionOut.model_validate(db_submission)

# Optional: Add GET endpoints if needed
@router.get("/", response_model=List[schemas.SubmissionOut])
def get_submissions(db: Session = Depends(get_db)) -> List[schemas.SubmissionOut]:
    submissions = db.query(models.Submission).all()
    return [schemas.SubmissionOut.model_validate(submission) for submission in submissions]

@router.get("/{submission_id}", response_model=schemas.SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> schemas.SubmissionOut:
    submission = db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return schemas.SubmissionOut.model_validate(submission)