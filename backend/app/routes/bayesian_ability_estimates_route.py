# backend/app/routes/bayesian_ability_estimates_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=schemas.BayesianAbilityEstimateOut, status_code=status.HTTP_201_CREATED)
def create_bayesian_ability_estimate(estimate: schemas.BayesianAbilityEstimateCreate, db: Session = Depends(get_db)) -> schemas.BayesianAbilityEstimateOut:
    db_estimate = models.BayesianAbilityEstimate(**estimate.model_dump())
    db.add(db_estimate)
    db.commit()
    db.refresh(db_estimate)
    return schemas.BayesianAbilityEstimateOut.model_validate(db_estimate)

# Optional: Add GET endpoints if needed
@router.get("/", response_model=List[schemas.BayesianAbilityEstimateOut])
def get_bayesian_ability_estimates(db: Session = Depends(get_db)) -> List[schemas.BayesianAbilityEstimateOut]:
    estimates = db.query(models.BayesianAbilityEstimate).all()
    return [schemas.BayesianAbilityEstimateOut.model_validate(estimate) for estimate in estimates]

@router.get("/{estimate_id}", response_model=schemas.BayesianAbilityEstimateOut)
def get_bayesian_ability_estimate(estimate_id: int, db: Session = Depends(get_db)) -> schemas.BayesianAbilityEstimateOut:
    estimate = db.query(models.BayesianAbilityEstimate).filter(models.BayesianAbilityEstimate.estimate_id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bayesian ability estimate not found")
    return schemas.BayesianAbilityEstimateOut.model_validate(estimate)