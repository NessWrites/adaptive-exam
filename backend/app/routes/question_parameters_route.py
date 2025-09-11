from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db
from ..services.irt_utils import fetch_data_for_bayesian_analysis, get_db_connection_params
from ..database.postgresql.connection import DatabaseManager

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Bayesian IRT model, fallback if not available
try:
    from ai_models.bayesian_irt import run_hierarchical_3pl_model
    BAYESIAN_IRT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Bayesian IRT dependencies not available: {e}")
    BAYESIAN_IRT_AVAILABLE = False
    run_hierarchical_3pl_model = None

router = APIRouter()

@router.post("/", response_model=schemas.QuestionParameterOut, status_code=status.HTTP_201_CREATED)
def create_question_parameter(param: schemas.QuestionParameterCreate, db: Session = Depends(get_db)) -> schemas.QuestionParameterOut:
    db_param = models.QuestionParameter(**param.model_dump())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return schemas.QuestionParameterOut.model_validate(db_param)

@router.get("/", response_model=List[schemas.QuestionParameterOut])
def get_question_parameters(db: Session = Depends(get_db)) -> List[schemas.QuestionParameterOut]:
    params = db.query(models.QuestionParameter).all()
    return [schemas.QuestionParameterOut.model_validate(param) for param in params]

@router.get("/summary", response_model=List[schemas.QuestionParameterSummaryOut])
def get_question_parameters_summary(db: Session = Depends(get_db)) -> List[schemas.QuestionParameterSummaryOut]:
    """
    Lightweight list of question parameters without heavy parameter_samples to avoid large payloads.
    """
    params = db.query(models.QuestionParameter).all()
    return [schemas.QuestionParameterSummaryOut.model_validate(param) for param in params]

@router.get("/{param_id}", response_model=schemas.QuestionParameterOut)
def get_question_parameter(param_id: int, db: Session = Depends(get_db)) -> schemas.QuestionParameterOut:
    param = db.query(models.QuestionParameter).filter(models.QuestionParameter.param_id == param_id).first()
    if not param:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question parameter not found")
    return schemas.QuestionParameterOut.model_validate(param)

@router.put("/{param_id}", response_model=schemas.QuestionParameterOut)
def update_question_parameter(
    param_id: int,
    updated_param: schemas.QuestionParameterUpdate,
    db: Session = Depends(get_db)
):
    db_param = db.query(models.QuestionParameter).filter(models.QuestionParameter.param_id == param_id).first()
    if not db_param:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question parameter not found")

    update_data = updated_param.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_param, key, value)

    db.commit()
    db.refresh(db_param)
    return schemas.QuestionParameterOut.model_validate(db_param)

@router.api_route("/update-from-bayesian-irt", methods=["POST", "GET"], response_model=List[schemas.QuestionParameterOut])
async def update_question_parameters_from_bayesian_irt(db: Session = Depends(get_db)):
    """
    Run Bayesian IRT model and update question parameters in the database.
    """
    if not BAYESIAN_IRT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bayesian IRT analysis not available. Please install required dependencies: pip install pymc arviz aesara pytensor"
        )
    
    try:
        # Initialize database manager
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()

        # Fetch data for Bayesian analysis
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        if not bayesian_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No response data available for Bayesian IRT analysis")

        # Run the Bayesian IRT model
        irt_results = run_hierarchical_3pl_model(bayesian_data)
        if not irt_results["analysis_completed"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bayesian IRT analysis failed")

        # Extract question parameters
        question_params = irt_results["question_parameters"]
        # Map model question index j -> actual question_id using df_long from bayesian_data
        df_long = bayesian_data["df_long"]
        j_to_question_id = (
            df_long.groupby("j")["question"].first().sort_index()
        )

        updated_params = []
        for j in range(irt_results["n_questions"]):
            # Get question_id from mapping; skip if missing (shouldn't happen if data aligned)
            question_id = j_to_question_id.get(j) if hasattr(j_to_question_id, "get") else j_to_question_id.loc[j]
            if not question_id:
                logger.warning(f"No question ID found for index {j}")
                continue

            # Check if question parameter exists
            db_param = db.query(models.QuestionParameter).filter(
                models.QuestionParameter.question_id == question_id
            ).first()

            param_data = {
                "question_id": question_id,
                "parameter_a_mean": question_params["a_means"][j],
                "parameter_a_std": question_params["a_stds"][j],
                "parameter_b_mean": question_params["b_means"][j],
                "parameter_b_std": question_params["b_stds"][j],
                "parameter_c_mean": question_params["c_means"][j],
                "parameter_c_std": question_params["c_stds"][j],
                "model_version": "bayesian_irt_v1",
                "estimation_method": "mcmc",
                "n_samples": 1500,
                "convergence_diagnostics": {"max_rhat": irt_results["max_rhat"]}
            }

            if db_param:
                # Update existing record
                for key, value in param_data.items():
                    setattr(db_param, key, value)
            else:
                # Create new record
                db_param = models.QuestionParameter(**param_data)
                db.add(db_param)

            updated_params.append(db_param)

            # Also update the main Questions table with latest a/b/c means
            db_question = db.query(models.Question).filter(models.Question.question_id == str(question_id)).first()
            if db_question:
                db_question.parameter_a = param_data["parameter_a_mean"]
                db_question.parameter_b = param_data["parameter_b_mean"]
                db_question.parameter_c = param_data["parameter_c_mean"]

        db.commit()
        for param in updated_params:
            db.refresh(param)

        db_manager.close()
        return [schemas.QuestionParameterOut.model_validate(param) for param in updated_params]

    except Exception as e:
        logger.error(f"Failed to update question parameters: {e}")
        db_manager.close()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))