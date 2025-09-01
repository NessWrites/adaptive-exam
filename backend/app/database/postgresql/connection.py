from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv
import os
from typing import Dict, Any
load_dotenv()

# Set up logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

\
# Database URL (adjust password if needed)
DATABASE_URL = f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')} host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')}"


def get_db_connection_params() -> Dict[str, Any]:
    """Get database connection parameters from environment variables"""
    load_dotenv()

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "dbname": os.getenv("DB_NAME"),     # psycopg2 expects "dbname"
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatabaseManager:
    def __init__(self, connection_params: dict[str,str | int] ):
        """_summary_

		Args:
			connection_params (dict[str,str]): host, database, user, password, port
		"""
        self.connection_params = connection_params
        self.conn = None
        
    def connect(self):
        """Establish Database Connection"""
        try:
            self.conn = self.conn = psycopg2.connect(DATABASE_URL)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    def close(self):
        """Close database connection """
        if self.conn:
            self.conn.close()
            logger.info("Database connection is closed")
    
    def create_table_if_not_exist(self):
        """Create table optimized for Bayesian IRT Analysis"""
        if self.conn is None:
            logger.error("Database connection is not available")
            raise ConnectionError("Database connection is not available")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS students(
            student_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            enrollment_date DATE DEFAULT CURRENT_DATE
		);
  
        CREATE TABLE IF NOT EXISTS questions(
            question_id VARCHAR(50) PRIMARY KEY,
            question_text TEXT,
            img_url TEXT,
            marks INTEGER,
            type VARCHAR(100),
            n_choices INTEGER NOT NULL DEFAULT 1,
            correct_answer INTEGER,
            options_metadata JSONB,
            parameter_a FLOAT,
            parameter_b FLOAT,
            parameter_c FLOAT,
            difficulty_level VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS test_sessions (
            session_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
            start_time TIMESTAMP DEFAULT NOW(),
            end_time TIMESTAMP,
            selection_strategy VARCHAR(255) DEFAULT 'random',
            selection_type VARCHAR(100) DEFAULT 'assessment',
            current_item_pool JSONB,
            metadata JSONB
        );
        
        CREATE TABLE IF NOT EXISTS responses (
            response_id SERIAL PRIMARY KEY,
            session_id INTEGER REFERENCES test_sessions(session_id) ON DELETE CASCADE,
            question_id VARCHAR(50) REFERENCES questions(question_id),
            student_id INTEGER REFERENCES students(student_id),
            chosen_answer INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            response_time_seconds FLOAT,
            answered_at TIMESTAMP DEFAULT NOW(),
            theta_before FLOAT,
            theta_after FLOAT,
            theta_change FLOAT,
            confidence_interval_low FLOAT,
            confidence_interval_high FLOAT,
            item_parameters JSONB,
            response_metadata JSONB
        );
        
        CREATE TABLE IF NOT EXISTS bayesian_ability_estimates (
            estimate_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
            theta_mean FLOAT NOT NULL,
            theta_std FLOAT,
            theta_samples JSONB,
            posterior_summary JSONB,
            model_version VARCHAR(100) DEFAULT 'bayesian_irt_v1',
            estimation_method VARCHAR(100) DEFAULT 'mcmc',
            n_samples INTEGER,
            convergence_diagnostics JSONB,
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS question_parameters (
            param_id SERIAL PRIMARY KEY,
            question_id VARCHAR(50) REFERENCES questions(question_id) ON DELETE CASCADE,
            parameter_a_mean FLOAT,
            parameter_a_std FLOAT,
            parameter_b_mean FLOAT,
            parameter_b_std FLOAT,
            parameter_c_mean FLOAT,
            parameter_c_std FLOAT,
            parameter_samples JSONB,
            model_version VARCHAR(100) DEFAULT 'bayesian_irt_v1',
            estimation_method VARCHAR(100) DEFAULT 'mcmc',
            n_samples INTEGER,
            convergence_diagnostics JSONB,
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
         -- Legacy submissions table for backward compatibility
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(student_id),
            question_id VARCHAR(50) REFERENCES questions(question_id),
            obtained_score INTEGER,
            total_score INTEGER,
            submitted_at TIMESTAMP,
            plagiarism VARCHAR(100),
            status VARCHAR(100),
            submission_url TEXT,
            selected_options TEXT,
            is_correct BOOLEAN,
            theta_estimate FLOAT,
            theta_change FLOAT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(student_id, question_id, submitted_at)
        );
        
        CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);
        CREATE INDEX IF NOT EXISTS idx_responses_student ON responses(student_id);
        CREATE INDEX IF NOT EXISTS idx_responses_question ON responses(question_id);
        CREATE INDEX IF NOT EXISTS idx_responses_session ON responses(session_id);
        CREATE INDEX IF NOT EXISTS idx_bayesian_estimates_student ON bayesian_ability_estimates(student_id);
        CREATE INDEX IF NOT EXISTS idx_question_params_question ON question_parameters(question_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_student_question ON submissions(student_id, question_id);
        
        """  
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.conn.commit()
                logger.info("Bayesian IRT tables created/verified successfully")
        except Exception as e:
            if self.conn is not None:
                self.conn.rollback()
            logger.error(f"Failed to create tables: {e}")
            raise

            