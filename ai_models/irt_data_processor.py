import pandas as pd
import json
import logging
from typing import Dict, Optional
from pathlib import Path
import uuid
from database import DatabaseManager
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayesianIRTDataProcessor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def get_existing_students(self) -> pd.DataFrame:
        """Get existing students from database"""
        query = "SELECT student_id, name, email FROM students"
        try:
            with self.db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Failed to fetch existing students: {e}")
            return pd.DataFrame(columns=['student_id', 'name', 'email'])
    
    def get_existing_questions(self) -> pd.DataFrame:
        """Get existing questions from database"""
        query = """SELECT question_id, question_text, img_url, marks, type, 
                          n_choices, correct_answer, parameter_a, parameter_b, parameter_c 
                   FROM questions"""
        try:
            with self.db_manager.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Failed to fetch existing questions: {e}")
            return pd.DataFrame(columns=['question_id', 'question_text', 'img_url', 'marks', 'type', 
                                       'n_choices', 'correct_answer', 'parameter_a', 'parameter_b', 'parameter_c'])
    
    def get_student_current_theta(self, student_id: int) -> Optional[float]:
        """Get current Bayesian theta estimate for a student"""
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
        """Process JSON file with Bayesian IRT focus"""
        from helpers import parse_score, parse_marks, parse_datetime, parse_options_metadata, clean_question_text, extract_choice_info, extract_chosen_answer
        
        with open(file_path) as f:
            data = json.load(f)

        rows = []
        for student_name, student_data in data.items():
            email = student_data.get("email")
            obtained_score, total_score = parse_score(student_data.get("score", ""))
            submitted_at = parse_datetime(student_data.get("submitted_at", ""))
            plagiarism = student_data.get("plagiarism")
            status = student_data.get("status")
            submission_url = student_data.get("submission_url")

            for q in student_data.get("questions", []):
                question_text = clean_question_text(q.get("question_text"))
                
                n_choices, correct_answer = extract_choice_info(q)
                chosen_answer = extract_chosen_answer(q, n_choices, correct_answer)
                
                is_correct = 1 if chosen_answer == correct_answer else 0
                
                response_time = q.get("response_time_seconds", q.get("response_time"))
                
                param_a = q.get("parameter_a") or q.get("discrimination")
                param_b = q.get("parameter_b") or q.get("difficulty") 
                param_c = q.get("parameter_c") or q.get("guessing")
                
                rows.append({
                    "student_name": student_name,
                    "email": email,
                    "obtained_score": obtained_score,
                    "total_score": total_score,
                    "submitted_at": submitted_at,
                    "plagiarism": plagiarism,
                    "status": status,
                    "submission_url": submission_url,
                    "question_number": q.get("question_number"),
                    "question_text": question_text,
                    "img_url": q.get("img_url"),
                    "marks": parse_marks(q.get("marks", "")),
                    "type": q.get("type"),
                    "n_choices": n_choices,
                    "correct_answer": correct_answer,
                    "chosen_answer": chosen_answer,
                    "is_correct": is_correct,
                    "response_time_seconds": response_time,
                    "parameter_a": param_a,
                    "parameter_b": param_b,
                    "parameter_c": param_c,
                    "options_metadata": parse_options_metadata(q.get("options_metadata", "")),
                })

        return pd.DataFrame(rows)
    
    def identify_new_students(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Identify students that don't exist in database"""
        existing_students = self.get_existing_students()
        
        unique_students = new_data[["student_name", "email"]].drop_duplicates()
        
        if existing_students.empty:
            new_students = unique_students
        else:
            new_students = unique_students[~unique_students['email'].isin(existing_students['email'])]
        
        return new_students
    
    def identify_new_questions(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Identify questions that don't exist in database"""
        existing_questions = self.get_existing_questions()
        
        question_cols = ["question_text", "img_url", "marks", "type", "n_choices", "correct_answer",
                        "parameter_a", "parameter_b", "parameter_c"]
        unique_questions = new_data[question_cols].drop_duplicates()
        
        if existing_questions.empty:
            new_questions = unique_questions
        else:
            existing_questions['composite_key'] = (
                existing_questions['question_text'].fillna('') + '|' +
                existing_questions['img_url'].fillna('') + '|' +
                existing_questions['marks'].astype(str) + '|' +
                existing_questions['type'].fillna('')
            )
            
            unique_questions['composite_key'] = (
                unique_questions['question_text'].fillna('') + '|' +
                unique_questions['img_url'].fillna('') + '|' +
                unique_questions['marks'].astype(str) + '|' +
                unique_questions['type'].fillna('')
            )
            
            new_questions = unique_questions[
                ~unique_questions['composite_key'].isin(existing_questions['composite_key'])
            ].drop('composite_key', axis=1)
        
        if not new_questions.empty:
            new_questions = new_questions.copy()
            new_questions["question_id"] = ["Q" + str(uuid.uuid4())[:8] for _ in range(len(new_questions))]
        
        return new_questions
    
    def insert_students(self, students_df: pd.DataFrame) -> Dict[str, int]:
        """Insert new students and return email->student_id mapping"""
        if students_df.empty:
            logger.info("No new students to insert")
            return {}
        
        insert_sql = """
        INSERT INTO students (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email) 
        DO UPDATE SET name = EXCLUDED.name
        RETURNING student_id, email
        """
        
        student_mapping = {}
        try:
            with self.db_manager.conn.cursor() as cursor:
                for _, row in students_df.iterrows():
                    cursor.execute(insert_sql, (row['student_name'], row['email']))
                    result = cursor.fetchone()
                    if result:
                        student_mapping[row['email']] = result[0]
                
                self.db_manager.conn.commit()
                logger.info(f"Inserted/updated {len(students_df)} students")
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert students: {e}")
            raise
        
        return student_mapping
    
    def insert_questions(self, questions_df: pd.DataFrame) -> Dict[str, str]:
        """Insert new questions optimized for Bayesian IRT"""
        if questions_df.empty:
            logger.info("No new questions to insert")
            return {}
        
        insert_sql = """
        INSERT INTO questions (question_id, question_text, img_url, marks, type, 
                             n_choices, correct_answer, parameter_a, parameter_b, parameter_c)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING question_id
        """
        
        question_mapping = {}
        try:
            with self.db_manager.conn.cursor() as cursor:
                for _, row in questions_df.iterrows():
                    cursor.execute(insert_sql, (
                        row['question_id'], row['question_text'], row['img_url'],
                        row['marks'], row['type'], row['n_choices'], row['correct_answer'],
                        row['parameter_a'], row['parameter_b'], row['parameter_c']
                    ))
                    
                    composite_key = f"{row['question_text']}|{row['img_url']}|{row['marks']}|{row['type']}"
                    question_mapping[composite_key] = row['question_id']
                
                self.db_manager.conn.commit()
                logger.info(f"Inserted {len(questions_df)} questions")
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert questions: {e}")
            raise
        
        return question_mapping
    
    def create_test_session(self, student_id: int, session_type: str = "assessment") -> int:
        """Create test session for Bayesian analysis"""
        insert_sql = """
        INSERT INTO test_sessions (student_id, session_type, selection_strategy)
        VALUES (%s, %s, %s)
        RETURNING session_id
        """
        try:
            with self.db_manager.conn.cursor() as cursor:
                cursor.execute(insert_sql, (student_id, session_type, 'random'))
                session_id = cursor.fetchone()[0]
                self.db_manager.conn.commit()
                return session_id
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to create test session: {e}")
            raise
    
    def insert_responses(self, responses_data: pd.DataFrame):
        """Insert responses optimized for Bayesian IRT"""
        if responses_data.empty:
            return
        
        insert_sql = """
        INSERT INTO responses (session_id, question_id, student_id, chosen_answer, 
                             is_correct, response_time_seconds, answered_at,
                             item_parameters, response_metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with self.db_manager.conn.cursor() as cursor:
                for _, row in responses_data.iterrows():
                    item_params = {
                        'a': row.get('parameter_a'),
                        'b': row.get('parameter_b'),
                        'c': row.get('parameter_c'),
                        'n_choices': row['n_choices'],
                        'correct_answer': row['correct_answer']
                    }
                    
                    response_meta = {
                        'options_metadata': row.get('options_metadata', {}),
                        'question_type': row.get('type'),
                        'marks': row.get('marks')
                    }
                    
                    cursor.execute(insert_sql, (
                        row['session_id'], row['question_id'], row['student_id'],
                        row['chosen_answer'], row['is_correct'],
                        row.get('response_time_seconds'), row.get('submitted_at'),
                        json.dumps(item_params), json.dumps(response_meta)
                    ))
                
                self.db_manager.conn.commit()
                logger.info(f"Inserted {len(responses_data)} responses")
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Failed to insert responses: {e}")
            raise