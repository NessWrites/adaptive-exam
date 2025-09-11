from pathlib import Path
from typing import Dict, Any
from ai_models.irt_data_processor import BayesianIRTDataProcessor
from ..database.postgresql.connection import DatabaseManager
from ..utils.helpers import parse_score, parse_marks, parse_datetime, parse_options_metadata, clean_question_text, extract_choice_info, extract_chosen_answer
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_and_update_database_bayesian(json_file_path: str, db_params: Dict[str, Any]) -> Dict[str, Any]:
    db_manager = DatabaseManager(db_params)
    processor = BayesianIRTDataProcessor(db_manager)
    try:
        db_manager.connect()
        processed_data = processor.process_json_file(json_file_path)
        if processed_data.empty:
            logger.info("No data found in JSON file")
            return {"new_students_count": 0, "new_questions_count": 0, "responses_processed": 0}
        
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
                    'student_id': student_id, 'question_id': question_id, 'session_id': session_id
                })
                responses_with_ids.append(response_dict)
        
        if responses_with_ids:
            responses_df = pd.DataFrame(responses_with_ids)
            processor.insert_responses(responses_df)
        
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

def process_multiple_json_files_bayesian(folder_path: str, db_params: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        "total_new_students": 0,
        "total_new_questions": 0,
        "total_responses_processed": 0,
        "processed_files": []
    }
    for file_path in Path(folder_path).glob("*.json"):
        logger.info(f"Processing file: {file_path}")
        try:
            file_results = process_and_update_database_bayesian(str(file_path), db_params)
            if file_results:
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