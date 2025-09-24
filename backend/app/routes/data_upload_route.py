import email
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..dependencies import get_db
from ..database.postgresql.connection import DatabaseManager, get_db_connection_params
from ..services.irt_data_processor import BayesianIRTDataProcessor
import pandas as pd
import json
import logging
from pathlib import Path
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_json_data(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Upload and process a single JSON file to insert data into the adaptive_exam_db database.
    Returns a dictionary with counts of new students, questions, and responses processed.
    """
    
    if not file.filename or not file.filename.endswith('.json'):
        logger.error("Invalid file type: must be a JSON file")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a valid JSON file"
        )
    
    temp_file_path = None
    db_manager = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        db_params = get_db_connection_params()
        db_params["dbname"] = "adaptive_exam_db"
        db_manager = DatabaseManager(db_params)
        db_manager.connect()
        processor = BayesianIRTDataProcessor(db_manager)
        
        logger.info(f"Processing JSON file: {file.filename}")
        processed_data = processor.process_json_file(temp_file_path)
        logger.info(f"Processed data shape: {processed_data.shape}, columns: {list(processed_data.columns)}")
        
        if processed_data.empty:
            logger.info("No data found in JSON file")
            return {
                "new_students_count": 0,
                "new_questions_count": 0,
                "responses_processed": 0,
                "message": "No data found in JSON file"
            }
        
        # Process students
        new_students = processor.identify_new_students(processed_data)
        processor.insert_students(new_students)
        
        # Process questions
        logger.info("Starting to identify new questions...")
        new_questions = processor.identify_new_questions(processed_data)
        logger.info(f"Identified {len(new_questions)} new questions")
        processor.insert_questions(new_questions)
        
        # Get all existing mappings
        existing_students = processor.get_existing_students()
        existing_questions = processor.get_existing_questions()
        
        logger.info(f"Existing students shape: {existing_students.shape}, columns: {list(existing_students.columns)}")
        logger.info(f"Existing questions shape: {existing_questions.shape}, columns: {list(existing_questions.columns)}")
        
        all_student_mapping = dict(zip(existing_students['email'], existing_students['student_id']))
        
        all_question_mapping = {}
        if not existing_questions.empty and 'question_id' in existing_questions.columns:
            for _, row in existing_questions.iterrows():
                composite_key = (
                    f"{row.get('question_number', '') or ''}|{row.get('question_text', '') or ''}|{row.get('img_url', '') or ''}|"
                    f"{row.get('marks', '') or ''}|{row.get('type', '') or ''}|{row.get('n_choices', '') or ''}|"
                    f"{row.get('correct_answer', '[]') or '[]'}"
                )
                all_question_mapping[composite_key] = row['question_id']
        
        # No need to update question_mapping since insert_questions doesn't return a mapping
        
        # Process responses
        responses_with_ids = []
        seen_responses = set()  # Track (student_id, question_id) pairs

        for idx, response in processed_data.iterrows():
            student_id = all_student_mapping.get(response['email'])
            
            q_composite_key = (
                f"{response.get('question_number', '') or ''}|{response.get('question_text', '') or ''}|{response.get('img_url', '') or ''}|"
                f"{response.get('marks', '') or ''}|{response.get('type', '') or ''}|{response.get('n_choices', '') or ''}|"
                f"{json.dumps(response.get('correct_answer', []) or [])}"
            )
            
            question_id = all_question_mapping.get(q_composite_key)
            
            if not student_id:
                logger.warning(f"No student_id found for email: {response.get('email', 'unknown')}, row_index={idx}")
                continue
            if not question_id:
                logger.warning(f"No question_id found for composite_key: {q_composite_key}, row_index={idx}")
                continue
            
            response_key = (student_id, question_id)
            if response_key in seen_responses:
                logger.warning(f"Duplicate response found for student_id={student_id}, question_id={question_id}, row_index={idx}")
                continue
            
            seen_responses.add(response_key)
            session_id = processor.create_test_session(student_id)
            
            # Handle selected_options (single value, list, or missing)
            selected_options = response.get('selected_options', [])
            chosen_answer = json.dumps(
                selected_options if isinstance(selected_options, list) 
                else [selected_options] if selected_options 
                else []
            )
            
            # Create proper response dictionary with all required fields
            response_dict = {
                'student_id': student_id,
                'session_id': session_id,
                'question_id': question_id,
                'chosen_answer': chosen_answer,
                'is_correct': 1 if response.get('is_correct', False) else 0,
                'response_time_seconds': response.get('response_time_seconds', 0),
                'theta_before': None,
                'theta_after': None,
                'theta_change': None,
                'confidence_interval_low': None,
                'confidence_interval_high': None,
                'item_parameters': json.dumps({}),
                'response_metadata': json.dumps({})
            }
            
            responses_with_ids.append(response_dict)
        
        # Insert all responses at once (outside the loop)
        if responses_with_ids:
            responses_df = pd.DataFrame(responses_with_ids)
            processor.insert_responses(responses_df)
        
        logger.info(f"Successfully processed and updated database with file: {file.filename}")
        logger.debug(f"Inserted {len(new_questions)} new questions, {len(responses_with_ids)} responses")
        
        # Get total counts from database
        total_students = processor.get_existing_students()
        total_questions = processor.get_existing_questions()
        total_responses_count = len(responses_with_ids)  # Current file responses
        
        # Get total responses count from database
        if processor.db_manager.conn:
            try:
                with processor.db_manager.conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM responses")
                    total_responses_count = cursor.fetchone()[0]
            except Exception as e:
                logger.warning(f"Could not get total responses count: {e}")
        
        return {
            "current_file_students": len(new_students),
            "current_file_questions": len(new_questions),
            "current_file_responses": len(responses_with_ids),
            "total_students_in_db": len(total_students),
            "total_questions_in_db": len(total_questions),
            "total_responses_in_db": total_responses_count,
            "message": f"Data from {file.filename} uploaded and processed successfully"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format in {file.filename}: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to process {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process {file.filename}: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")
        
        # Close database connection
        if db_manager:
            db_manager.close()


@router.post("/upload_multiple", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_multiple_json_data(files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
	"""
	Upload and process multiple JSON files to insert data into the adaptive_exam_db database.
	Returns a dictionary with processing results for each file, including counts of new students,
	questions, and responses, and status messages.
	"""
	results = {
		"total_files_processed": 0,
		"total_new_students": 0,
		"total_new_questions": 0,
		"total_responses_processed": 0,
		"file_results": []
	}
	# Initialize DatabaseManager once to reuse connection
	db_params = get_db_connection_params()
	db_params["dbname"] = "adaptive_exam_db"
	db_manager = DatabaseManager(db_params)
	try:
		db_manager.connect()
		processor = BayesianIRTDataProcessor(db_manager)
		for file in files:
			if not file.filename or not file.filename.endswith('.json'):
				logger.error(f"Invalid file type for {file.filename}: must be a JSON file")
				results["file_results"].append({
					"filename": file.filename,
					"status": "failed",
					"error": "File must be a valid JSON file"
				})
				continue
			try:
				logger.info(f"Processing JSON file: {file.filename}")
				with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
					content = await file.read()
					temp_file.write(content)
					temp_file_path = temp_file.name
				# Process the JSON file
				processed_data = processor.process_json_file(temp_file_path)
				if processed_data.empty:
					logger.info(f"No data found in {file.filename}")
					results["file_results"].append({
						"filename": file.filename,
						"status": "skipped",
						"new_students_count": 0,
						"new_questions_count": 0,
						"responses_processed": 0,
						"message": "No data found in JSON file"
					})
					continue
				# Identify and insert new students
				new_students = processor.identify_new_students(processed_data)
				processor.insert_students(new_students)
				# Identify and insert new questions
				new_questions = processor.identify_new_questions(processed_data)
				processor.insert_questions(new_questions)
				# Get existing students and questions
				existing_students = processor.get_existing_students()
				existing_questions = processor.get_existing_questions()
				all_student_mapping = dict(zip(existing_students['email'], existing_students['student_id']))
				all_question_mapping = {}
				if not existing_questions.empty and 'question_id' in existing_questions.columns:
					for _, row in existing_questions.iterrows():
						composite_key = (
							f"{row.get('question_number', '') or ''}|{row.get('question_text', '') or ''}|{row.get('img_url', '') or ''}|"
							f"{row.get('marks', '') or ''}|{row.get('type', '') or ''}|{row.get('n_choices', '') or ''}|"
							f"{row.get('correct_answer', '[]') or '[]'}"
						)
						all_question_mapping[composite_key] = row['question_id']
				
				# No need to update question_mapping since insert_questions doesn't return a mapping
				
				# Process responses and create test sessions
				responses_with_ids = []
				seen_responses = set()  # Track (student_id, question_id) pairs

				for idx, response in processed_data.iterrows():
					student_id = all_student_mapping.get(response['email'])
					
					q_composite_key = (
						f"{response.get('question_number', '') or ''}|{response.get('question_text', '') or ''}|{response.get('img_url', '') or ''}|"
						f"{response.get('marks', '') or ''}|{response.get('type', '') or ''}|{response.get('n_choices', '') or ''}|"
						f"{json.dumps(response.get('correct_answer', []) or [])}"
					)
					
					question_id = all_question_mapping.get(q_composite_key)
					
					if not student_id:
						logger.warning(f"No student_id found for email: {response.get('email', 'unknown')}, row_index={idx}")
						continue
					if not question_id:
						logger.warning(f"No question_id found for composite_key: {q_composite_key}, row_index={idx}")
						continue
					
					response_key = (student_id, question_id)
					if response_key in seen_responses:
						logger.warning(f"Duplicate response found for student_id={student_id}, question_id={question_id}, row_index={idx}")
						continue
					
					seen_responses.add(response_key)
					session_id = processor.create_test_session(student_id)
					
					# Handle selected_options (single value, list, or missing)
					selected_options = response.get('selected_options', [])
					chosen_answer = json.dumps(
						selected_options if isinstance(selected_options, list) 
						else [selected_options] if selected_options 
						else []
					)
					
					# Create proper response dictionary with all required fields
					response_dict = {
						'student_id': student_id,
						'session_id': session_id,
						'question_id': question_id,
						'chosen_answer': chosen_answer,
						'is_correct': 1 if response.get('is_correct', False) else 0,
						'response_time_seconds': response.get('response_time_seconds', 0),
						'theta_before': None,
						'theta_after': None,
						'theta_change': None,
						'confidence_interval_low': None,
						'confidence_interval_high': None,
						'item_parameters': json.dumps({}),
						'response_metadata': json.dumps({})
					}
					
					responses_with_ids.append(response_dict)
				# Insert responses
				if responses_with_ids:
					responses_df = pd.DataFrame(responses_with_ids)
					processor.insert_responses(responses_df)
				# Update results
				results["total_files_processed"] += 1
				results["total_new_students"] += len(new_students)
				results["total_new_questions"] += len(new_questions)
				results["total_responses_processed"] += len(responses_with_ids)
				
				# Get current database totals
				current_students = processor.get_existing_students()
				current_questions = processor.get_existing_questions()
				current_responses_count = 0
				if processor.db_manager.conn:
					try:
						with processor.db_manager.conn.cursor() as cursor:
							cursor.execute("SELECT COUNT(*) FROM responses")
							current_responses_count = cursor.fetchone()[0]
					except Exception as e:
						logger.warning(f"Could not get total responses count: {e}")
				
				results["file_results"].append({
					"filename": file.filename,
					"status": "success",
					"current_file_students": len(new_students),
					"current_file_questions": len(new_questions),
					"current_file_responses": len(responses_with_ids),
					"total_students_in_db": len(current_students),
					"total_questions_in_db": len(current_questions),
					"total_responses_in_db": current_responses_count,
					"message": f"Data from {file.filename} uploaded and processed successfully"
				})
				logger.info(f"Successfully processed and updated database with file: {file.filename}")
			except json.JSONDecodeError as e:
				logger.error(f"Invalid JSON format in {file.filename}: {str(e)}")
				results["file_results"].append({
					"filename": file.filename,
					"status": "failed",
					"error": f"Invalid JSON format: {str(e)}"
				})
			except Exception as e:
				logger.error(f"Failed to process {file.filename}: {str(e)}")
				results["file_results"].append({
					"filename": file.filename,
					"status": "failed",
					"error": f"Failed to process: {str(e)}"
				})
			finally:
				if 'temp_file_path' in locals():
					try:
						os.unlink(temp_file_path)
					except Exception as e:
						logger.warning(f"Failed to delete temporary file for {file.filename}: {str(e)}")
		# Add final database totals to results
		final_students = processor.get_existing_students()
		final_questions = processor.get_existing_questions()
		final_responses_count = 0
		if processor.db_manager.conn:
			try:
				with processor.db_manager.conn.cursor() as cursor:
					cursor.execute("SELECT COUNT(*) FROM responses")
					final_responses_count = cursor.fetchone()[0]
			except Exception as e:
				logger.warning(f"Could not get final responses count: {e}")
		
		results["final_database_totals"] = {
			"total_students_in_db": len(final_students),
			"total_questions_in_db": len(final_questions),
			"total_responses_in_db": final_responses_count
		}
		
		return results
	except Exception as e:
		logger.error(f"Unexpected error during batch processing: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Unexpected error during batch processing: {str(e)}"
		)
	finally:
		db_manager.close()
