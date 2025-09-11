# backend/app/routes/responses_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ResponseOut, status_code=status.HTTP_201_CREATED)
def create_response(response: schemas.ResponseCreate, db: Session = Depends(get_db)) -> schemas.ResponseOut:
    db_response = models.Response(**response.model_dump())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return schemas.ResponseOut.model_validate(db_response)

# Optional: Add GET endpoints if needed
@router.get("/", response_model=List[schemas.ResponseOut])
def get_responses(db: Session = Depends(get_db)) -> List[schemas.ResponseOut]:
    responses = db.query(models.Response).all()
    return [schemas.ResponseOut.model_validate(response) for response in responses]

@router.get("/{response_id}", response_model=schemas.ResponseOut)
def get_response(response_id: int, db: Session = Depends(get_db)) -> schemas.ResponseOut:
    response = db.query(models.Response).filter(models.Response.response_id == response_id).first()
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Response not found")
    return schemas.ResponseOut.model_validate(response)