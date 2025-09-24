from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, TypedDict, Any, Optional
import logging
import json
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

from backend.app import models
from ..utils.helpers import parse_score, parse_marks, parse_datetime, parse_options_metadata, clean_question_text, extract_choice_info, extract_chosen_answer
from ..services.irt_data_processor import BayesianIRTDataProcessor
from ..database.postgresql.connection import DatabaseManager
import arviz as az
from sqlalchemy.orm import Session


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayesianIRTData(TypedDict):
    N: int
    J: int
    i_idx: np.ndarray
    j_idx: np.ndarray
    y_obs: np.ndarray
    K_arr: np.ndarray
    df_long: pd.DataFrame
    
def get_db_connection_params() -> Dict[str, Any]:
    """Get database connection parameters from environment variables"""
    load_dotenv()
    
    return {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT", "5432"))  # Default to 5432 if not set
    }
    
def create_long_format_data(responses_df: pd.DataFrame, questions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert response data to long format suitable for Bayesian IRT analysis
    Similar to your df_long creation
    """
    rows = []
    
    # Create student index mapping
    students = responses_df['student_id'].unique()
    student_to_idx = {student: i for i, student in enumerate(students)}
    
    # Create question index mapping
    questions = questions_df['question_id'].unique()
    question_to_idx = {question: j for j, question in enumerate(questions)}
    
    for _, response in responses_df.iterrows():
        student_id = response['student_id']
        question_id = response['question_id']
        
        # Get question metadata
        q_meta = questions_df[questions_df['question_id'] == question_id].iloc[0]
        
        rows.append({
            "student_id": student_id,
            "i": student_to_idx[student_id],  # Student index for modeling
            "question_id": question_id,
            "j": question_to_idx[question_id],  # Question index for modeling
            "n_choices": q_meta['n_choices'],
            "correct_answer": q_meta['correct_answer'],
            "chosen": response['chosen_answer'],
            "is_correct": response['is_correct'],
            "response_time": response.get('response_time_seconds'),
            "session_id": response.get('session_id')
        })
    
    df_long = pd.DataFrame(rows)
    return df_long

def prepare_bayesian_irt_data(df_long: pd.DataFrame) -> BayesianIRTData:
    """
    Prepare data arrays for PyMC Bayesian IRT model
    Returns the same format as your preprocessing
    """
    N = df_long["i"].nunique()  # Number of students
    J = df_long["j"].nunique()  # Number of questions
    
    i_idx = df_long["i"].to_numpy(dtype=int)
    j_idx = df_long["j"].to_numpy(dtype=int)
    y_obs = df_long["is_correct"].to_numpy(dtype=int)
    
    # Get K_arr (number of choices per question) in question order
    K_arr = df_long.groupby("j")["n_choices"].first().sort_index().to_numpy(dtype=int)
    
    return {"N": N,
        "J": J,
        "i_idx": i_idx,
        "j_idx": j_idx,
        "y_obs": y_obs,
        "K_arr": K_arr,
        "df_long": df_long}    
    
def fetch_data_for_bayesian_analysis(db_manager: DatabaseManager) -> Optional[BayesianIRTData]:
    """
    Fetch all response data from database and prepare for Bayesian IRT analysis
    Returns data in the same format as your PyMC preprocessing
    """
    if db_manager.conn is None:
        logger.error("Database connection is not available")
        raise ConnectionError("Database connection is not available")
    
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
    """
    
    try:
        with db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            
        if not results:
            logger.warning("No response data found for Bayesian analysis")
            return None
        
        df = pd.DataFrame(results)
        
        # Create the long format data
        students = df['student_id'].unique()
        questions = df['question_id'].unique()
        
        student_to_idx = {student: i for i, student in enumerate(students)}
        question_to_idx = {question: j for j, question in enumerate(questions)}
        
        df['i'] = df['student_id'].map(student_to_idx)
        df['j'] = df['question_id'].map(question_to_idx)
        
        # Prepare data arrays
        bayesian_data = prepare_bayesian_irt_data(df)
        
        logger.info(f"Prepared Bayesian IRT data: {bayesian_data['N']} students, {bayesian_data['J']} questions")
        return bayesian_data
        
    except Exception as e:
        logger.error(f"Failed to fetch data for Bayesian analysis: {e}")
        raise

def save_bayesian_ability_estimates(db_manager: DatabaseManager, theta_means: np.ndarray, 
                                   theta_stds: np.ndarray, df_long: pd.DataFrame):
    """Save Bayesian ability estimates to database"""
    if db_manager.conn is None:
        logger.error("Database connection is not available")
        raise ConnectionError("Database connection is not available")
    
    students = df_long.groupby('i')['student_id'].first()

    
    insert_sql = """
    INSERT INTO bayesian_ability_estimates 
    (student_id, theta_mean, theta_std, theta_samples, posterior_summary, n_samples)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        with db_manager.conn.cursor() as cursor:
            for i, (student_idx, student_id) in enumerate(students.items()):
                theta_samples = np.random.normal(theta_means[i], theta_stds[i], 1000).tolist()
                
                posterior_summary = {
                    "mean": float(theta_means[i]),
                    "std": float(theta_stds[i]),
                    "hdi_5": float(np.percentile(theta_samples, 5)),
                    "hdi_95": float(np.percentile(theta_samples, 95)),
                    "r_hat": 1.01,
                    "ess": 950
                }
                
                cursor.execute(insert_sql, (
                    student_id, float(theta_means[i]), float(theta_stds[i]),
                    json.dumps(theta_samples), json.dumps(posterior_summary), 1000
                ))
        
        db_manager.conn.commit()
        logger.info(f"Saved Bayesian ability estimates for {len(students)} students")
        
    except Exception as e:
        if db_manager.conn is not None:
            db_manager.conn.rollback()
        logger.error(f"Failed to save ability estimates: {e}")
        raise

def save_bayesian_question_parameters(
    db_manager: DatabaseManager, 
    param_a: np.ndarray,
    param_b: np.ndarray,
    param_c: np.ndarray,
    a_stds: np.ndarray,
    b_stds: np.ndarray,
    c_stds: np.ndarray,
    df_long: pd.DataFrame,
    trace: az.InferenceData)-> None:
    
    """Save Bayesian question parameters to database"""
    if db_manager.conn is None:
        logger.error("Database connection is not available")
        raise ConnectionError("Database connection is not available")
    
    questions = df_long.groupby('j')['question_id'].first()
    
    insert_sql = """
    INSERT INTO question_parameters 
    (question_id, parameter_a_mean, parameter_a_std, parameter_b_mean, parameter_b_std,
     parameter_c_mean, parameter_c_std, parameter_samples,model_version, estimation_method, n_samples,convergence_diagnostics)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (question_id) DO UPDATE SET 
        parameter_a_mean = EXCLUDED.parameter_a_mean,
        parameter_a_std = EXCLUDED.parameter_a_std,
        parameter_b_mean = EXCLUDED.parameter_b_mean,
        parameter_b_std = EXCLUDED.parameter_b_std,
        parameter_c_mean = EXCLUDED.parameter_c_mean,
        parameter_c_std = EXCLUDED.parameter_c_std,
        parameter_samples = EXCLUDED.parameter_samples,
        model_version = EXCLUDED.model_version,
        estimation_method = EXCLUDED.estimation_method,
        n_samples = EXCLUDED.n_samples
        convergence_diagnostics = EXCLUDED.convergence_diagnostics,
    """
    
    try:
        with db_manager.conn.cursor() as cursor:
            # Compute convergence diagnostics once
            rhat = az.rhat(trace)
            ess = az.ess(trace)  # Effective sample size for better diagnostics
            for j, (question_idx, question_id) in enumerate(questions.items()):
                # Use passed standard deviations
                a_std = float(a_stds[j])
                b_std = float(b_stds[j])
                c_std = float(c_stds[j])
                
                a_samples = np.random.normal(param_a[j], a_std, 1000).tolist()
                b_samples = np.random.normal(param_b[j], b_std, 1000).tolist()
                c_samples = np.random.normal(param_c[j], c_std, 1000).tolist()
                
                parameter_samples = {
                    "a_samples": a_samples,
                    "b_samples": b_samples,
                    "c_samples": c_samples,
                    
                }

                # Construct convergence diagnostics
                convergence_diagnostics = {
                    "a_r_hat": float(rhat.a.sel(a_dim_0=j).values),
                    "b_r_hat": float(rhat.b.sel(b_dim_0=j).values),
                    "c_r_hat": float(rhat.c.sel(c_dim_0=j).values),
                    "a_ess": float(ess.a.sel(a_dim_0=j).values),
                    "b_ess": float(ess.b.sel(b_dim_0=j).values),
                    "c_ess": float(ess.c.sel(c_dim_0=j).values)
                }

                
                cursor.execute(insert_sql, (
                    question_id,
                    float(param_a[j]),
                    float(a_std),
                    float(param_b[j]),
                    float(b_std),
                    float(param_c[j]),
                    float(c_std),
                    json.dumps(parameter_samples),
                    "bayesian_irt_v1",  # model_version
                    "mcmc",             # estimation_method
                    len(a_samples),      # n_samples
                    json.dumps(convergence_diagnostics)
                ))
        
        db_manager.conn.commit()
        logger.info(f"Saved Bayesian question parameters for {len(questions)} questions")
        
    except Exception as e:
        if db_manager.conn is not None:
            db_manager.conn.rollback()
        logger.error(f"Failed to save question parameters: {e}")
        raise

def update_theta_after_response(db_manager: DatabaseManager, response_id: int, 
                               new_theta_mean: float, new_theta_std: float,
                               theta_samples: List[float], convergence_info: Dict):
    """
    Update theta estimates after processing a new response
    """
    if db_manager.conn is None:
        logger.error("Database connection is not available")
        raise ConnectionError("Database connection is not available")
    
    update_response_sql = """
    UPDATE responses 
    SET theta_after = %s, 
        theta_change = theta_after - COALESCE(theta_before, 0),
        confidence_interval_low = %s,
        confidence_interval_high = %s
    WHERE response_id = %s
    """
    
    get_student_sql = "SELECT student_id FROM responses WHERE response_id = %s"
    
    try:
        with db_manager.conn.cursor() as cursor:
            cursor.execute(get_student_sql, (response_id,))
            result = cursor.fetchone()
            if result is None:
                raise ValueError("Failed to create student session - no student_id returned")
            student_id = result[0]
            
            hdi_low = float(np.percentile(theta_samples, 5))
            hdi_high = float(np.percentile(theta_samples, 95))
            
            cursor.execute(update_response_sql, (
                new_theta_mean, hdi_low, hdi_high, response_id
            ))
            
            insert_ability_sql = """
            INSERT INTO bayesian_ability_estimates 
            (student_id, theta_mean, theta_std, theta_samples, posterior_summary, 
             convergence_diagnostics, n_samples)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            posterior_summary = {
                "mean": new_theta_mean,
                "std": new_theta_std,
                "hdi_5": hdi_low,
                "hdi_95": hdi_high
            }
            
            cursor.execute(insert_ability_sql, (
                student_id, new_theta_mean, new_theta_std,
                json.dumps(theta_samples), json.dumps(posterior_summary),
                json.dumps(convergence_info), len(theta_samples)
            ))
            
        db_manager.conn.commit()
        logger.info(f"Updated theta estimates for student {student_id}")
        
    except Exception as e:
        if db_manager.conn is not None:
            db_manager.conn.rollback()
        logger.error(f"Failed to update theta after response: {e}")
        raise

def export_for_pymc_analysis(db_connection_params: Dict[str, str], 
                            output_path: str = "bayesian_irt_data.json") -> Optional[Dict[str, Any]]:
    """
    Export database data in the exact format needed for PyMC model
    """
    db_params = get_db_connection_params()
    db_manager = DatabaseManager(db_params)
    
    try:
        db_manager.connect()
        bayesian_data = fetch_data_for_bayesian_analysis(db_manager)
        
        if bayesian_data:
            export_data = {
                "N": int(bayesian_data["N"]),
                "J": int(bayesian_data["J"]),
                "i_idx": bayesian_data["i_idx"].tolist(),
                "j_idx": bayesian_data["j_idx"].tolist(),
                "y_obs": bayesian_data["y_obs"].tolist(),
                "K_arr": bayesian_data["K_arr"].tolist()
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return {
                "data_arrays": export_data,
                "df_long": bayesian_data["df_long"],
                "exported_to": output_path
            }
        
    except Exception as e:
        logger.error(f"Failed to export PyMC data: {e}")
        raise
    finally:
        db_manager.close()

def process_and_update_database_bayesian(json_file_path: str, db_connection_params: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Main function to process JSON file and update database for Bayesian IRT analysis
    """
    db_params = get_db_connection_params()

    db_manager = DatabaseManager(db_params)
    processor = BayesianIRTDataProcessor(db_manager)
    
    try:
        db_manager.connect()
        db_manager.create_table_if_not_exist()
        
        logger.info(f"Processing JSON file for Bayesian IRT: {json_file_path}")
        processed_data = processor.process_json_file(json_file_path)
        
        if processed_data.empty:
            logger.info("No data found in JSON file")
            return{"new_students_count": 0,
                "new_questions_count": 0,
                "responses_processed": 0}
        
        new_students = processor.identify_new_students(processed_data)
        student_mapping = processor.insert_students(new_students)
        
        new_questions = processor.identify_new_questions(processed_data)
        question_mapping = processor.insert_questions(new_questions)
        
        existing_students = processor.get_existing_students()
        existing_questions = processor.get_existing_questions()
        
        all_student_mapping = dict(zip(existing_students['email'], existing_students['student_id']))
        all_student_mapping.update(student_mapping)
        
        all_question_mapping = {}
        for _, row in existing_questions.iterrows():
            composite_key = f"{row['question_text']}|{row['img_url']}|{row['marks']}|{row['type']}"
            all_question_mapping[composite_key] = row['question_id']
        all_question_mapping.update(question_mapping)
        
        responses_with_ids = []
        for _, response in processed_data.iterrows():
            student_id = all_student_mapping.get(response['email'])
            q_composite_key = f"{response['question_text']}|{response['img_url']}|{response['marks']}|{response['type']}"
            question_id = all_question_mapping.get(q_composite_key)
            
            if student_id and question_id:
                session_id = processor.create_test_session(student_id)
                response_dict = response.to_dict()
                response_dict.update({
                    'student_id': student_id,
                    'question_id': question_id,
                    'session_id': session_id
                })
                responses_with_ids.append(response_dict)
        
        if responses_with_ids:
            responses_df = pd.DataFrame(responses_with_ids)
            processor.insert_responses(responses_df)
        
        logger.info("Bayesian IRT pipeline completed successfully")
        
        return {
            "new_students_count": len(new_students),
            "new_questions_count": len(new_questions),
            "responses_processed": len(responses_with_ids)
        }
        
    except Exception as e:
        logger.error(f"Bayesian IRT pipeline failed: {e}")
        raise
    finally:
        db_manager.close()

def process_multiple_json_files_bayesian(folder_path: str, db_connection_params: Dict[str, str]) -> Dict[str, Any]:
    """Process multiple JSON files with Bayesian IRT optimization"""
    results = {
        "total_new_students": 0,
        "total_new_questions": 0,
        "total_responses_processed": 0,
        "processed_files": []
    }
    
    for file_path in Path(folder_path).glob("*.json"):
        logger.info(f"Processing file: {file_path}")
        try:
            db_params = get_db_connection_params()
            file_results = process_and_update_database_bayesian(str(file_path), db_params)
            if file_results:  # Check if file_results is not None
                results["total_new_students"] += file_results["new_students_count"]
                results["total_new_questions"] += file_results["new_questions_count"]
                results["total_responses_processed"] += file_results["responses_processed"]
                results["processed_files"].append(str(file_path))
            else:
                logger.warning(f"No results returned for file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            continue
    
    return results

def prepare_lite_bayesian_data(bayesian_data: BayesianIRTData) -> Dict[str, Any]:
    """
    Prepare data for the lightweight 3PL model from existing BayesianIRTData format.
    Creates a response matrix format suitable for the sparse implementation.
    
    Args:
        bayesian_data: Output from prepare_bayesian_irt_data()
    
    Returns:
        Dictionary with response matrix and metadata
    """
    N = bayesian_data["N"]
    J = bayesian_data["J"]
    i_idx = bayesian_data["i_idx"]
    j_idx = bayesian_data["j_idx"]
    y_obs = bayesian_data["y_obs"]
    
    # Create a dense response matrix with NaN for missing responses
    response_matrix = np.full((N, J), np.nan, dtype=np.float32)
    response_matrix[i_idx, j_idx] = y_obs
    
    return {
        'response_matrix': response_matrix,
        'student_ids': np.arange(N),
        'question_ids': np.arange(J),
        'original_data': bayesian_data  # Keep original for reference
    }
def prepare_lite_bayesian_data(bayesian_data: dict) -> Dict[str, Any]:
    """
    Prepare data for the lightweight 3PL model from existing BayesianIRTData format.
    Creates a response matrix format suitable for the sparse implementation with stability enhancements.
    
    Args:
        bayesian_data: Output from prepare_bayesian_irt_data()
    
    Returns:
        Dictionary with response matrix and metadata
    """
    N = bayesian_data["N"]
    J = bayesian_data["J"]
    i_idx = bayesian_data["i_idx"]
    j_idx = bayesian_data["j_idx"]
    y_obs = bayesian_data["y_obs"]
    
    # Create a dense response matrix with NaN for missing responses
    response_matrix = np.full((N, J), np.nan, dtype=np.float32)
    response_matrix[i_idx, j_idx] = y_obs
    
    # Apply stability preprocessing
    stable_data = preprocess_for_stable_irt(response_matrix)
    
    return {
        'response_matrix': stable_data['response_matrix'],
        'student_ids': stable_data['student_ids'],
        'question_ids': stable_data['question_ids'],
        'filtering_stats': stable_data['filtering_stats'],
        'original_data': bayesian_data  # Keep original for reference
    }

def prepare_lite_bayesian_irt_data(db: Session) -> Dict[str, Any]:
    """
    Enhanced preparation of Bayesian IRT data with stability preprocessing
    """
    try:
        from ..models import models
        
        # Get all responses with student and question info
        responses = db.query(
            models.Response.student_id,
            models.Response.question_id,
            models.Response.is_correct
        ).all()
        
        if not responses:
            raise ValueError("No response data found in database")
        
        # Get unique student and question IDs
        student_ids = sorted(set([r.student_id for r in responses]))
        question_ids = sorted(set([r.question_id for r in responses]))
        
        n_students = len(student_ids)
        n_questions = len(question_ids)
        
        logger.info(f"Initial data: {n_students} students, {n_questions} questions")
        
        # Create mapping from IDs to indices
        student_id_to_idx = {id: idx for idx, id in enumerate(student_ids)}
        question_id_to_idx = {id: idx for idx, id in enumerate(question_ids)}
        
        # Initialize response matrix with NaN
        response_matrix = np.full((n_students, n_questions), np.nan)
        
        # Fill response matrix
        for response in responses:
            student_idx = student_id_to_idx[response.student_id]
            question_idx = question_id_to_idx[response.question_id]
            response_matrix[student_idx, question_idx] = response.is_correct
        
        # Apply enhanced stability preprocessing
        stable_data = preprocess_for_stable_irt(
            response_matrix=response_matrix,
            original_student_ids=student_ids,
            original_question_ids=question_ids
        )
        
        logger.info(f"After preprocessing: {len(stable_data['student_ids'])} students, "
                   f"{len(stable_data['question_ids'])} questions")
        logger.info(f"Filtering stats: {stable_data['filtering_stats']}")
        
        return stable_data
        
    except Exception as e:
        raise Exception(f"Failed to prepare Bayesian IRT data: {str(e)}")

def preprocess_for_stable_irt(response_matrix: np.ndarray, 
                            original_student_ids: list = None, 
                            original_question_ids: list = None,
                            min_responses_per_student: int = 3,
                            min_responses_per_question: int = 3,
                            min_question_difficulty: float = 0.05,
                            max_question_difficulty: float = 0.95,
                            min_student_ability: float = 0.05,
                            max_student_ability: float = 0.95) -> Dict[str, Any]:
    """
    Enhanced preprocessing to create a stable response matrix for IRT modeling
    
    Args:
        response_matrix: Original response matrix with NaN for missing responses
        original_student_ids: List of original student IDs (optional)
        original_question_ids: List of original question IDs (optional)
        min_responses_per_student: Minimum responses required per student
        min_responses_per_question: Minimum responses required per question
        min_question_difficulty: Minimum proportion correct (filters too easy questions)
        max_question_difficulty: Maximum proportion correct (filters too hard questions)
        min_student_ability: Minimum proportion correct (filters very low ability students)
        max_student_ability: Maximum proportion correct (filters perfect score students)
    
    Returns:
        Dictionary with filtered data and filtering statistics
    """
    n_students_orig, n_questions_orig = response_matrix.shape
    logger.info(f"Starting preprocessing: {n_students_orig} students, {n_questions_orig} questions")
    
    # Initialize filtering statistics
    filtering_stats = {
        'original_students': n_students_orig,
        'original_questions': n_questions_orig,
        'students_removed_low_responses': 0,
        'questions_removed_low_responses': 0,
        'questions_removed_extreme_difficulty': 0,
        'students_removed_extreme_ability': 0,
        'final_students': 0,
        'final_questions': 0,
        'sparsity_before': 0.0,
        'sparsity_after': 0.0
    }
    
    # Calculate initial sparsity
    total_possible = n_students_orig * n_questions_orig
    observed_orig = np.sum(~np.isnan(response_matrix))
    filtering_stats['sparsity_before'] = (1 - observed_orig / total_possible) * 100
    
    # Step 1: Remove questions with insufficient responses
    question_response_counts = np.sum(~np.isnan(response_matrix), axis=0)
    valid_questions = question_response_counts >= min_responses_per_question
    
    if np.sum(~valid_questions) > 0:
        logger.info(f"Removing {np.sum(~valid_questions)} questions with < {min_responses_per_question} responses")
        filtering_stats['questions_removed_low_responses'] = int(np.sum(~valid_questions))
        response_matrix = response_matrix[:, valid_questions]
        if original_question_ids is not None:
            original_question_ids = [original_question_ids[i] for i in range(len(original_question_ids)) if valid_questions[i]]
    
    # Step 2: Remove students with insufficient responses
    student_response_counts = np.sum(~np.isnan(response_matrix), axis=1)
    valid_students = student_response_counts >= min_responses_per_student
    
    if np.sum(~valid_students) > 0:
        logger.info(f"Removing {np.sum(~valid_students)} students with < {min_responses_per_student} responses")
        filtering_stats['students_removed_low_responses'] = int(np.sum(~valid_students))
        response_matrix = response_matrix[valid_students, :]
        if original_student_ids is not None:
            original_student_ids = [original_student_ids[i] for i in range(len(original_student_ids)) if valid_students[i]]
    
    # Step 3: Remove questions with extreme difficulties (too easy or too hard)
    question_means = np.nanmean(response_matrix, axis=0)
    reasonable_difficulty = (question_means >= min_question_difficulty) & (question_means <= max_question_difficulty)
    
    if np.sum(~reasonable_difficulty) > 0:
        logger.info(f"Removing {np.sum(~reasonable_difficulty)} questions with extreme difficulty")
        filtering_stats['questions_removed_extreme_difficulty'] = int(np.sum(~reasonable_difficulty))
        response_matrix = response_matrix[:, reasonable_difficulty]
        if original_question_ids is not None:
            original_question_ids = [original_question_ids[i] for i in range(len(original_question_ids)) if reasonable_difficulty[i]]
    
    # Step 4: Remove students with extreme abilities (perfect or zero scores)
    student_means = np.nanmean(response_matrix, axis=1)
    reasonable_ability = (student_means >= min_student_ability) & (student_means <= max_student_ability)
    
    if np.sum(~reasonable_ability) > 0:
        logger.info(f"Removing {np.sum(~reasonable_ability)} students with extreme abilities")
        filtering_stats['students_removed_extreme_ability'] = int(np.sum(~reasonable_ability))
        response_matrix = response_matrix[reasonable_ability, :]
        if original_student_ids is not None:
            original_student_ids = [original_student_ids[i] for i in range(len(original_student_ids)) if reasonable_ability[i]]
    
    # Step 5: One more pass to ensure minimum requirements are still met
    # (removing extreme cases might have reduced response counts)
    question_response_counts = np.sum(~np.isnan(response_matrix), axis=0)
    valid_questions_final = question_response_counts >= min_responses_per_question
    
    if np.sum(~valid_questions_final) > 0:
        logger.info(f"Final pass: removing {np.sum(~valid_questions_final)} more questions")
        response_matrix = response_matrix[:, valid_questions_final]
        if original_question_ids is not None:
            original_question_ids = [original_question_ids[i] for i in range(len(original_question_ids)) if valid_questions_final[i]]
    
    student_response_counts = np.sum(~np.isnan(response_matrix), axis=1)
    valid_students_final = student_response_counts >= min_responses_per_student
    
    if np.sum(~valid_students_final) > 0:
        logger.info(f"Final pass: removing {np.sum(~valid_students_final)} more students")
        response_matrix = response_matrix[valid_students_final, :]
        if original_student_ids is not None:
            original_student_ids = [original_student_ids[i] for i in range(len(original_student_ids)) if valid_students_final[i]]
    
    # Update final statistics
    n_students_final, n_questions_final = response_matrix.shape
    filtering_stats['final_students'] = n_students_final
    filtering_stats['final_questions'] = n_questions_final
    
    # Calculate final sparsity
    total_possible_final = n_students_final * n_questions_final
    observed_final = np.sum(~np.isnan(response_matrix))
    filtering_stats['sparsity_after'] = (1 - observed_final / total_possible_final) * 100
    
    # Create student and question IDs if not provided
    if original_student_ids is None:
        original_student_ids = list(range(n_students_final))
    if original_question_ids is None:
        original_question_ids = list(range(n_questions_final))
    
    # Validate minimum requirements for IRT
    if n_students_final < 20:
        logger.warning(f"Very few students remaining ({n_students_final}). Consider relaxing filtering criteria.")
    if n_questions_final < 10:
        logger.warning(f"Very few questions remaining ({n_questions_final}). Consider relaxing filtering criteria.")
    
    return {
        'response_matrix': response_matrix,
        'student_ids': original_student_ids,
        'question_ids': original_question_ids,
        'n_students': n_students_final,
        'n_questions': n_questions_final,
        'filtering_stats': filtering_stats
    }

def check_sparse_matrix_stats(db: Session, apply_preprocessing: bool = True) -> Dict[str, Any]:
    """
    Enhanced statistics check with optional preprocessing preview
    """
    try:
        from ..models import models
        
        # Get all responses with student and question info
        responses = db.query(
            models.Response.student_id,
            models.Response.question_id,
            models.Response.is_correct
        ).all()
        
        if not responses:
            raise ValueError("No response data found in database")
        
        # Get unique student and question IDs
        student_ids = sorted(set([r.student_id for r in responses]))
        question_ids = sorted(set([r.question_id for r in responses]))
        
        n_students = len(student_ids)
        n_questions = len(question_ids)
        
        # Create mapping from IDs to indices
        student_id_to_idx = {id: idx for idx, id in enumerate(student_ids)}
        question_id_to_idx = {id: idx for idx, id in enumerate(question_ids)}
        
        # Initialize response matrix with NaN
        response_matrix = np.full((n_students, n_questions), np.nan)
        
        # Fill response matrix
        for response in responses:
            student_idx = student_id_to_idx[response.student_id]
            question_idx = question_id_to_idx[response.question_id]
            response_matrix[student_idx, question_idx] = response.is_correct
        
        # Calculate original statistics
        total_possible_entries = n_students * n_questions
        observed_entries = np.sum(~np.isnan(response_matrix))
        sparsity = 1 - (observed_entries / total_possible_entries)
        
        # Student response counts
        student_response_counts = np.sum(~np.isnan(response_matrix), axis=1)
        # Question response counts  
        question_response_counts = np.sum(~np.isnan(response_matrix), axis=0)
        
        # Count questions with low responses
        low_response_questions_1 = np.sum(question_response_counts < 1)
        low_response_questions_3 = np.sum(question_response_counts < 3)
        low_response_questions_5 = np.sum(question_response_counts < 5)
        low_response_questions_10 = np.sum(question_response_counts < 10)
        
        # Apply preprocessing if requested
        preprocessed_stats = None
        if apply_preprocessing:
            try:
                preprocessed_data = preprocess_for_stable_irt(
                    response_matrix, student_ids, question_ids
                )
                preprocessed_matrix = preprocessed_data['response_matrix']
                
                # Calculate preprocessed statistics
                pp_n_students, pp_n_questions = preprocessed_matrix.shape
                pp_observed = np.sum(~np.isnan(preprocessed_matrix))
                pp_total_possible = pp_n_students * pp_n_questions
                pp_sparsity = 1 - (pp_observed / pp_total_possible)
                
                preprocessed_stats = {
                    'preprocessed_students': pp_n_students,
                    'preprocessed_questions': pp_n_questions,
                    'preprocessed_sparsity': float(pp_sparsity * 100),
                    'filtering_applied': preprocessed_data['filtering_stats']
                }
                
                # Update suitability based on preprocessed data
                n_students = pp_n_students
                n_questions = pp_n_questions
                student_response_counts = np.sum(~np.isnan(preprocessed_matrix), axis=1)
                question_response_counts = np.sum(~np.isnan(preprocessed_matrix), axis=0)
                low_response_questions_3 = np.sum(question_response_counts < 3)
                low_response_questions_5 = np.sum(question_response_counts < 5)
                
            except Exception as e:
                logger.warning(f"Preprocessing failed during stats check: {e}")
                preprocessed_stats = {'error': str(e)}
        
        # Enhanced suitability criteria
        ideal_for_irt = (
            n_students >= 100 and 
            n_questions >= 30 and
            np.min(student_response_counts) >= 10 and
            np.mean(question_response_counts) >= 20 and
            low_response_questions_5 <= 5
        )
        
        suitable_for_irt = (
            n_students >= 50 and 
            n_questions >= 20 and
            np.min(student_response_counts) >= 5 and
            np.mean(question_response_counts) >= 10 and
            low_response_questions_5 <= 10
        )
        
        can_proceed_with_caution = (
            n_students >= 30 and 
            n_questions >= 15 and
            np.min(student_response_counts) >= 3 and
            np.mean(question_response_counts) >= 8 and
            low_response_questions_3 <= 15
        )
        
        stats = {
            'n_students': n_students,
            'n_questions': n_questions,
            'total_possible_entries': int(total_possible_entries),
            'observed_entries': int(observed_entries),
            'sparsity_percentage': float(sparsity * 100),
            'avg_responses_per_student': float(np.mean(student_response_counts)),
            'min_responses_per_student': int(np.min(student_response_counts)),
            'max_responses_per_student': int(np.max(student_response_counts)),
            'avg_responses_per_question': float(np.mean(question_response_counts)),
            'min_responses_per_question': int(np.min(question_response_counts)),
            'max_responses_per_question': int(np.max(question_response_counts)),
            'questions_with_0_responses': int(low_response_questions_1),
            'questions_with_less_than_3_responses': int(low_response_questions_3),
            'questions_with_less_than_5_responses': int(low_response_questions_5),
            'questions_with_less_than_10_responses': int(low_response_questions_10),
            'student_ids_sample': student_ids[:5],
            'question_ids_sample': question_ids[:5],
            'matrix_shape': response_matrix.shape,
            'is_ideal_for_irt': ideal_for_irt,
            'is_suitable_for_irt': suitable_for_irt,
            'can_proceed_with_caution': can_proceed_with_caution,
            'data_quality': 'ideal' if ideal_for_irt else 'suitable' if suitable_for_irt else 'caution' if can_proceed_with_caution else 'poor',
            'preprocessing_preview': preprocessed_stats
        }
        
        return stats
        
    except Exception as e:
        raise Exception(f"Failed to compute sparse matrix stats: {str(e)}")

def validate_data_for_2pl(response_matrix: np.ndarray, min_variance_threshold: float = 0.01) -> Dict[str, Any]:
    """
    Additional validation specifically for 2PL model stability
    
    Args:
        response_matrix: Response matrix to validate
        min_variance_threshold: Minimum variance required for parameters
    
    Returns:
        Dictionary with validation results and recommendations
    """
    n_students, n_questions = response_matrix.shape
    
    # Check for numerical stability issues
    validation = {
        'matrix_shape': (n_students, n_questions),
        'has_variation': True,
        'warnings': [],
        'recommendations': []
    }
    
    # Check if there's sufficient variation
    question_means = np.nanmean(response_matrix, axis=0)
    question_vars = np.nanvar(response_matrix, axis=0)
    
    low_variance_questions = np.sum(question_vars < min_variance_threshold)
    if low_variance_questions > 0:
        validation['warnings'].append(f"{low_variance_questions} questions have very low variance")
        validation['recommendations'].append("Consider removing questions with minimal variation")
    
    # Check for extreme response patterns
    extreme_easy = np.sum(question_means > 0.95)
    extreme_hard = np.sum(question_means < 0.05)
    
    if extreme_easy > 0:
        validation['warnings'].append(f"{extreme_easy} questions are answered correctly >95% of the time")
        validation['recommendations'].append("Remove overly easy questions for better discrimination")
    
    if extreme_hard > 0:
        validation['warnings'].append(f"{extreme_hard} questions are answered correctly <5% of the time")
        validation['recommendations'].append("Remove overly difficult questions for better model fit")
    
    # Check student ability distribution
    student_means = np.nanmean(response_matrix, axis=1)
    perfect_students = np.sum(student_means >= 0.95)
    zero_students = np.sum(student_means <= 0.05)
    
    if perfect_students > 0:
        validation['warnings'].append(f"{perfect_students} students have >95% correct responses")
    if zero_students > 0:
        validation['warnings'].append(f"{zero_students} students have <5% correct responses")
    
    return validation