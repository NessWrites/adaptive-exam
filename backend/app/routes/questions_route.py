from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..database.postgresql.connection import SessionLocal

router = APIRouter(prefix="/questions", tags=["questions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.QuestionOut)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    db_question = models.Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/", response_model=list[schemas.QuestionOut])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    return questions

@router.get("/{question_id}", response_model=schemas.QuestionOut)
def get_question(question_id: str, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question