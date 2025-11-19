import pandas as pd
import numpy as np
from scipy.stats import norm, multivariate_normal
from scipy.integrate import quad
from scipy.optimize import minimize
import warnings
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class MIRTCATSimulator:
    """
    A Multidimensional Computerized Adaptive Testing (MIRT CAT) Simulator.
    
    This class manages the logic for a multidimensional adaptive test using a Bi-Factor MIRT model with:
    - 1 General factor (all items load on this)
    - 6 Topic factors (ANN, CNN, Ensemble Models, Linear Models, MLOps, Statistics)
    - 3 Cognitive Level factors (Knowledge, Application, Analysis)
    
    Uses compensatory MIRT model with 3PL formulation and shadow test approach for item selection.
    """
    
    def __init__(self, model_type='3PL'):
        """Initialize the MIRT CAT simulator with database connection.
        
        Args:
            model_type: '2PL' or '3PL' to select the IRT model type
        """
        self.model_type = model_type  # Store model type
        
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
        
        # Define dimensions from database first
        self.topic_dimensions = self.get_unique_topic_dimensions()
        self.cognitive_dimensions = self.get_unique_cognitive_dimensions()
        self.all_dimensions = ['General'] + self.topic_dimensions + self.cognitive_dimensions
        self.num_dimensions = len(self.all_dimensions)
        
        # Now load questions with dimensions defined
        self.full_qbank = self.load_questions_from_database()
        
        # Initialize test state
        self.remaining_items = self.full_qbank.copy()
        self.administered_items = []
        self.responses = []
        
        # Initialize theta vector (start with neutral values for better initialization)
        self.theta_vector = np.zeros(self.num_dimensions)
        # For first question, we'll use a simple heuristic
        self.theta_se_vector = np.ones(self.num_dimensions)  # Standard errors
        
        # Content constraint tracking
        self.topic_counts = {topic: 0 for topic in self.topic_dimensions}
        self.cognitive_counts = {level: 0 for level in self.cognitive_dimensions}
        
        # Test configuration
        self.test_length = 20
        self.min_items_per_topic = 2
        
        # Logging
        self.log = []
        
        print(f"Initialized MIRT CAT with {len(self.full_qbank)} items across {self.num_dimensions} dimensions")
    
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
        """Load questions from the database and prepare them for CAT."""
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
            parameter_a_2pl as a_2pl,
            parameter_b_2pl as b_2pl,
            topic_dimension,
            cognitive_dimension
        FROM questions 
        WHERE (parameter_a IS NOT NULL AND parameter_b IS NOT NULL AND parameter_c IS NOT NULL)
        OR (parameter_a_2pl IS NOT NULL AND parameter_b_2pl IS NOT NULL)
        ORDER BY RANDOM()
        LIMIT 100
        """
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
            if not results:
                raise ValueError("No questions found in database with IRT parameters")
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            
            # Create Q-matrix based on topic_dimension and cognitive_dimension
            df = self.create_q_matrix(df)
            
            print(f"Loaded {len(df)} questions from database")
            return df
            
        except Exception as e:
            print(f"Failed to load questions from database: {e}")
            raise
    
    def create_q_matrix(self, df):
        """Create Q-matrix based on topic_dimension and cognitive_dimension columns."""
        # Initialize Q-matrix columns
        for topic in self.topic_dimensions:
            df[topic] = 0
        for cognitive in self.cognitive_dimensions:
            df[cognitive] = 0
        
        # Set General factor (all items load on general factor)
        df['General'] = 1
        
        # Set topic-specific loadings
        for idx, row in df.iterrows():
            topic_dim = row['topic_dimension']
            if topic_dim and topic_dim in self.topic_dimensions:
                df.at[idx, topic_dim] = 1
        
        # Set cognitive-level loadings
        for idx, row in df.iterrows():
            cognitive_dim = row['cognitive_dimension']
            if cognitive_dim and cognitive_dim in self.cognitive_dimensions:
                df.at[idx, cognitive_dim] = 1
        
        # Add item_id for compatibility
        df['item_id'] = df['question_id']
        
        # Add topic and cognitive_level columns for compatibility with existing code
        df['topic'] = df['topic_dimension']
        df['cognitive_level'] = df['cognitive_dimension']
        
        return df
    
    def get_unique_topic_dimensions(self):
        """Get unique topic dimensions from database."""
        if not self.conn:
            return ['ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps', 'Statistics']
        
        query = "SELECT DISTINCT topic_dimension FROM questions WHERE topic_dimension IS NOT NULL"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                topics = [row[0] for row in results if row[0]]
                return topics if topics else ['ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps', 'Statistics']
        except Exception as e:
            print(f"Failed to get topic dimensions: {e}")
            return ['ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps', 'Statistics']
    
    def get_unique_cognitive_dimensions(self):
        """Get unique cognitive dimensions from database."""
        if not self.conn:
            return ['Knowledge', 'Application', 'Analysis']
        
        query = "SELECT DISTINCT cognitive_dimension FROM questions WHERE cognitive_dimension IS NOT NULL"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                cognitive = [row[0] for row in results if row[0]]
                return cognitive if cognitive else ['Knowledge', 'Application', 'Analysis']
        except Exception as e:
            print(f"Failed to get cognitive dimensions: {e}")
            return ['Knowledge', 'Application', 'Analysis']
    
    def _mirt_3pl_probability(self, theta_vector, item_row):
        """
        Calculate the probability of correct response using multidimensional 3PL model.
        P(θ) = c + (1-c) / (1 + exp(-1.7 * sum(a_j * θ_j) + b))
        """
        # Extract discrimination parameters for each dimension
        a_vector = np.array([item_row[dim] * item_row['a'] for dim in self.all_dimensions])
        b = item_row['b']
        c = item_row.get('c', 0)  # Use c parameter for 3PL
        
        # Calculate the linear combination
        linear_combination = np.sum(a_vector * theta_vector) - 1.7 * b
        
        # Apply 3PL formula
        probability = c + (1 - c) / (1 + np.exp(-1.7 * linear_combination))
        return np.clip(probability, 1e-9, 1 - 1e-9)
    
    def _mirt_2pl_probability(self, theta_vector, item_row):
        """
        Calculate the probability of correct response using multidimensional 2PL model.
        P(θ) = 1 / (1 + exp(-1.7 * sum(a_j * θ_j) + b))
        """
        # Extract discrimination parameters for each dimension using 2PL parameters
        a_2pl = item_row.get('a_2pl') or item_row.get('a', 1.0)  # Use 3PL 'a' if 2PL not available
        a_vector = np.array([item_row[dim] * a_2pl for dim in self.all_dimensions])
        b_2pl = item_row.get('b_2pl') or item_row.get('b', 0)  # Use 3PL 'b' if 2PL not available
        
        # Calculate the linear combination
        linear_combination = np.sum(a_vector * theta_vector) - 1.7 * b_2pl
        
        # Apply 2PL formula (no guessing parameter)
        probability = 1 / (1 + np.exp(-1.7 * linear_combination))
        return np.clip(probability, 1e-9, 1 - 1e-9)
    
    def _multidimensional_fisher_information(self, theta_vector, item_row):
        """
        Calculate the Fisher Information matrix for a multidimensional item.
        Returns the trace (sum of diagonal elements) as a scalar measure.
        """
        p = self._mirt_3pl_probability(theta_vector, item_row)
        q = 1 - p
        
        # Extract discrimination parameters
        a_vector = np.array([item_row[dim] * item_row['a'] for dim in self.all_dimensions])
        c = item_row['c']
        
        # Calculate the scaling factor
        scaling_factor = (1.7**2) * (q / p) * ((p - c)**2 / (1 - c)**2)
        
        # Fisher Information matrix is a_vector * a_vector.T * scaling_factor
        # Return trace (sum of diagonal) as scalar information measure
        information_matrix = np.outer(a_vector, a_vector) * scaling_factor
        return np.trace(information_matrix)
    
    def _likelihood_function(self, theta_vector, responses, administered_items):
        """Calculate the likelihood of observed responses given theta vector."""
        # Get the appropriate probability function based on model type
        prob_func = self._get_probability_function()
        
        likelihood = 1.0
        for i, response in enumerate(responses):
            item = administered_items[i]
            p = prob_func(theta_vector, item)
            if response == 1:
                likelihood *= p
            else:
                likelihood *= (1 - p)
        return likelihood
    
    def _get_probability_function(self):
        """Return the appropriate probability function based on model type."""
        if self.model_type == '2PL':
            return self._mirt_2pl_probability
        else:
            return self._mirt_3pl_probability
    
    def _update_theta_eap_multidimensional(self):
        """
        Update the multidimensional ability estimates using Expected A Posteriori (EAP).
        Uses Monte Carlo integration for computational efficiency.
        """
        if not self.responses:
            return
        
        # For first response, use simple update based on correctness
        if len(self.responses) == 1:
            # Update theta based on first response: correct -> +0.5, incorrect -> -0.5
            if self.responses[0] == 1:
                # Correct answer: increase ability estimate
                self.theta_vector[0] = 0.5
            else:
                # Incorrect answer: decrease ability estimate  
                self.theta_vector[0] = -0.5
            return
        
        # Monte Carlo integration parameters - reduced for faster computation
        n_samples = 100  # Reduced from 1000 for speed
        
        # Prior: Multivariate normal with mean=0, cov=2*I
        # Theta values typically range from -3 to +3 in IRT, with 0 as neutral
        prior_mean = np.zeros(self.num_dimensions)
        prior_cov = 2.0 * np.eye(self.num_dimensions)
        
        # Generate samples from prior
        theta_samples = np.random.multivariate_normal(prior_mean, prior_cov, n_samples)
        
        # Calculate likelihoods and weights (vectorized for speed)
        likelihoods = np.array([
            self._likelihood_function(theta, self.responses, self.administered_items)
            for theta in theta_samples
        ])
        
        # Avoid numerical issues with very small likelihoods
        likelihoods = np.clip(likelihoods, 1e-100, 1e100)
        
        # Calculate prior densities
        prior_densities = multivariate_normal.pdf(theta_samples, prior_mean, prior_cov)
        
        # Calculate posterior weights
        weights = likelihoods * prior_densities
        weights = weights / np.sum(weights)  # Normalize
        
        # EAP estimates (weighted averages)
        self.theta_vector = np.sum(theta_samples * weights.reshape(-1, 1), axis=0)
        
        # Calculate standard errors (weighted standard deviations)
        variance_matrix = np.sum(weights.reshape(-1, 1, 1) * 
                               (theta_samples.reshape(-1, self.num_dimensions, 1) - 
                                self.theta_vector.reshape(1, self.num_dimensions, 1)) *
                               (theta_samples.reshape(-1, 1, self.num_dimensions) - 
                                self.theta_vector.reshape(1, 1, self.num_dimensions)), axis=0)
        
        self.theta_se_vector = np.sqrt(np.diag(variance_matrix))
    
    def _check_content_constraints(self, item_row):
        """Check if administering this item would violate content constraints."""
        # Find which topic this item belongs to
        item_topic = None
        for topic in self.topic_dimensions:
            if item_row[topic] == 1:
                item_topic = topic
                break
        
        # Find which cognitive level this item belongs to
        item_cognitive = None
        for level in self.cognitive_dimensions:
            if item_row[level] == 1:
                item_cognitive = level
                break
        
        return item_topic, item_cognitive
    
    def _assemble_shadow_test(self):
        """
        Use shadow test approach to select the next item.
        Considers both information maximization and content constraints.
        """
        if len(self.administered_items) >= self.test_length:
            return None, "Test length reached."
        
        if self.remaining_items.empty:
            return None, "No items remaining."
        
        # Select item with maximum information from candidates
        # First, filter out already administered items to prevent repetition
        administered_item_ids = set(item.get('item_id', item.get('question_id')) for item in self.administered_items)
        remaining_filtered = self.remaining_items[~self.remaining_items['item_id'].isin(administered_item_ids)]
        
        if remaining_filtered.empty:
            # Fallback if all items have been administered
            remaining_filtered = self.remaining_items
        
        if len(self.administered_items) == 0:
            # First question: RANDOM selection - NO COMPUTATION, INSTANT!
            # Just pick any remaining item at random
            if not remaining_filtered.empty:
                random_idx = np.random.randint(0, len(remaining_filtered))
                selected_item = remaining_filtered.iloc[random_idx]
                reason = "First item: Instant random selection"
            else:
                return None, "No candidates available"
        else:
            # Determine content constraints based on current progress
            remaining_questions = self.test_length - len(self.administered_items)
            
            # Strategy: Cycle through topics to ensure balanced coverage
            # Find topics that haven't met the minimum requirement
            topics_needing_items = []
            for topic in self.topic_dimensions:
                if self.topic_counts[topic] < self.min_items_per_topic:
                    topics_needing_items.append(topic)
            
            # If there are topics needing items, select from those
            if topics_needing_items:
                # Prioritize topics that need items
                constraint_reason = f"Content constraint: Need items from {topics_needing_items}"
                
                # Filter to items from needed topics (using remaining_filtered, not self.remaining_items)
                mask = remaining_filtered[topics_needing_items].sum(axis=1) > 0
                candidate_items = remaining_filtered[mask]
                
                if candidate_items.empty:
                    # Fallback to any remaining item
                    candidate_items = remaining_filtered
                    constraint_reason = "Fallback: No items available for constrained topics"
            else:
                # All topics have minimum coverage, select from all
                candidate_items = remaining_filtered
                constraint_reason = "All topics covered, maximizing information"
            
            # Calculate information ONLY for candidate items
            if not candidate_items.empty:
                candidate_items['mirt_info'] = candidate_items.apply(
                    lambda row: self._multidimensional_fisher_information(self.theta_vector, row),
                    axis=1
                )
                # Find item with max information
                best_idx = candidate_items['mirt_info'].idxmax()
                selected_item = candidate_items.loc[best_idx]
                reason = f"Max MIRT information from candidates. {constraint_reason}"
            else:
                return None, "No candidates available"
        
        return selected_item.to_dict(), reason
    
    def select_next_item(self):
        """Select the next item using shadow test approach."""
        return self._assemble_shadow_test()
    
    def administer_item(self, item_id, user_answer_keys):
        """Record response, update theta estimates, and track content coverage."""
        # Find the item
        item = self.full_qbank[self.full_qbank['item_id'] == item_id].iloc[0].to_dict()
        
        # Check correctness
        # correct_answer from database is 1-based (e.g., [2] means second option)
        # user_answer_keys from Streamlit is 0-based (e.g., [1] means second option)
        correct_answer = item['correct_answer']
        
        # Parse correct_answer (which is 1-based in database)
        if isinstance(correct_answer, list):
            # Convert from 1-based to 0-based
            correct_answer_list = [int(x) - 1 for x in correct_answer]
        elif isinstance(correct_answer, (int, float)):
            correct_answer_list = [int(correct_answer) - 1]
        else:
            # Try to parse string or other format
            try:
                import json
                parsed = json.loads(str(correct_answer)) if isinstance(correct_answer, str) else correct_answer
                if isinstance(parsed, list):
                    correct_answer_list = [int(x) - 1 for x in parsed]
                else:
                    correct_answer_list = [int(parsed) - 1]
            except:
                correct_answer_list = [0]  # Default to first option
        
        # user_answer_keys is already 0-based from Streamlit
        if isinstance(user_answer_keys, (int, float)):
            user_answer_list = [int(user_answer_keys)]
        elif isinstance(user_answer_keys, str):
            user_answer_list = [int(user_answer_keys)]
        else:
            user_answer_list = [int(x) for x in user_answer_keys]
        
        # Compare answers (both are now 0-based)
        is_correct = sorted(user_answer_list) == sorted(correct_answer_list)
        
        # Store current theta for logging
        theta_before = self.theta_vector.copy()
        
        # Update test state
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Remove item from remaining pool to prevent repetition
        item_index = self.remaining_items[self.remaining_items['item_id'] == item_id].index
        if len(item_index) > 0:
            self.remaining_items.drop(item_index, inplace=True)
        
        # Update content tracking
        item_topic, item_cognitive = self._check_content_constraints(item)
        if item_topic:
            self.topic_counts[item_topic] += 1
        if item_cognitive:
            self.cognitive_counts[item_cognitive] += 1
        
        # Update theta estimates
        self._update_theta_eap_multidimensional()
        theta_after = self.theta_vector.copy()
        
        # Create detailed log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': item_id,
            'item_content': item['content'],
            'item_topic': item['topic'],
            'item_cognitive_level': item['cognitive_level'],
            'item_difficulty_b': item['b'],
            'response_correct': 'Yes' if is_correct else 'No',
            'theta_before': theta_before,
            'theta_after': theta_after,
            'theta_change': theta_after - theta_before,
            'topic_counts': self.topic_counts.copy(),
            'cognitive_counts': self.cognitive_counts.copy()
        }
        
        self.log.append(log_entry)
    
    def get_diagnostic_report(self):
        """Generate comprehensive diagnostic report."""
        dimension_names = self.all_dimensions
        
        report = {
            'theta_estimates': dict(zip(dimension_names, self.theta_vector)),
            'standard_errors': dict(zip(dimension_names, self.theta_se_vector)),
            'content_coverage': {
                'topics': self.topic_counts,
                'cognitive_levels': self.cognitive_counts
            },
            'total_items_administered': len(self.administered_items),
            'overall_score': self.theta_vector[0],  # General factor
            'diagnostic_profile': self._create_diagnostic_profile()
        }
        
        return report
    
    def _create_diagnostic_profile(self):
        """Create diagnostic profile showing relative strengths and weaknesses."""
        profile = {}
        
        # General ability
        general_theta = self.theta_vector[0]
        profile['General Ability'] = {
            'score': general_theta,
            'interpretation': self._interpret_theta(general_theta)
        }
        
        # Topic-specific abilities
        topic_scores = {}
        for i, topic in enumerate(self.topic_dimensions, 1):
            theta = self.theta_vector[i]
            topic_scores[topic] = {
                'score': theta,
                'interpretation': self._interpret_theta(theta),
                'relative_to_general': theta - general_theta
            }
        profile['Topic Abilities'] = topic_scores
        
        # Cognitive-level abilities
        cognitive_scores = {}
        for i, level in enumerate(self.cognitive_dimensions, 7):
            theta = self.theta_vector[i]
            cognitive_scores[level] = {
                'score': theta,
                'interpretation': self._interpret_theta(theta),
                'relative_to_general': theta - general_theta
            }
        profile['Cognitive Abilities'] = cognitive_scores
        
        return profile
    
    def _interpret_theta(self, theta):
        """Interpret theta score in human-readable terms."""
        if theta > 2:
            return "Exceptional"
        elif theta > 1:
            return "Above Average"
        elif theta > -1:
            return "Average"
        elif theta > -2:
            return "Below Average"
        else:
            return "Needs Significant Improvement"
    
    def export_results(self):
        """Export examinee results for storage."""
        results = {
            'timestamp': pd.Timestamp.now(),
            'theta_vector': self.theta_vector.tolist(),
            'theta_se_vector': self.theta_se_vector.tolist(),
            'dimension_names': self.all_dimensions,
            'administered_items': [item['item_id'] for item in self.administered_items],
            'responses': self.responses,
            'topic_counts': self.topic_counts,
            'cognitive_counts': self.cognitive_counts,
            'diagnostic_report': self.get_diagnostic_report(),
            'detailed_log': self.log
        }
        
        return results
    
    def close_database_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed")