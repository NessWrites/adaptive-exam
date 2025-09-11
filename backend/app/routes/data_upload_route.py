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
	Upload and process a single JSON file to insert data into the adaptive-exam database.
	Returns a dictionary with counts of new students, questions, and responses processed.
	"""

	
	if not file.filename or not file.filename.endswith('.json'):
		logger.error("Invalid file type: must be a JSON file")
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="File must be a valid JSON file"
		)
	try:
		with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
			content = await file.read()
			temp_file.write(content)
			temp_file_path = temp_file.name
		db_params = get_db_connection_params()
		db_params["dbname"] = "adaptive-exam"
		db_manager = DatabaseManager(db_params)
		db_manager.connect()
		processor = BayesianIRTDataProcessor(db_manager)
		logger.info(f"Processing JSON file: {file.filename}")
		processed_data = processor.process_json_file(temp_file_path)
		if processed_data.empty:
			logger.info("No data found in JSON file")
			return {
				"new_students_count": 0,
				"new_questions_count": 0,
				"responses_processed": 0,
				"message": "No data found in JSON file"
			}
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
		logger.info(f"Successfully processed and updated database with file: {file.filename}")
		return {
			"new_students_count": len(new_students),
			"new_questions_count": len(new_questions),
			"responses_processed": len(responses_with_ids),
			"message": f"Data from {file.filename} uploaded and processed successfully"
		}
	except json.JSONDecodeError as e:
		logger.error(f"Invalid JSON format in {file.filename}: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Invalid JSON format in {file.filename}: {str(e)}"
		)
	except Exception as e:
		logger.error(f"Failed to process {file.filename}: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Failed to process {file.filename}: {str(e)}"
		)
	finally:
		if temp_file_path is not None:
			try:
				os.unlink(temp_file_path)
			except Exception as e:
				logger.warning(f"Failed to delete temporary file: {str(e)}")
		if db_manager is not None:
			db_manager.close()
@router.post("/upload_multiple", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_multiple_json_data(files: List[UploadFile] = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
	"""
	Upload and process multiple JSON files to insert data into the adaptive-exam database.
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
	db_params["dbname"] = "adaptive-exam"
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
				student_mapping = processor.insert_students(new_students)
				# Identify and insert new questions
				new_questions = processor.identify_new_questions(processed_data)
				question_mapping = processor.insert_questions(new_questions)
				# Get existing students and questions
				existing_students = processor.get_existing_students()
				existing_questions = processor.get_existing_questions()
				all_student_mapping = dict(zip(existing_students['email'], existing_students['student_id']))
				all_student_mapping.update(student_mapping)
				all_question_mapping = {}
				for _, row in existing_questions.iterrows():
					composite_key = f"{row['question_text']}|{row['img_url']}|{row['marks']}|{row['type']}"
					all_question_mapping[composite_key] = row['question_id']
				all_question_mapping.update(question_mapping)
				# Process responses and create test sessions
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
				# Insert responses
				if responses_with_ids:
					responses_df = pd.DataFrame(responses_with_ids)
					processor.insert_responses(responses_df)
				# Update results
				results["total_files_processed"] += 1
				results["total_new_students"] += len(new_students)
				results["total_new_questions"] += len(new_questions)
				results["total_responses_processed"] += len(responses_with_ids)
				results["file_results"].append({
					"filename": file.filename,
					"status": "success",
					"new_students_count": len(new_students),
					"new_questions_count": len(new_questions),
					"responses_processed": len(responses_with_ids),
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
		return results
	except Exception as e:
		logger.error(f"Unexpected error during batch processing: {str(e)}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Unexpected error during batch processing: {str(e)}"
		)
	finally:
		db_manager.close()
