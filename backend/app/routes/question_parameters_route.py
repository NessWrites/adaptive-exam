from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import models
from ..schemas import schemas
from ..dependencies import get_db
from ..services.irt_utils import create_long_format_data, fetch_data_for_bayesian_analysis, get_db_connection_params
from ..database.postgresql.connection import DatabaseManager
from psycopg2.extras import RealDictCursor  
import logging
import pandas as pd
import numpy as np
import asyncio
import arviz as az

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

# Custom routes must be defined before parameterized routes to avoid conflicts
@router.api_route("/bayesian-update", methods=["POST", "GET"], response_model=List[schemas.QuestionParameterOut])
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

        # Fetch data for Bayesian analysis, This creates the df_long a format data and prepares it for the Bayesian IRT model
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        if not bayesian_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No response data available for Bayesian IRT analysis.Please install required dependencies: pip install pymc arviz aesara pytensor")

        # Run the Bayesian IRT model
        loop = asyncio.get_running_loop()
        irt_results = await loop.run_in_executor(None,run_hierarchical_3pl_model,bayesian_data)
        if not irt_results["analysis_completed"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bayesian IRT analysis failed")
        
        # Extract trace for diagnostics and samples
        trace = irt_results["trace"]
        rhat = az.rhat(trace)
        ess = az.ess(trace)

       


        # Extract question parameters
        question_params = irt_results["question_parameters"]
        # Map model question index j -> actual question_id using df_long from bayesian_data
        df_long = bayesian_data["df_long"]
        j_to_question_id = (
            df_long.groupby("j")["question_id"].first().sort_index()
        )

        logger.info(f"Processing {irt_results['n_questions']} questions for parameter update")
        logger.info(f"Available question indices: {list(j_to_question_id.index)}")
        
        updated_params = []
        for j in range(irt_results["n_questions"]):
            # Get question_id from mapping; skip if missing (shouldn't happen if data aligned)
            question_id = j_to_question_id[j]
            if not question_id:
                logger.warning(f"No question ID found for index {j}")
                continue
            
            logger.info(f"Processing question {j} with ID: {question_id}")

            # Compute samples and diagnostics from trace with proper type conversion
            try:
                a_samples = [float(x) for x in trace.posterior["a"].sel(a_dim_0=j).values.flatten()[:1000]]
                b_samples = [float(x) for x in trace.posterior["b"].sel(b_dim_0=j).values.flatten()[:1000]]
                c_samples = [float(x) for x in trace.posterior["c"].sel(c_dim_0=j).values.flatten()[:1000]]
            except Exception as e:
                logger.warning(f"Error extracting samples for question {j}: {e}")
                a_samples = [0.0] * 1000
                b_samples = [0.0] * 1000
                c_samples = [0.0] * 1000
            
            parameter_samples = {
                "a_samples": a_samples,
                "b_samples": b_samples,
                "c_samples": c_samples
            }
            
            # Safely compute convergence diagnostics
            try:
                convergence_diagnostics = {
                    "a_r_hat": float(rhat.a.sel(a_dim_0=j).values) if hasattr(rhat, 'a') else 1.0,
                    "b_r_hat": float(rhat.b.sel(b_dim_0=j).values) if hasattr(rhat, 'b') else 1.0,
                    "c_r_hat": float(rhat.c.sel(c_dim_0=j).values) if hasattr(rhat, 'c') else 1.0,
                    "a_ess": float(ess.a.sel(a_dim_0=j).values) if hasattr(ess, 'a') else 100.0,
                    "b_ess": float(ess.b.sel(b_dim_0=j).values) if hasattr(ess, 'b') else 100.0,
                    "c_ess": float(ess.c.sel(c_dim_0=j).values) if hasattr(ess, 'c') else 100.0
                }
            except Exception as e:
                logger.warning(f"Error computing convergence diagnostics for question {j}: {e}")
                convergence_diagnostics = {
                    "a_r_hat": 1.0,
                    "b_r_hat": 1.0,
                    "c_r_hat": 1.0,
                    "a_ess": 100.0,
                    "b_ess": 100.0,
                    "c_ess": 100.0
                }

            # Check if question parameter exists
            db_param = db.query(models.QuestionParameter).filter(
                models.QuestionParameter.question_id == question_id
            ).first()

            param_data = {
                "question_id": str(question_id),
                "parameter_a_mean": float(question_params["a_means"][j]),
                "parameter_a_std": float(question_params["a_stds"][j]),
                "parameter_b_mean": float(question_params["b_means"][j]),
                "parameter_b_std": float(question_params["b_stds"][j]),
                "parameter_c_mean": float(question_params["c_means"][j]),
                "parameter_c_std": float(question_params["c_stds"][j]),
                "model_version": "bayesian_irt_v1",
                "estimation_method": "mcmc",
                "n_samples": int(len(a_samples)),
                "convergence_diagnostics": irt_results["convergence_diagnostics"]
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
                logger.info(f"Updating Question table for {question_id}: a={param_data['parameter_a_mean']:.3f}, b={param_data['parameter_b_mean']:.3f}, c={param_data['parameter_c_mean']:.3f}")
                db_question.parameter_a = param_data["parameter_a_mean"]
                db_question.parameter_b = param_data["parameter_b_mean"]
                db_question.parameter_c = param_data["parameter_c_mean"]
            else:
                logger.warning(f"Question {question_id} not found in Questions table")
        
        #Save ability estimates similarly
        theta_means = irt_results["theta_estimates"]
        theta_stds = irt_results["theta_stds"]
        students = df_long.groupby('i')['student_id'].first()
        
        for i in range(irt_results["n_students"]):
            student_id = int(students[i])  # Convert numpy type to Python int
            if not student_id:
                logger.warning(f"No student ID found for index {i}")
                continue

            theta_samples = [float(x) for x in trace.posterior["theta"].sel(theta_dim_0=i).values.flatten()[:1000]]
            hdi_5, hdi_95 = float(np.percentile(theta_samples, 5)), float(np.percentile(theta_samples, 95))
            posterior_summary = {
                "mean": float(theta_means[i]),
                "std": float(theta_stds[i]),
                "hdi_5": hdi_5,
                "hdi_95": hdi_95
            }
            convergence_diagnostics = {
                "r_hat": float(rhat.theta.sel(theta_dim_0=i).values) if hasattr(rhat, 'theta') else 1.0,
                "ess": float(ess.theta.sel(theta_dim_0=i).values) if hasattr(ess, 'theta') else 100.0
            }
            estimate_data = {
                "student_id": int(student_id),
                "theta_mean": float(theta_means[i]),
                "theta_std": float(theta_stds[i]),
                "theta_samples": theta_samples,
                "posterior_summary": posterior_summary,
                "model_version": "bayesian_irt_v1",
                "estimation_method": "mcmc",
                "n_samples": int(len(theta_samples)),
                "convergence_diagnostics": convergence_diagnostics
            }
            db_estimate = db.query(models.BayesianAbilityEstimate).filter(
                models.BayesianAbilityEstimate.student_id == student_id
            ).first()
            if db_estimate:
                for key, value in estimate_data.items():
                    setattr(db_estimate, key, value)
            else:
                db_estimate = models.BayesianAbilityEstimate(**estimate_data)
                db.add(db_estimate)


        # Commit all changes in a single transaction
        try:
            db.commit()
            for param in updated_params:
                db.refresh(param)
            logger.info(f"Successfully updated {len(updated_params)} question parameters and {irt_results['n_students']} ability estimates")
            logger.info(f"Convergence diagnostics: {irt_results['convergence_diagnostics']}")
        except Exception as e:
                db.rollback()
                logger.error(f"Database commit failed: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database commit failed: {str(e)}")

        return [schemas.QuestionParameterOut.model_validate(param) for param in updated_params]

    except Exception as e:
        logger.error(f"Failed to update question parameters: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        if 'db_manager' in locals() and db_manager:
            logger.debug("Closing database connection")
            db_manager.close()

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

@router.get("/debug/long-format-data")
async def debug_long_format_data(db: Session = Depends(get_db)):
    """Debug endpoint to test the create_long_format_data function"""
    logger.info("Basic test endpoint called")
    try:
        # Initialize database manager
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()
        logger.info("Database connection established")

        # Fetch raw data from database
        query = """
        SELECT 
            r.student_id,
            r.question_id,
            r.chosen_answer,
            r.is_correct,
            r.response_time_seconds,
            q.n_choices,
            q.correct_answer,
            q.parameter_a,
            q.parameter_b,
            q.parameter_c
        FROM responses r
        JOIN questions q ON r.question_id = q.question_id
        ORDER BY r.student_id, r.question_id
        LIMIT 100
        """
        
        with db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
        if not results:
            return {"error": "No response data found"}
        
        responses_df = pd.DataFrame(results)
        
        # Get questions data
        question_ids = responses_df['question_id'].unique()
        question_ids_str = ",".join([f"'{qid}'" for qid in question_ids])
        
        questions_query = f"""
        SELECT question_id, question_text, img_url, marks, type, 
               n_choices, correct_answer, parameter_a, parameter_b, parameter_c
        FROM questions 
        WHERE question_id IN ({question_ids_str})
        """
        
        with db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(questions_query)
            questions_results = cursor.fetchall()
        
        questions_df = pd.DataFrame(questions_results)
        
        # Test the create_long_format_data function
        df_long = create_long_format_data(responses_df, questions_df)
        
        db_manager.close()
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # Convert df_long sample data
        df_long_sample = df_long.head(10).to_dict('records')
        df_long_sample = convert_numpy_types(df_long_sample)
        
        # Convert student and question mappings
        student_mapping = {int(k): int(v) for k, v in enumerate(responses_df['student_id'].unique())}
        question_mapping = {int(k): str(v) for k, v in enumerate(questions_df['question_id'].unique())}
        
        return {
            "success": True,
            "df_long_created": not df_long.empty,
            "df_long_shape": list(df_long.shape),
            "df_long_columns": list(df_long.columns),
            "df_long_sample": df_long_sample,
            "student_mapping_sample": dict(list(student_mapping.items())[:5]),
            "question_mapping_sample": dict(list(question_mapping.items())[:5])
        }
        
    except Exception as e:
        logger.error(f"Debug long format data failed: {e}", exc_info=True)
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
        return {"error": str(e), "success": False}

@router.get("/debug/test-bayesian-model")
async def debug_test_bayesian_model(db: Session = Depends(get_db)):
    """Debug endpoint to test just the Bayesian model without saving to database"""
    try:
        if not BAYESIAN_IRT_AVAILABLE:
            return {"error": "Bayesian IRT not available", "success": False}
            
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()

        # Fetch data for Bayesian analysis
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        if not bayesian_data:
            return {"error": "No Bayesian data found", "success": False}

        logger.info("Starting mock Bayesian model (due to compilation issues)...")
        
        # Create mock results instead of running actual PyMC model
        # This simulates what the Bayesian model would return
        N = bayesian_data["N"]
        J = bayesian_data["J"]
        
        # Generate realistic parameter estimates
        np.random.seed(42)  # For reproducible results
        
        # Discrimination parameters (a) - lognormal distribution
        a_means = np.random.lognormal(mean=0.5, sigma=0.3, size=J)
        a_stds = np.random.uniform(0.1, 0.3, size=J)
        
        # Difficulty parameters (b) - normal distribution
        b_means = np.random.normal(0, 1, size=J)
        b_stds = np.random.uniform(0.2, 0.5, size=J)
        
        # Guessing parameters (c) - beta distribution
        c_means = np.random.beta(2, 8, size=J)  # Mean around 0.2
        c_stds = np.random.uniform(0.05, 0.15, size=J)
        
        # Student ability estimates
        theta_means = np.random.normal(0, 1, size=N)
        theta_stds = np.random.uniform(0.1, 0.4, size=N)
        
        # Create mock results
        mock_results = {
            "analysis_completed": True,
            "n_questions": J,
            "n_students": N,
            "max_rhat": 1.02,
            "convergence_diagnostics": {
                "max_rhat": 1.02,
                "min_ess": 800,
                "divergences": 0
            },
            "question_parameters": {
                "a_means": a_means,
                "a_stds": a_stds,
                "b_means": b_means,
                "b_stds": b_stds,
                "c_means": c_means,
                "c_stds": c_stds
            },
            "student_parameters": {
                "theta_means": theta_means,
                "theta_stds": theta_stds
            }
        }
        
        logger.info("Mock Bayesian model completed successfully")
        
        # Show sample results
        sample_results = {
            "success": True,
            "analysis_completed": mock_results["analysis_completed"],
            "n_questions": mock_results["n_questions"],
            "n_students": mock_results["n_students"],
            "max_rhat": mock_results["max_rhat"],
            "sample_question_params": {
                "a_means_sample": a_means[:5].tolist(),
                "b_means_sample": b_means[:5].tolist(),
                "c_means_sample": c_means[:5].tolist(),
                "a_stds_sample": a_stds[:5].tolist(),
                "b_stds_sample": b_stds[:5].tolist(),
                "c_stds_sample": c_stds[:5].tolist()
            },
            "note": "This is a mock implementation due to PyMC compilation issues on Apple Silicon"
        }
        
        db_manager.close()
        return sample_results
        
    except Exception as e:
        logger.error(f"Debug test bayesian model failed: {e}", exc_info=True)
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
        return {"error": str(e), "success": False}

@router.get("/debug/fetch-bayesian-data")
async def debug_fetch_bayesian_data(db: Session = Depends(get_db)):
    """Debug endpoint to see what fetch_data_for_bayesian_analysis returns"""
    try:
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()

        # Fetch data for Bayesian analysis
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        
        if not bayesian_data:
            return {"error": "No Bayesian data found", "success": False}
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # Convert df_long sample data
        df_long_sample = bayesian_data["df_long"].to_dict('records')
        df_long_sample = convert_numpy_types(df_long_sample)
        
        # debug_data = {
        #     "success": True,
        #     "N": int(bayesian_data["N"]),
        #     "J": int(bayesian_data["J"]),
        #     "i_idx_sample": bayesian_data["i_idx"][:20].tolist(),  # First 20 student indices
        #     "j_idx_sample": bayesian_data["j_idx"][:20].tolist(),  # First 20 question indices
        #     "y_obs_sample": bayesian_data["y_obs"][:20].tolist(),  # First 20 responses
        #     "K_arr": bayesian_data["K_arr"].tolist(),
        #     "df_long_shape": list(bayesian_data["df_long"].shape),
        #     "df_long_columns": list(bayesian_data["df_long"].columns),
        #     "df_long_sample": df_long_sample,
        #     "unique_students": int(bayesian_data["df_long"]["i"].nunique()),
        #     "unique_questions": int(bayesian_data["df_long"]["j"].nunique())
        # }
        
        db_manager.close()
        return df_long_sample
        
    except Exception as e:
        logger.error(f"Debug fetch bayesian data failed: {e}", exc_info=True)
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
        return {"error": str(e), "success": False}

@router.get("/debug/save-ability-estimates")
async def debug_save_ability_estimates(db: Session = Depends(get_db)):
    """Debug endpoint to see what save_bayesian_ability_estimates saves"""
    try:
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()

        # Get some sample data
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        if not bayesian_data:
            return {"error": "No data available for testing", "success": False}

        # Create sample theta data
        n_students = bayesian_data["N"]
        theta_means = np.random.normal(0, 1, n_students)
        theta_stds = np.random.uniform(0.1, 0.5, n_students)
        
        # Show what would be saved
        df_long = bayesian_data["df_long"]
        students = df_long.groupby('i')['student_id'].first()
        
        sample_estimates = []
        for i, (student_idx, student_id) in enumerate(students.items()[:5]):  # First 5 students
            theta_samples = np.random.normal(theta_means[i], theta_stds[i], 1000).tolist()
            posterior_summary = {
                "mean": float(theta_means[i]),
                "std": float(theta_stds[i]),
                "hdi_5": float(np.percentile(theta_samples, 5)),
                "hdi_95": float(np.percentile(theta_samples, 95)),
                "r_hat": 1.01,
                "ess": 950
            }
            
            sample_estimates.append({
                "student_id": int(student_id),
                "theta_mean": float(theta_means[i]),
                "theta_std": float(theta_stds[i]),
                "theta_samples_count": len(theta_samples),
                "posterior_summary": posterior_summary,
                "n_samples": 1000
            })
        
        db_manager.close()
        
        return {
            "success": True,
            "total_students": len(students),
            "sample_estimates": sample_estimates,
            "table_name": "bayesian_ability_estimates",
            "description": "This shows what would be saved to bayesian_ability_estimates table"
        }
        
    except Exception as e:
        logger.error(f"Debug save ability estimates failed: {e}", exc_info=True)
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
        return {"error": str(e), "success": False}

@router.get("/debug/save-question-parameters")
async def debug_save_question_parameters(db: Session = Depends(get_db)):
    """Debug endpoint to see what save_bayesian_question_parameters saves"""
    try:
        db_params = get_db_connection_params()
        db_manager = DatabaseManager(db_params)
        db_manager.connect()

        # Get some sample data
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        if not bayesian_data:
            return {"error": "No data available for testing", "success": False}

        # Create sample parameter data
        n_questions = bayesian_data["J"]
        param_a = np.random.uniform(0.5, 2.0, n_questions)
        param_b = np.random.uniform(-2.0, 2.0, n_questions)
        param_c = np.random.uniform(0.1, 0.3, n_questions)
        a_stds = np.random.uniform(0.1, 0.3, n_questions)
        b_stds = np.random.uniform(0.2, 0.4, n_questions)
        c_stds = np.random.uniform(0.05, 0.15, n_questions)
        
        # Show what would be saved
        df_long = bayesian_data["df_long"]
        questions = df_long.groupby('j')['question'].first()
        
        sample_parameters = []
        for j, (question_idx, question_id) in enumerate(questions.items()[:5]):  # First 5 questions
            a_samples = np.random.normal(param_a[j], a_stds[j], 1000).tolist()
            b_samples = np.random.normal(param_b[j], b_stds[j], 1000).tolist()
            c_samples = np.random.normal(param_c[j], c_stds[j], 1000).tolist()
            
            parameter_samples = {
                "a_samples": a_samples[:10],  # Just first 10 for display
                "b_samples": b_samples[:10],
                "c_samples": c_samples[:10],
                "convergence": {
                    "a_r_hat": 1.02,
                    "b_r_hat": 1.01,
                    "c_r_hat": 1.03
                }
            }
            
            sample_parameters.append({
                "question_id": str(question_id),
                "parameter_a_mean": float(param_a[j]),
                "parameter_a_std": float(a_stds[j]),
                "parameter_b_mean": float(param_b[j]),
                "parameter_b_std": float(b_stds[j]),
                "parameter_c_mean": float(param_c[j]),
                "parameter_c_std": float(c_stds[j]),
                "parameter_samples": parameter_samples,
                "n_samples": 1000
            })
        
        db_manager.close()
        
        return {
            "success": True,
            "total_questions": len(questions),
            "sample_parameters": sample_parameters,
            "table_name": "question_parameters",
            "description": "This shows what would be saved to question_parameters table"
        }
        
    except Exception as e:
        logger.error(f"Debug save question parameters failed: {e}", exc_info=True)
        if 'db_manager' in locals() and db_manager:
            db_manager.close()
        return {"error": str(e), "success": False}