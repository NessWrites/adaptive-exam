# backend/app/routes/students_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)) -> schemas.StudentOut:
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return schemas.StudentOut.model_validate(db_student)

@router.get("/", response_model=List[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)) -> List[schemas.StudentOut]:
    students = db.query(models.Student).all()
    return [schemas.StudentOut.model_validate(student) for student in students]

@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)) -> schemas.StudentOut:
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return schemas.StudentOut.model_validate(student)