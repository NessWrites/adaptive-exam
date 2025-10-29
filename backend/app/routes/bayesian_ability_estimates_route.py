# backend/app/routes/bayesian_ability_estimates_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from pymc.data import np
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from ai_models.bayesian_irt import lite_hierarchical_3pl_model, run_hierarchical_2pl_model
from ai_models.bayesian_irt import run_hierarchical_2pl_model_improved, run_simple_2pl_model, run_adaptive_2pl_model
from backend.app.services.irt_utils import check_sparse_matrix_stats, prepare_bayesian_irt_data, prepare_lite_bayesian_irt_data, validate_data_for_2pl

import logging
import warnings

# Suppress Pydantic protected namespaces warning
warnings.filterwarnings("ignore", message=".*protected_namespaces.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# SPECIFIC ROUTES MUST COME FIRST (before parameterized routes like /{estimate_id})
# ============================================================================

@router.get("/preview-preprocessing")
async def preview_preprocessing(db: Session = Depends(get_db)):
    """
    Preview the effects of preprocessing without running the full model
    """
    try:
        stats = check_sparse_matrix_stats(db, apply_preprocessing=True)
        
        # Add detailed comparison
        if 'preprocessing_preview' in stats and 'filtering_applied' in stats['preprocessing_preview']:
            filtering = stats['preprocessing_preview']['filtering_applied']
            
            comparison = {
                'original_data': {
                    'students': stats['n_students'],
                    'questions': stats['n_questions'],
                    'sparsity': stats['sparsity_percentage']
                },
                'after_preprocessing': {
                    'students': filtering.get('final_students', stats['n_students']),
                    'questions': filtering.get('final_questions', stats['n_questions']),
                    'sparsity': filtering.get('sparsity_after', stats['sparsity_percentage'])
                },
                'filtering_summary': filtering,
                'data_quality_assessment': {
                    'original_quality': 'ideal' if stats['is_ideal_for_irt'] else 'suitable' if stats['is_suitable_for_irt'] else 'caution' if stats['can_proceed_with_caution'] else 'poor',
                    'recommended_model': 'hierarchical_2pl' if stats['is_suitable_for_irt'] else 'simple_2pl',
                    'stability_outlook': 'excellent' if stats['is_ideal_for_irt'] else 'good' if stats['is_suitable_for_irt'] else 'moderate' if stats['can_proceed_with_caution'] else 'poor'
                }
            }
            
            return comparison
        else:
            return stats
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview preprocessing: {str(e)}"
        )

