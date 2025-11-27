import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class ConventionalTestSimulator:
    """
    A Conventional Test Simulator that selects 20 questions at random.
    
    This class demonstrates the traditional approach to testing where questions
    are selected randomly without considering item difficulty, discrimination,
    or student ability estimates.
    """
    
    def __init__(self):
        """Initialize the conventional test simulator with database connection."""
        
        # Get the current working directory and project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        
        # Load environment variables from .env file - try most likely location first
        env_paths = [
            '.env',  # Current directory
            '../../backend/.env',  # Most likely location
            os.path.join(project_root, 'backend/.env'),
            '../.env',
            '../../.env',
            '../../../backend/.env',
            '/home/ness/FuseMachines/projects/adaptive-exam/backend/.env'
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                env_loaded = True
                break
        
        # Database connection parameters
        self.db_params = {
            "host": os.getenv("DB_HOST", "localhost"),
            "dbname": os.getenv("DB_NAME", "adaptive_exam_db"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": int(os.getenv("DB_PORT", "5432")),
        }
        
        # Debug: Print connection parameters (without password)
        print(f"Connecting to database: {self.db_params['host']}:{self.db_params['port']}/{self.db_params['dbname']} as {self.db_params['user']}")
        
        # Connect to database and load questions
        self.conn = None
        self.connect_to_database()
        
        # Load all available questions
        self.full_qbank = self.load_questions_from_database()
        
        # Initialize test state
        self.test_length = 20
        self.administered_items = []
        self.responses = []
        
        # Randomly select 20 questions upfront
        self.selected_questions = self.select_random_questions()
        
        # Logging
        self.log = []
        
        print(f"Initialized Conventional Test with {len(self.selected_questions)} randomly selected questions")
    
    def connect_to_database(self):
        """Connect to the PostgreSQL database."""
        try:
            # Check if password is provided
            if not self.db_params.get('password'):
                raise ValueError("Database password not provided. Please set DB_PASSWORD in .env file or environment variables.")
            
            self.conn = psycopg2.connect(**self.db_params)
            print("Connected to database successfully")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            print("\nTroubleshooting steps:")
            print("1. Make sure PostgreSQL is running")
            print("2. Check your .env file has correct DB_PASSWORD")
            print("3. Verify database 'adaptive_exam_db' exists")
            print("4. Ensure user has proper permissions")
            raise
    
    def load_questions_from_database(self):
        """Load questions from the database."""
        if not self.conn:
            raise ConnectionError("Database connection not available")
        
        query = """
        SELECT 
            question_id,
            question_text as content,
            img_url,
            marks,
            type as question_type,
            n_choices,
            correct_answer,
            options_metadata,
            parameter_a as a,
            parameter_b as b,
            parameter_c as c,
            topic_dimension,
            cognitive_dimension
        FROM questions 
        WHERE parameter_a IS NOT NULL AND parameter_b IS NOT NULL AND parameter_c IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 200
        """
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
            if not results:
                raise ValueError("No questions found in database with IRT parameters")
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Add item_id for compatibility
            df['item_id'] = df['question_id']
            
            # Add topic and cognitive_level columns for compatibility
            df['topic'] = df['topic_dimension']
            df['cognitive_level'] = df['cognitive_dimension']
            
            print(f"Loaded {len(df)} questions from database")
            return df
            
        except Exception as e:
            print(f"Failed to load questions from database: {e}")
            raise
    
    def select_random_questions(self):
        """Select 20 questions randomly from the available pool."""
        if len(self.full_qbank) < self.test_length:
            raise ValueError(f"Not enough questions available. Need {self.test_length}, have {len(self.full_qbank)}")
        
        # Randomly select questions
        selected_indices = np.random.choice(len(self.full_qbank), size=self.test_length, replace=False)
        selected_questions = self.full_qbank.iloc[selected_indices].copy()
        
        # Reset index for easier iteration
        selected_questions.reset_index(drop=True, inplace=True)
        
        return selected_questions
    
    def select_next_item(self):
        """Select the next item from the pre-selected questions."""
        current_index = len(self.administered_items)
        
        if current_index >= len(self.selected_questions):
            return None, "Test completed - all questions administered"
        
        # Get the next question from our pre-selected list
        next_item = self.selected_questions.iloc[current_index].to_dict()
        reason = f"Conventional: Random question {current_index + 1} of {self.test_length}"
        
        return next_item, reason
    
    def administer_item(self, item_id, user_answer_keys):
        """Record response for conventional test."""
        # Find the item in our selected questions
        item = None
        for idx, row in self.selected_questions.iterrows():
            if row['item_id'] == item_id:
                item = row.to_dict()
                break
        
        if not item:
            raise ValueError(f"Item {item_id} not found in selected questions")
        
        # Check correctness (same logic as IRT model)
        correct_answer = item['correct_answer']
        
        # Parse correct_answer (which is 1-based in database)
        if isinstance(correct_answer, list):
            correct_answer_list = [int(x) - 1 for x in correct_answer]
        elif isinstance(correct_answer, (int, float)):
            correct_answer_list = [int(correct_answer) - 1]
        else:
            try:
                import json
                parsed = json.loads(str(correct_answer)) if isinstance(correct_answer, str) else correct_answer
                if isinstance(parsed, list):
                    correct_answer_list = [int(x) - 1 for x in parsed]
                else:
                    correct_answer_list = [int(parsed) - 1]
            except:
                correct_answer_list = [0]
        
        # user_answer_keys is already 0-based from Streamlit
        if isinstance(user_answer_keys, (int, float)):
            user_answer_list = [int(user_answer_keys)]
        elif isinstance(user_answer_keys, str):
            user_answer_list = [int(user_answer_keys)]
        else:
            user_answer_list = [int(x) for x in user_answer_keys]
        
        # Compare answers (both are now 0-based)
        is_correct = sorted(user_answer_list) == sorted(correct_answer_list)
        
        # Update test state
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Create log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': item_id,
            'item_content': item['content'],
            'item_topic': item['topic'],
            'item_cognitive_level': item['cognitive_level'],
            'item_discrimination_a': item.get('a'),
            'item_difficulty_b': item.get('b'),
            'item_guessing_c': item.get('c'),
            'response_correct': 'Yes' if is_correct else 'No',
            'model_type': 'Conventional',
            'selection_reason': 'Random selection'
        }
        
        self.log.append(log_entry)
    
    def get_test_statistics(self):
        """Get statistics about the conventional test."""
        if not self.responses:
            return {
                'total_questions': 0,
                'correct_answers': 0,
                'accuracy': 0.0,
                'average_difficulty': 0.0,
                'difficulty_range': (0.0, 0.0),
                'topic_distribution': {},
                'cognitive_distribution': {}
            }
        
        total_questions = len(self.responses)
        correct_answers = sum(self.responses)
        accuracy = correct_answers / total_questions if total_questions > 0 else 0.0
        
        # Calculate difficulty statistics
        difficulties = [item['b'] for item in self.administered_items]
        average_difficulty = np.mean(difficulties) if difficulties else 0.0
        difficulty_range = (min(difficulties), max(difficulties)) if difficulties else (0.0, 0.0)
        
        # Calculate topic distribution
        topic_distribution = {}
        for item in self.administered_items:
            topic = item.get('topic', 'Unknown')
            topic_distribution[topic] = topic_distribution.get(topic, 0) + 1
        
        # Calculate cognitive level distribution
        cognitive_distribution = {}
        for item in self.administered_items:
            cognitive = item.get('cognitive_level', 'Unknown')
            cognitive_distribution[cognitive] = cognitive_distribution.get(cognitive, 0) + 1
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'average_difficulty': average_difficulty,
            'difficulty_range': difficulty_range,
            'topic_distribution': topic_distribution,
            'cognitive_distribution': cognitive_distribution
        }
    
    def close_database_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def export_results(self):
        """Export examinee results in a simple format for CSV storage."""
        total_items = len(self.administered_items)
        correct = sum(self.responses) if total_items > 0 else 0
        accuracy = (correct / total_items) if total_items > 0 else 0.0
        return {
            'timestamp': pd.Timestamp.now(),
            'model_type': 'Conventional',
            'administered_items': [item['item_id'] for item in self.administered_items],
            'responses': self.responses,
            'score_percent': accuracy * 100.0,
            # Optional keys to align with save_results contract
            'dimension_names': [],
            'theta_vector': [],
            'theta_se_vector': [],
            'topic_counts': {},
            'cognitive_counts': {}
        }
