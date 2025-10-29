import hashlib
import pandas as pd
import json
import logging
from typing import Dict, Optional
from pathlib import Path
import uuid
from ..database.postgresql.connection import DatabaseManager
from psycopg2.extras import RealDictCursor
from ..utils.helpers import parse_score, parse_marks, parse_datetime, parse_options_metadata, clean_question_text, extract_choice_info, extract_chosen_answer


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayesianIRTDataProcessor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # Ensure tables exist when initializing the processor
        # Temporarily disabled to test upload endpoint
        # self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Ensure all required tables exist in the database"""
        try:
            logger.info("Starting table creation/verification...")
            self.db_manager.create_table_if_not_exist()
            logger.info("Database tables verified/created successfully")
        except Exception as e:
            logger.error(f"Failed to ensure tables exist: {e}")
            raise

    # --------------------------------------------------------------------------
    # NEW ORCHESTRATION METHOD
    # --------------------------------------------------------------------------
    def process_directory(self, directory_path: str):
        """
        Processes all JSON files in a given directory, identifies new students
        and questions, creates records, and inserts all student responses.
        This method orchestrates the batch processing functionality.
        """
        # --- Step 1: Aggregate Data from all JSONs ---
        logger.info(f"Starting to process directory: {directory_path}")
        data_folder = Path(directory_path)
        if not data_folder.is_dir():
            logger.error(f"Error: Directory '{directory_path}' not found.")
            return

        json_files = list(data_folder.glob('*.json'))
        if not json_files:
            logger.warning(f"No JSON files found in '{directory_path}'.")
            return

        logger.info(f"Found {len(json_files)} JSON files to process.")
        all_dfs = [self.process_json_file(str(file_path)) for file_path in json_files]
        master_df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Aggregated {len(master_df)} total responses from all files.")

        if master_df.empty:
            logger.info("No data to process after reading files. Exiting.")
            return
            
        # --- Step 2: Handle Students ---
        logger.info("Processing students...")
        unique_students_df = master_df[['email', 'student_name']].drop_duplicates()
        self.insert_students(unique_students_df)
        
        all_students_db = self.get_existing_students()
        email_to_id_map = pd.Series(all_students_db.student_id.values, index=all_students_db.email).to_dict()
        master_df['student_id'] = master_df['email'].map(email_to_id_map)
        
        if master_df['student_id'].isnull().any():
            missing_students = master_df[master_df['student_id'].isnull()]['email'].unique()
            logger.error(f"Could not map student_id for emails: {list(missing_students)}. Aborting.")
            raise ValueError("Student ID mapping failed.")
        master_df['student_id'] = master_df['student_id'].astype(int)
        logger.info("Student processing complete.")
        
        # --- Step 3: Handle Questions ---
        logger.info("Processing questions...")
        new_questions_df = self.identify_new_questions(master_df)
        if not new_questions_df.empty:
            self.insert_questions(new_questions_df)
            logger.info(f"Processed {len(new_questions_df)} new questions.")
        else:
            logger.info("No new questions found.")
        
        all_questions_db = self.get_existing_questions()

        def create_composite_key(row, answer_is_json=False):
            correct_answer_str = row['correct_answer'] if answer_is_json else json.dumps(row.get('correct_answer') or [])
            topic_dimension = row.get('topic_dimension', '')
            cognitive_dimension = row.get('cognitive_dimension', '')
            return (
                f"{row.get('question_number', '')}|{row.get('question_text', '')}|{row.get('img_url', '')}|"
                f"{row.get('marks', '')}|{row.get('type', '')}|{row.get('n_choices', '')}|"
                f"{correct_answer_str}|{topic_dimension}|{cognitive_dimension}"
            )

        all_questions_db['composite_key'] = all_questions_db.apply(lambda row: create_composite_key(row, answer_is_json=True), axis=1)
        composite_to_id_map = pd.Series(all_questions_db.question_id.values, index=all_questions_db.composite_key).to_dict()
        
        master_df['composite_key'] = master_df.apply(lambda row: create_composite_key(row, answer_is_json=False), axis=1)
        master_df['question_id'] = master_df['composite_key'].map(composite_to_id_map)
        master_df = master_df.drop(columns=['composite_key'])
        
        if master_df['question_id'].isnull().any():
            logger.error("Could not map question_id for some responses. Aborting.")
            raise ValueError("Question ID mapping failed.")
        logger.info("Question processing complete.")
        
        # --- Step 4: Handle Test Sessions ---
        logger.info("Creating test sessions...")
        student_ids_for_sessions = master_df['student_id'].unique()
        student_id_to_session_id = {
            student_id: self.create_test_session(student_id) for student_id in student_ids_for_sessions
        }
        
        master_df['session_id'] = master_df['student_id'].map(student_id_to_session_id)
        logger.info(f"Created {len(student_id_to_session_id)} new test sessions.")
        
        # --- Step 5: Insert Responses ---
        logger.info("Inserting responses...")
        # Add placeholder columns required by the insert_responses method
        for col in ['response_time_seconds', 'theta_before', 'theta_after', 'theta_change', 
                    'confidence_interval_low', 'confidence_interval_high', 'item_parameters', 
                    'response_metadata']:
            if col not in master_df:
                master_df[col] = None
                
        self.insert_responses(master_df)
        logger.info("Successfully inserted all responses.")
        logger.info("Directory processing complete.")

    # --------------------------------------------------------------------------
    # EXISTING HELPER METHODS (with one bug fix)
    # --------------------------------------------------------------------------

    def get_existing_students(self) -> pd.DataFrame:
        """Get existing students from database"""
        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            return pd.DataFrame(columns=['student_id', 'name', 'email'])
    
        query = "SELECT student_id, name, email FROM students"
        try:
            with self.db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    return pd.DataFrame(results)
                else:
                    # Return empty DataFrame with correct column names
                    return pd.DataFrame(columns=['student_id', 'name', 'email'])
        except Exception as e:
            logger.error(f"Failed to fetch existing students: {e}")
            return pd.DataFrame(columns=['student_id', 'name', 'email'])
    
    def get_existing_questions(self) -> pd.DataFrame:
        """Get existing questions from database"""
        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            return pd.DataFrame(columns=['question_id','question_number', 'question_text', 'img_url', 'marks', 'type', 
                                   'n_choices', 'correct_answer', 'options', 'parameter_a', 'parameter_b', 'parameter_c', 
                                   'topic_dimension', 'cognitive_dimension'])
        query = """SELECT question_id, question_number, question_text, img_url, marks, type, 
                          n_choices, correct_answer, options, parameter_a, parameter_b, parameter_c, 
                          topic_dimension, cognitive_dimension 
                   FROM questions"""
        try:
            with self.db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    return pd.DataFrame(results)
                else:
                    # Return empty DataFrame with correct column names
                    return pd.DataFrame(columns=['question_id', 'question_number','question_text', 'img_url', 'marks', 'type', 
                                               'n_choices', 'correct_answer', 'options', 'parameter_a', 'parameter_b', 'parameter_c',
                                               'topic_dimension', 'cognitive_dimension'])
        except Exception as e:
            logger.error(f"Failed to fetch existing questions: {e}")
            return pd.DataFrame(columns=['question_id', 'question_number','question_text', 'img_url', 'marks', 'type', 
                                       'n_choices', 'correct_answer', 'options', 'parameter_a', 'parameter_b', 'parameter_c',
                                       'topic_dimension', 'cognitive_dimension'])
    
    def get_student_current_theta(self, student_id: int) -> Optional[float]:
        """Get current Bayesian theta estimate for a student"""
        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            return None
        query = """
        SELECT theta_mean 
        FROM bayesian_ability_estimates 
        WHERE student_id = %s 
        ORDER BY updated_at DESC 
        LIMIT 1
        """
        try:
            with self.db_manager.conn.cursor() as cursor:
                cursor.execute(query, (student_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception:
            return None
    
    def process_json_file(self, file_path: str) -> pd.DataFrame:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Validate that data is a dictionary
            if not isinstance(data, dict):
                logger.error(f"Invalid JSON structure: expected dictionary, got {type(data)}")
                return pd.DataFrame()
            
            rows = []
            for student, student_data in data.items():
                # Validate that student_data is a dictionary
                if not isinstance(student_data, dict):
                    logger.warning(f"Invalid student data structure for {student}: expected dictionary, got {type(student_data)}")
                    continue
                    
                email = student_data.get('email', '')
                student_name = student_data.get('name', '')
                questions = student_data.get('questions', [])
                if len(questions) != 50:
                    logger.warning(f"Student {email} has {len(questions)} questions, expected 50")
                question_numbers = set()
                for question in questions:
                    # Validate that question is a dictionary
                    if not isinstance(question, dict):
                        logger.warning(f"Invalid question structure for student {email}: expected dictionary, got {type(question)}")
                        continue
                        
                    question_number = question.get('question_number', '')
                    if question_number in question_numbers:
                        logger.warning(f"Duplicate question_number {question_number} for student {email}")
                        continue
                    question_numbers.add(question_number)
                    marks_text = question.get('marks', '')
                    marks_value = parse_marks(marks_text)
                    n_choices, correct_answer = extract_choice_info(question)
                    chosen_answer = extract_chosen_answer(question, n_choices, correct_answer)
                    # Extract and preprocess options_metadata to keep only labels
                    options_metadata = question.get('options_metadata', '[]')
                    try:
                        if isinstance(options_metadata, str):
                            options_list = json.loads(options_metadata)
                        else:
                            options_list = options_metadata
                        
                        # Extract only the "label" values from each option
                        if isinstance(options_list, list):
                            # Keep only unique labels (remove duplicates)
                            unique_labels = []
                            for opt in options_list:
                                if isinstance(opt, dict) and 'label' in opt:
                                    label = opt.get('label', '').strip()
                                    if label and label not in unique_labels:
                                        unique_labels.append(label)
                            options_list = unique_labels
                    except (json.JSONDecodeError, TypeError):
                        options_list = []
                    
                    row = {
                        'email': email,
                        'student_name': student_name,
                        'question_number': question_number,
                        'question_text': clean_question_text(question.get('question_text', '')),
                        'img_url': question.get('img_url', ''),
                        'marks': marks_value,
                        'type': question.get('type', ''),
                        'selected_options': question.get('selected_options', []),
                        'is_correct': question.get('is_correct', False),
                        'n_choices': n_choices,
                        'correct_answer': correct_answer,
                        'chosen_answer': chosen_answer,
                        'options': options_list,
                        'options_metadata': json.dumps(options_list),  # Store cleaned labels as JSON string
                        'topic_dimension': question.get('topic_dimension', ''),
                        'cognitive_dimension': question.get('cognitive_dimension', '')
                    }
                    rows.append(row)
            processed_data = pd.DataFrame(rows)
            logger.debug(f"Processed JSON: {len(processed_data)} rows, {processed_data['question_number'].nunique()} unique questions")
            if len(processed_data) != len(data) * 50:
                logger.warning(f"Expected {len(data) * 50} responses, got {len(processed_data)}")
            return processed_data
        except Exception as e:
            logger.error(f"Failed to process JSON file {file_path}: {str(e)}", exc_info=True)
            raise
    
    def identify_new_students(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Identify students that don't exist in database"""
        existing_students = self.get_existing_students()
        unique_students = new_data[["email", "student_name"]].drop_duplicates("email")
        
        if existing_students.empty:
            return unique_students
        else:
            new_students = unique_students[~unique_students['email'].isin(existing_students['email'])]
            return new_students
    
    def identify_new_questions(self, data: pd.DataFrame) -> pd.DataFrame:
        existing_questions = self.get_existing_questions()
        logger.debug(f"Existing questions DataFrame shape: {existing_questions.shape}")
        logger.debug(f"Existing questions DataFrame columns: {list(existing_questions.columns)}")
        
        existing_composites = set()
        if not existing_questions.empty and 'question_number' in existing_questions.columns:
            for _, row in existing_questions.iterrows():
                topic_dimension = row.get('topic_dimension', '')
                cognitive_dimension = row.get('cognitive_dimension', '')
                composite_key = (
                    f"{row['question_number'] or ''}|{row['question_text'] or ''}|{row['img_url'] or ''}|"
                    f"{row['marks'] or ''}|{row['type'] or ''}|{row['n_choices'] or ''}|"
                    f"{row['correct_answer'] or '[]'}|{topic_dimension}|{cognitive_dimension}"
                )
                existing_composites.add(composite_key)
        
        new_questions_map = {}
        for _, row in data.iterrows():
            topic_dimension = row.get('topic_dimension', '')
            cognitive_dimension = row.get('cognitive_dimension', '')
            composite_key = (
                f"{row['question_number'] or ''}|{row['question_text'] or ''}|{row['img_url'] or ''}|"
                f"{row['marks'] or ''}|{row['type'] or ''}|{row['n_choices'] or ''}|"
                f"{json.dumps(row['correct_answer'] or [])}|{topic_dimension}|{cognitive_dimension}"
            )
            if composite_key not in existing_composites and composite_key not in new_questions_map:
                question_id = f"Q{hashlib.md5(composite_key.encode()).hexdigest()[:8]}"
                new_questions_map[composite_key] = {
                    'question_id': question_id,
                    'question_number': row['question_number'],
                    'question_text': row['question_text'],
                    'img_url': row['img_url'],
                    'marks': row['marks'],
                    'type': row['type'],
                    'n_choices': row['n_choices'],
                    'correct_answer': json.dumps(row['correct_answer']),
                    'options_metadata': row.get('options_metadata', ''),
                    'topic_dimension': topic_dimension,
                    'cognitive_dimension': cognitive_dimension
                }
        
        new_questions_df = pd.DataFrame(list(new_questions_map.values()))
        logger.debug(f"Identified {len(new_questions_df)} new questions.")
        return new_questions_df
    
    def insert_students(self, students_df: pd.DataFrame) -> None:
        """Insert new students or update existing ones."""
        if students_df.empty:
            logger.info("No new students to insert.")
            return
        if self.db_manager.conn is None:
            logger.error("Database connection is not available.")
            return
        
        insert_sql = """
        INSERT INTO students (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email) 
        DO UPDATE SET name = EXCLUDED.name
        """
        
        try:
            with self.db_manager.conn.cursor() as cursor:
                # Use execute_batch for efficiency if available, otherwise loop
                values = [(row.get('student_name'), row['email']) for _, row in students_df.iterrows()]
                cursor.executemany(insert_sql, values)
                self.db_manager.conn.commit()
                logger.info(f"Inserted/updated {len(students_df)} students.")
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert students: {e}")
            raise
    
    def insert_questions(self, questions_df: pd.DataFrame) -> None:
        """Insert new questions into the database."""
        if questions_df.empty:
            return
        
        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            return

        query = """
        INSERT INTO questions (question_id, question_number, question_text, img_url, marks, type, n_choices, correct_answer, options, options_metadata, topic_dimension, cognitive_dimension)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (question_id) DO NOTHING
        """
        try:
            with self.db_manager.conn.cursor() as cursor:
                # *** BUG FIX: The original code returned inside the loop. ***
                # This has been corrected to insert all questions in the DataFrame.
                values = [
                    (row['question_id'], row['question_number'], row['question_text'],
                     row['img_url'], row['marks'], row['type'],
                     row['n_choices'], row['correct_answer'], 
                     json.dumps(row.get('options', [])),
                     row.get('options_metadata', ''),
                     row.get('topic_dimension'), row.get('cognitive_dimension'))
                    for _, row in questions_df.iterrows()
                ]
                cursor.executemany(query, values)
            self.db_manager.conn.commit()
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert questions: {e}")
            raise
    
    def create_test_session(self, student_id: int, session_type: str = "assessment") -> int:
        """Create test session for Bayesian analysis"""
        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            raise ConnectionError("Database connection is not available")
        
        insert_sql = """
        INSERT INTO test_sessions (student_id, session_type, selection_strategy)
        VALUES (%s, %s, %s)
        RETURNING session_id
        """
        try:
            with self.db_manager.conn.cursor() as cursor:
                cursor.execute(insert_sql, (student_id, session_type, 'random'))
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Failed to create test session - no session_id returned")
                session_id = result[0]
                self.db_manager.conn.commit()
                return session_id
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to create test session for student_id {student_id}: {e}")
            raise
    
    def insert_responses(self, responses_df: pd.DataFrame) -> None:
        """Insert response data into database"""
        if responses_df.empty:
            logger.info("No responses to insert")
            return

        if self.db_manager.conn is None:
            logger.error("Database connection is not available")
            return

        insert_sql = """
        INSERT INTO responses (
            student_id, session_id, question_id, chosen_answer, is_correct,
            response_time_seconds, answered_at, theta_before, theta_after, theta_change,
            confidence_interval_low, confidence_interval_high, item_parameters,
            response_metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT unique_student_question 
        DO UPDATE SET 
            chosen_answer = EXCLUDED.chosen_answer,
            is_correct = EXCLUDED.is_correct,
            response_time_seconds = EXCLUDED.response_time_seconds,
            session_id = EXCLUDED.session_id,
            answered_at = EXCLUDED.answered_at,
            theta_before = EXCLUDED.theta_before,
            theta_after = EXCLUDED.theta_after,
            theta_change = EXCLUDED.theta_change,
            confidence_interval_low = EXCLUDED.confidence_interval_low,
            confidence_interval_high = EXCLUDED.confidence_interval_high,
            item_parameters = EXCLUDED.item_parameters,
            response_metadata = EXCLUDED.response_metadata
        """

        try:
            with self.db_manager.conn.cursor() as cursor:
                values = []
                for _, row in responses_df.iterrows():
                    is_correct = row.get('is_correct', False)
                    is_correct_int = 1 if is_correct else 0
                    
                    # Convert potential NaN from pandas to None for PostgreSQL
                    def to_db_type(val):
                        return None if pd.isna(val) else val
                        
                    values.append((
                        row['student_id'],
                        row['session_id'],
                        row['question_id'],
                        json.dumps(row.get('chosen_answer', [])),
                        is_correct_int,
                        to_db_type(row.get('response_time_seconds')),
                        to_db_type(row.get('theta_before')),
                        to_db_type(row.get('theta_after')),
                        to_db_type(row.get('theta_change')),
                        to_db_type(row.get('confidence_interval_low')),
                        to_db_type(row.get('confidence_interval_high')),
                        json.dumps(to_db_type(row.get('item_parameters', {}))),
                        json.dumps(to_db_type(row.get('response_metadata', {})))
                    ))
                
                cursor.executemany(insert_sql, values)

            self.db_manager.conn.commit()
            logger.info(f"Inserted/updated {len(responses_df)} responses")

        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert responses: {e}")
            raise