@router.get("/preview-adaptive-model-selection") 
async def preview_adaptive_model_selection(db: Session = Depends(get_db)):
    """Preview which model the adaptive 2PL would select based on current data"""
    try:
        stats = check_sparse_matrix_stats(db, apply_preprocessing=True)
        bayesian_data = prepare_lite_bayesian_irt_data(db)
        
        response_matrix = bayesian_data['response_matrix']
        n_students, n_questions = response_matrix.shape
        observed_responses = np.sum(~np.isnan(response_matrix))
        sparsity = 1 - (observed_responses / (n_students * n_questions))
        
        # Apply same decision logic as adaptive model
        use_hierarchical = (
            n_students >= 100 and 
            n_questions >= 30 and 
            sparsity < 0.8 and
            observed_responses > 1000
        )
        
        recommendation = {
            'data_characteristics': {
                'students': n_students,
                'questions': n_questions,
                'observed_responses': int(observed_responses),
                'sparsity_percentage': float(sparsity * 100),
                'data_quality': stats['data_quality']
            },
            'model_selection': {
                'recommended_model': 'hierarchical_2pl' if use_hierarchical else 'simple_2pl',
                'reasoning': {
                    'sufficient_students': n_students >= 100,
                    'sufficient_questions': n_questions >= 30,
                    'acceptable_sparsity': sparsity < 0.8,
                    'sufficient_observations': observed_responses > 1000
                }
            },
            'expected_stability': 'high' if use_hierarchical and stats['data_quality'] in ['ideal', 'suitable'] else 'moderate' if not use_hierarchical else 'low'
        }
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.get("/preview-relaxed-preprocessing")
async def preview_relaxed_preprocessing(db: Session = Depends(get_db)):
    """
    Preview preprocessing with more relaxed criteria to retain more data
    """
    try:
        # Test different levels of filtering strictness
        filtering_levels = {
            'strict': {
                'min_responses_per_student': 3,
                'min_responses_per_question': 3,
                'min_question_difficulty': 0.05,
                'max_question_difficulty': 0.95,
                'min_student_ability': 0.05,
                'max_student_ability': 0.95
            },
            'moderate': {
                'min_responses_per_student': 2,
                'min_responses_per_question': 2,
                'min_question_difficulty': 0.01,
                'max_question_difficulty': 0.99,
                'min_student_ability': 0.01,
                'max_student_ability': 0.99
            },
            'relaxed': {
                'min_responses_per_student': 1,
                'min_responses_per_question': 1,
                'min_question_difficulty': float('-inf'),  # No filtering on question difficulty
                'max_question_difficulty': float('inf'),   # No filtering on question difficulty
                'min_student_ability': 0.001,
                'max_student_ability': 0.999
            }
        }
        
        from backend.app.services.irt_utils import preprocess_for_stable_irt
        
        # Get original data
        responses = db.query(
            models.Response.student_id,
            models.Response.question_id,
            models.Response.is_correct
        ).all()
        
        if not responses:
            raise HTTPException(status_code=400, detail="No response data found")
        
        # Build original response matrix
        student_ids = sorted(set([r.student_id for r in responses]))
        question_ids = sorted(set([r.question_id for r in responses]))
        
        student_id_to_idx = {id: idx for idx, id in enumerate(student_ids)}
        question_id_to_idx = {id: idx for idx, id in enumerate(question_ids)}
        
        response_matrix = np.full((len(student_ids), len(question_ids)), np.nan)
        
        for response in responses:
            student_idx = student_id_to_idx[response.student_id]
            question_idx = question_id_to_idx[response.question_id]
            response_matrix[student_idx, question_idx] = response.is_correct
        
        # Test each filtering level
        results = {'original': {
            'students': len(student_ids),
            'questions': len(question_ids),
            'sparsity': float((1 - np.sum(~np.isnan(response_matrix)) / (len(student_ids) * len(question_ids))) * 100)
        }}
        
        for level, params in filtering_levels.items():
            try:
                filtered_data = preprocess_for_stable_irt(
                    response_matrix.copy(),
                    student_ids.copy(),
                    question_ids.copy(),
                    **params
                )
                
                results[level] = {
                    'students': filtered_data['n_students'],
                    'questions': filtered_data['n_questions'],
                    'sparsity': filtered_data['filtering_stats']['sparsity_after'],
                    'filtering_stats': filtered_data['filtering_stats'],
                    'suitable_for_irt': (
                        filtered_data['n_students'] >= 30 and 
                        filtered_data['n_questions'] >= 15
                    )
                }
                
            except Exception as e:
                results[level] = {'error': str(e)}
        
        # Recommend best level
        recommendation = 'strict'
        for level in ['relaxed', 'moderate', 'strict']:
            if level in results and 'suitable_for_irt' in results[level]:
                if results[level]['suitable_for_irt']:
                    recommendation = level
                    break
        
        return {
            'filtering_comparison': results,
            'recommendation': recommendation,
            'recommended_params': filtering_levels[recommendation] if recommendation in filtering_levels else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.post("/compute-2pl", response_model=List[schemas.BayesianAbilityEstimateOut])
async def compute_bayesian_ability_estimates_2pl(
    db: Session = Depends(get_db),
    use_simple_model: bool = False,
    apply_strict_filtering: bool = True
):
    """
    Compute ability estimates using 2PL model with enhanced stability preprocessing
    
    Args:
        db: Database session
        use_simple_model: If True, use simple 2PL without hierarchy (more stable)
        apply_strict_filtering: If True, apply strict data filtering for stability
    """
    try:
        # Enhanced data statistics check
        stats = check_sparse_matrix_stats(db, apply_preprocessing=True)
        
        # Log preprocessing preview
        if 'preprocessing_preview' in stats and stats['preprocessing_preview']:
            pp_stats = stats['preprocessing_preview']
            if 'error' not in pp_stats:
                logger.info(f"Preprocessing preview: {pp_stats['preprocessed_students']} students, "
                          f"{pp_stats['preprocessed_questions']} questions after filtering")
                logger.info(f"Filtering stats: {pp_stats.get('filtering_applied', {})}")
        
        # Enhanced suitability check
        if not stats['can_proceed_with_caution']:
            raise HTTPException(
                status_code=400, 
                detail=f"Data not suitable for IRT after preprocessing. "
                      f"Data quality: {stats['data_quality']}. "
                      f"Consider collecting more data or relaxing quality thresholds."
            )
        
        # Issue warnings for marginal data quality
        if stats['data_quality'] == 'caution':
            logger.warning(f"Proceeding with caution - data quality: {stats['data_quality']}")
            logger.warning("Results may be less reliable due to limited data")
        elif stats['data_quality'] == 'poor':
            logger.warning("Data quality is poor - strongly recommend collecting more data")
        
        # Prepare data with enhanced preprocessing
        bayesian_data = prepare_lite_bayesian_irt_data(db)
        
        # Additional validation for 2PL stability
        validation = validate_data_for_2pl(bayesian_data['response_matrix'])
        if validation['warnings']:
            logger.warning(f"Data validation warnings: {validation['warnings']}")
        
        # Run the appropriate 2PL model based on parameters
        if use_simple_model:
            logger.info("Using simple 2PL model")
            results = run_simple_2pl_model(bayesian_data)
        else:
            logger.info("Using adaptive 2PL model")
            results = run_adaptive_2pl_model(bayesian_data)
        
        model_used = results.get('model_used', 'unknown')
        logger.info(f"Model used: {model_used}")
        
        # Validate results
        if 'theta_estimates' not in results:
            raise HTTPException(
                status_code=500,
                detail="Model failed to produce theta estimates"
            )
        
        theta_estimates = results["theta_estimates"]
        theta_stds = results.get("theta_stds", [0.1] * len(theta_estimates))
        
        # Check for issues
        if np.any(np.isnan(theta_estimates)) or np.any(np.isinf(theta_estimates)):
            raise HTTPException(
                status_code=500,
                detail="Numerical instability in ability estimates"
            )
        
        # Report model quality
        divergences = results.get('divergences', 0)
        convergence_quality = results.get('convergence_quality', 'unknown')
        
        if divergences == 0:
            logger.info("✅ Perfect convergence - no divergences!")
        elif divergences < 10:
            logger.info(f"✅ Excellent convergence - only {divergences} divergences")
        elif divergences < 50:
            logger.warning(f"⚠️ Acceptable convergence - {divergences} divergences")
        else:
            logger.warning(f"⚠️ Poor convergence - {divergences} divergences")
        
        # Clear existing estimates and store new ones
        db.query(models.BayesianAbilityEstimate).delete()
        
        estimates_created = 0
        for student_id, theta, std in zip(bayesian_data['student_ids'], theta_estimates, theta_stds):
            try:
                # Ensure finite values with reasonable bounds
                theta_val = float(np.clip(theta, -5.0, 5.0)) if np.isfinite(theta) else 0.0
                std_val = float(np.clip(std, 0.01, 3.0)) if np.isfinite(std) and std > 0 else 0.1
                
                db_estimate = models.BayesianAbilityEstimate(
                    student_id=student_id,
                    theta_mean=theta_val,
                    theta_std=std_val
                )
                db.add(db_estimate)
                estimates_created += 1
                
            except Exception as e:
                logger.error(f"Failed to store estimate for student {student_id}: {e}")
                continue
        
        if estimates_created == 0:
            raise HTTPException(status_code=500, detail="No valid estimates could be created")
        
        logger.info(f"✅ Successfully created {estimates_created} ability estimates using {model_used}")
        
        # Update question parameters in the Questions table if available
        parameters_updated = 0
        if 'difficulty_estimates' in results and 'discrimination_estimates' in results:
            difficulty_estimates = results['difficulty_estimates']
            discrimination_estimates = results['discrimination_estimates']
            
            logger.info(f"Updating 2PL question parameters for {len(bayesian_data['question_ids'])} questions")
            
            for i, question_id in enumerate(bayesian_data['question_ids']):
                try:
                    # Get parameter estimates (clip to reasonable ranges)
                    a_val = float(np.clip(discrimination_estimates[i], 0.01, 5.0)) if np.isfinite(discrimination_estimates[i]) else 1.0
                    b_val = float(np.clip(difficulty_estimates[i], -5.0, 5.0)) if np.isfinite(difficulty_estimates[i]) else 0.0
                    
                    # Update the Questions table with 2PL parameters
                    db_question = db.query(models.Question).filter(
                        models.Question.question_id == question_id
                    ).first()
                    
                    if db_question:
                        db_question.parameter_a_2pl = a_val
                        db_question.parameter_b_2pl = b_val
                        db_question.updated_at = func.now()
                        logger.info(f"Updated Question {question_id}: a_2pl={a_val:.3f}, b_2pl={b_val:.3f}")
                        parameters_updated += 1
                    else:
                        logger.warning(f"Question {question_id} not found in Questions table")
                    
                except Exception as e:
                    logger.error(f"Failed to update parameters for question {question_id}: {e}")
                    continue
            
            logger.info(f"Updated {parameters_updated} question parameters")
        else:
            logger.warning("No question parameters found in 2PL model results")
        
        db.commit()
        
        # Return results
        estimates = db.query(models.BayesianAbilityEstimate).all()
        result_list = [schemas.BayesianAbilityEstimateOut.model_validate(estimate) for estimate in estimates]
        
        # Log summary statistics
        theta_vals = [est.theta_mean for est in result_list]
        logger.info(f"📈 Estimate summary - Mean: {np.mean(theta_vals):.3f}, "
                   f"Std: {np.std(theta_vals):.3f}, Range: [{np.min(theta_vals):.3f}, {np.max(theta_vals):.3f}]")
        
        return result_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Adaptive 2PL model failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Adaptive 2PL failed: {str(e)}")

@router.post("/compute-adaptive-2pl-relaxed", response_model=List[schemas.BayesianAbilityEstimateOut])
async def compute_adaptive_2pl_with_relaxed_preprocessing(
    db: Session = Depends(get_db),
    filtering_level: str = "moderate"  # strict, moderate, or relaxed
):
    """
    Compute adaptive 2PL with configurable preprocessing strictness
    
    Args:
        filtering_level: 'strict', 'moderate', or 'relaxed' preprocessing
    """
    try:
        # Define filtering parameters
        filtering_params = {
            'strict': {
                'min_responses_per_student': 3,
                'min_responses_per_question': 3,
                'min_question_difficulty': 0.05,
                'max_question_difficulty': 0.95,
                'min_student_ability': 0.05,
                'max_student_ability': 0.95
            },
            'moderate': {
                'min_responses_per_student': 2,
                'min_responses_per_question': 2,
                'min_question_difficulty': 0.01,
                'max_question_difficulty': 0.99,
                'min_student_ability': 0.01,
                'max_student_ability': 0.99
            },
            'relaxed': {
                'min_responses_per_student': 1,
                'min_responses_per_question': 1,
                'min_question_difficulty': float('-inf'),  # No filtering on question difficulty
                'max_question_difficulty': float('inf'),   # No filtering on question difficulty
                'min_student_ability': 0.001,
                'max_student_ability': 0.999
            }
        }
        
        if filtering_level not in filtering_params:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filtering_level. Choose from: {list(filtering_params.keys())}"
            )
        
        logger.info(f"Using {filtering_level} preprocessing")
        
        # Custom preprocessing with selected parameters
        responses = db.query(
            models.Response.student_id,
            models.Response.question_id,
            models.Response.is_correct
        ).all()
        
        if not responses:
            raise HTTPException(status_code=400, detail="No response data found")
        
        # Build response matrix
        student_ids = sorted(set([r.student_id for r in responses]))
        question_ids = sorted(set([r.question_id for r in responses]))
        
        student_id_to_idx = {id: idx for idx, id in enumerate(student_ids)}
        question_id_to_idx = {id: idx for idx, id in enumerate(question_ids)}
        
        response_matrix = np.full((len(student_ids), len(question_ids)), np.nan)
        
        for response in responses:
            student_idx = student_id_to_idx[response.student_id]
            question_idx = question_id_to_idx[response.question_id]
            response_matrix[student_idx, question_idx] = response.is_correct
        
        logger.info(f"Original data: {len(student_ids)} students, {len(question_ids)} questions")
        
        # Apply selected preprocessing
        from backend.app.services.irt_utils import preprocess_for_stable_irt
        
        stable_data = preprocess_for_stable_irt(
            response_matrix,
            student_ids,
            question_ids,
            **filtering_params[filtering_level]
        )
        
        logger.info(f"After {filtering_level} filtering: {stable_data['n_students']} students, {stable_data['n_questions']} questions")
        
        # Check minimum requirements
        if stable_data['n_students'] < 20 or stable_data['n_questions'] < 10:
            raise HTTPException(
                status_code=400,
                detail=f"After {filtering_level} preprocessing: {stable_data['n_students']} students, "
                      f"{stable_data['n_questions']} questions. Need at least 20 students and 10 questions. "
                      f"Try a more relaxed filtering level."
            )
        
        # Prepare bayesian data format
        bayesian_data = {
            'response_matrix': stable_data['response_matrix'],
            'student_ids': stable_data['student_ids'],
            'question_ids': stable_data['question_ids'],
            'n_students': stable_data['n_students'],
            'n_questions': stable_data['n_questions']
        }
        
        # Run adaptive 2PL
        logger.info("Running adaptive 2PL with relaxed preprocessing")
        results = run_adaptive_2pl_model(bayesian_data)
        
        model_used = results.get('model_used', 'unknown')
        logger.info(f"Model used: {model_used}")
        
        # Validate results
        if 'theta_estimates' not in results:
            raise HTTPException(
                status_code=500,
                detail="Model failed to produce theta estimates"
            )
        
        theta_estimates = results["theta_estimates"]
        theta_stds = results.get("theta_stds", [0.1] * len(theta_estimates))
        
        # Check for issues
        if np.any(np.isnan(theta_estimates)) or np.any(np.isinf(theta_estimates)):
            raise HTTPException(
                status_code=500,
                detail="Numerical issues in estimates"
            )
        
        # Report convergence
        divergences = results.get('divergences', 0)
        if divergences == 0:
            logger.info("Perfect convergence!")
        elif divergences < 20:
            logger.info(f"Good convergence with {divergences} divergences")
        else:
            logger.warning(f"Convergence issues: {divergences} divergences")
        
        # Store results
        db.query(models.BayesianAbilityEstimate).delete()
        
        estimates_created = 0
        for student_id, theta, std in zip(bayesian_data['student_ids'], theta_estimates, theta_stds):
            try:
                theta_val = float(np.clip(theta, -6.0, 6.0)) if np.isfinite(theta) else 0.0
                std_val = float(np.clip(std, 0.01, 4.0)) if np.isfinite(std) and std > 0 else 0.1
                
                db_estimate = models.BayesianAbilityEstimate(
                    student_id=student_id,
                    theta_mean=theta_val,
                    theta_std=std_val
                )
                db.add(db_estimate)
                estimates_created += 1
                
            except Exception as e:
                logger.error(f"Failed to store estimate for student {student_id}: {e}")
                continue
        
        if estimates_created == 0:
            raise HTTPException(status_code=500, detail="No valid estimates created")
        
        logger.info(f"Created {estimates_created} estimates using {filtering_level} preprocessing")
        
        # Update question parameters if available
        parameters_updated = 0
        if 'difficulty_estimates' in results and 'discrimination_estimates' in results:
            difficulty_estimates = results['difficulty_estimates']
            discrimination_estimates = results['discrimination_estimates']
            
            logger.info(f"Updating question parameters for {len(bayesian_data['question_ids'])} questions")
            
            for i, question_id in enumerate(bayesian_data['question_ids']):
                try:
                    # Get parameter estimates (clip to reasonable ranges)
                    a_val = float(np.clip(discrimination_estimates[i], 0.01, 5.0)) if np.isfinite(discrimination_estimates[i]) else 1.0
                    b_val = float(np.clip(difficulty_estimates[i], -5.0, 5.0)) if np.isfinite(difficulty_estimates[i]) else 0.0
                    
                    # Update or create QuestionParameter record
                    db_param = db.query(models.QuestionParameter).filter(
                        models.QuestionParameter.question_id == question_id
                    ).first()
                    
                    if db_param:
                        # Update existing record
                        db_param.parameter_a_mean = a_val
                        db_param.parameter_b_mean = b_val
                        db_param.parameter_c_mean = 0.0  # 2PL model has no guessing parameter
                        db_param.version = "adaptive_2pl_v1"
                        db_param.estimation_method = "mcmc"
                        db_param.updated_at = func.now()
                    else:
                        # Create new record
                        db_param = models.QuestionParameter(
                            question_id=question_id,
                            parameter_a_mean=a_val,
                            parameter_b_mean=b_val,
                            parameter_c_mean=0.0,  # 2PL model has no guessing parameter
                            version="adaptive_2pl_v1",
                            estimation_method="mcmc"
                        )
                        db.add(db_param)
                    
                    # Also update the main Questions table with 2PL parameters
                    db_question = db.query(models.Question).filter(
                        models.Question.question_id == question_id
                    ).first()
                    if db_question:
                        # Store 2PL parameters separately
                        db_question.parameter_a_2pl = a_val
                        db_question.parameter_b_2pl = b_val
                        db_question.updated_at = func.now()
                        logger.info(f"Updated Question {question_id}: a_2pl={a_val:.3f}, b_2pl={b_val:.3f}")
                    else:
                        logger.warning(f"Question {question_id} not found in Questions table")
                    
                    parameters_updated += 1
                    
                except Exception as e:
                    logger.error(f"Failed to update parameters for question {question_id}: {e}")
                    continue
            
            logger.info(f"Updated {parameters_updated} question parameters")
        else:
            logger.warning("No question parameters found in model results")
        
        db.commit()
        
        # Return results
        estimates = db.query(models.BayesianAbilityEstimate).all()
        result_list = [schemas.BayesianAbilityEstimateOut.model_validate(estimate) for estimate in estimates]
        
        return result_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Relaxed adaptive 2PL failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

