import pandas as pd
import numpy as np
from scipy.stats import norm, multivariate_normal
from scipy.integrate import quad
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class MIRTCATSimulator:
    """
    A Multidimensional Computerized Adaptive Testing (MIRT CAT) Simulator.
    
    This class manages the logic for a multidimensional adaptive test using a Bi-Factor MIRT model with:
    - 1 General factor (all items load on this)
    - 6 Topic factors (ANN, CNN, Ensemble Models, Linear Models, MLOps, Statistics)
    - 3 Cognitive Level factors (Knowledge, Application, Analysis)
    
    Uses compensatory MIRT model with 3PL formulation and shadow test approach for item selection.
    """
    
    def __init__(self, qbank_path, multidimensional_qbank_path):
        """Initialize the MIRT CAT simulator with question banks."""
        # Load the original question bank
        self.qbank = pd.read_csv(qbank_path)
        
        # Load the Q-matrix (multidimensional question bank)
        self.q_matrix = pd.read_csv(multidimensional_qbank_path)
        
        # Merge the banks on item_id
        self.full_qbank = pd.merge(self.qbank, self.q_matrix, on='item_id', suffixes=('', '_qmatrix'))
        
        # Define dimensions
        self.topic_dimensions = ['ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps', 'Statistics']
        self.cognitive_dimensions = ['Knowledge', 'Application', 'Analysis']
        self.all_dimensions = ['General'] + self.topic_dimensions + self.cognitive_dimensions
        self.num_dimensions = len(self.all_dimensions)
        
        # Initialize test state
        self.remaining_items = self.full_qbank.copy()
        self.administered_items = []
        self.responses = []
        
        # Initialize 10-dimensional theta vector (all start at 0)
        self.theta_vector = np.zeros(self.num_dimensions)
        self.theta_se_vector = np.ones(self.num_dimensions)  # Standard errors
        
        # Content constraint tracking
        self.topic_counts = {topic: 0 for topic in self.topic_dimensions}
        self.cognitive_counts = {level: 0 for level in self.cognitive_dimensions}
        
        # Test configuration
        self.test_length = 15
        self.min_items_per_topic = 2
        
        # Logging
        self.log = []
        
        print(f"Initialized MIRT CAT with {len(self.full_qbank)} items across {self.num_dimensions} dimensions")
    
    def _mirt_3pl_probability(self, theta_vector, item_row):
        """
        Calculate the probability of correct response using multidimensional 3PL model.
        P(θ) = c + (1-c) / (1 + exp(-1.7 * sum(a_j * θ_j) + b))
        """
        # Extract discrimination parameters for each dimension
        a_vector = np.array([item_row[dim] * item_row['a'] for dim in self.all_dimensions])
        b = item_row['b']
        c = item_row['c']
        
        # Calculate the linear combination
        linear_combination = np.sum(a_vector * theta_vector) - 1.7 * b
        
        # Apply 3PL formula
        probability = c + (1 - c) / (1 + np.exp(-1.7 * linear_combination))
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
        likelihood = 1.0
        for i, response in enumerate(responses):
            item = administered_items[i]
            p = self._mirt_3pl_probability(theta_vector, item)
            if response == 1:
                likelihood *= p
            else:
                likelihood *= (1 - p)
        return likelihood
    
    def _update_theta_eap_multidimensional(self):
        """
        Update the multidimensional ability estimates using Expected A Posteriori (EAP).
        Uses Monte Carlo integration for computational efficiency.
        """
        if not self.responses:
            return
        
        # Monte Carlo integration parameters
        n_samples = 1000
        
        # Prior: Multivariate normal with mean=0, cov=2*I
        prior_mean = np.zeros(self.num_dimensions)
        prior_cov = 2.0 * np.eye(self.num_dimensions)
        
        # Generate samples from prior
        theta_samples = np.random.multivariate_normal(prior_mean, prior_cov, n_samples)
        
        # Calculate likelihoods and weights
        likelihoods = np.array([
            self._likelihood_function(theta, self.responses, self.administered_items)
            for theta in theta_samples
        ])
        
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
        
        # Calculate information for all remaining items
        self.remaining_items['mirt_info'] = self.remaining_items.apply(
            lambda row: self._multidimensional_fisher_information(self.theta_vector, row),
            axis=1
        )
        
        # Determine content constraints based on current progress
        remaining_questions = self.test_length - len(self.administered_items)
        
        # Check which topics need more items
        topics_needing_items = []
        for topic in self.topic_dimensions:
            if self.topic_counts[topic] < self.min_items_per_topic:
                topics_needing_items.append(topic)
        
        # Filter items based on constraints
        if topics_needing_items and remaining_questions > len(topics_needing_items):
            # Prioritize topics that need items
            constraint_reason = f"Content constraint: Need items from {topics_needing_items}"
            
            # Filter to items from needed topics
            mask = self.remaining_items[topics_needing_items].sum(axis=1) > 0
            candidate_items = self.remaining_items[mask]
            
            if candidate_items.empty:
                # Fallback to any remaining item
                candidate_items = self.remaining_items
                constraint_reason = "Fallback: No items available for constrained topics"
        else:
            # No content constraints needed, select from all remaining items
            candidate_items = self.remaining_items
            constraint_reason = "No content constraints active"
        
        # Select item with maximum information from candidates
        if len(self.administered_items) == 0:
            # First question: random selection from top 5 most informative
            top_candidates = candidate_items.nlargest(5, 'mirt_info')
            if not top_candidates.empty:
                selected_item = top_candidates.sample(1).iloc[0]
                reason = "First item: Random from top 5 most informative candidates"
            else:
                return None, "No candidates available"
        else:
            # Subsequent questions: maximum information
            if not candidate_items.empty:
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
        correct_keys = str(item['correct_answer']).split(';')
        is_correct = sorted(user_answer_keys) == sorted(correct_keys)
        
        # Store current theta for logging
        theta_before = self.theta_vector.copy()
        
        # Update test state
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Remove item from remaining pool
        item_index = self.remaining_items[self.remaining_items['item_id'] == item_id].index
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