# ============================================================================
# BASIC CRUD OPERATIONS
# ============================================================================

@router.post("/", response_model=schemas.BayesianAbilityEstimateOut, status_code=status.HTTP_201_CREATED)
def create_bayesian_ability_estimate(estimate: schemas.BayesianAbilityEstimateCreate, db: Session = Depends(get_db)) -> schemas.BayesianAbilityEstimateOut:
    db_estimate = models.BayesianAbilityEstimate(**estimate.model_dump())
    db.add(db_estimate)
    db.commit()
    db.refresh(db_estimate)
    return schemas.BayesianAbilityEstimateOut.model_validate(db_estimate)

@router.get("/", response_model=List[schemas.BayesianAbilityEstimateOut])
def get_bayesian_ability_estimates(db: Session = Depends(get_db)) -> List[schemas.BayesianAbilityEstimateOut]:
    estimates = db.query(models.BayesianAbilityEstimate).all()
    return [schemas.BayesianAbilityEstimateOut.model_validate(estimate) for estimate in estimates]

# ============================================================================
# PARAMETERIZED ROUTES MUST COME LAST (after all specific routes)
# ============================================================================

@router.get("/{estimate_id}", response_model=schemas.BayesianAbilityEstimateOut)
def get_bayesian_ability_estimate(estimate_id: int, db: Session = Depends(get_db)) -> schemas.BayesianAbilityEstimateOut:
    estimate = db.query(models.BayesianAbilityEstimate).filter(models.BayesianAbilityEstimate.estimate_id == estimate_id).first()
    if not estimate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bayesian ability estimate not found")
    return schemas.BayesianAbilityEstimateOut.model_validate(estimate)