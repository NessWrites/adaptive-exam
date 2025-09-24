import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from scipy.integrate import quad
import json
from datetime import datetime

class CATSimulator:
    """
    Enhanced Computerized Adaptive Testing (CAT) Simulator with Combined Score Selection.

    This class manages the logic for an adaptive test, including:
    - Loading a question bank.
    - Combined Score Selection (CSS) with adaptive weighting.
    - Expected A Posteriori (EAP) scoring.
    - Enhanced logging and constraint tracking.
    """
    def __init__(self, qbank_path):
        """Initializes the CAT simulator with a question bank and a test blueprint."""
        self.qbank = pd.read_csv(qbank_path)
        self.remaining_items = self.qbank.copy()
        self.administered_items = []
        self.responses = []
        self.theta = 0.0  # Initial ability estimate
        self.log = []
        self.test_start_time = datetime.now()

        # Define the test blueprint for content balancing (15 questions total)
        self.blueprint = {
            'total_questions': 15,
            'constraints': {
                'topic': {'ANN': 3, 'MLOps': 2, 'Ensemble Models': 2, 'CNN': 2, 'Linear Models':3, 'Statistics':2},
                'cognitive_level': {'Application': 4, 'Analysis': 3, 'Knowledge': 4}
            }
        }
        
        # Weighting schedule parameters
        self.weighting_schedule = {
            'strategy': 'hybrid',  # Options: 'front_load', 'quota_driven', 'hybrid'
            'base_weight_early': 0.1,
            'base_weight_late': 1.0,
            'quota_multiplier': 2.0
        }

    def _irt_3pl(self, theta, a, b, c):
        """Calculates the probability of a correct response using the 3PL IRT model."""
        return c + (1 - c) / (1 + np.exp(-1.7 * a * (theta - b)))

    def _fisher_information(self, theta, a, b, c):
        """Calculates the Fisher Information for a single item at a given theta."""
        p = self._irt_3pl(theta, a, b, c)
        p = np.clip(p, 1e-9, 1 - 1e-9)  # Avoid division by zero or log(0)
        q = 1 - p
        return (1.7**2) * (a**2) * (q / p) * ((p - c)**2 / (1 - c)**2)

    def _likelihood_function(self, theta, responses, administered_params):
        """Calculates the likelihood of the observed responses given a theta."""
        likelihood = 1.0
        for i, u in enumerate(responses):
            a, b, c = administered_params[i]
            p = self._irt_3pl(theta, a, b, c)
            p = np.clip(p, 1e-9, 1 - 1e-9)
            if u == 1:
                likelihood *= p
            else:
                likelihood *= (1 - p)
        return likelihood

    def _update_theta_eap(self):
        """
        Update the ability estimate (theta) using Expected A Posteriori (EAP).
        EAP is the mean of the posterior distribution, calculated via numerical integration.
        """
        if not self.responses:
            return

        administered_params = [
            (item['a'], item['b'], item['c']) for item in self.administered_items
        ]
        
        def numerator_integrand(t):
            likelihood = self._likelihood_function(t, self.responses, administered_params)
            prior = norm.pdf(t, 0, 2)
            return t * likelihood * prior

        def denominator_integrand(t):
            likelihood = self._likelihood_function(t, self.responses, administered_params)
            prior = norm.pdf(t, 0, 2)
            return likelihood * prior
        
        integration_range = [-4, 4]
        numerator, _ = quad(numerator_integrand, *integration_range)
        denominator, _ = quad(denominator_integrand, *integration_range)

        if denominator > 1e-9:
            self.theta = numerator / denominator

    def _get_constraint_status(self):
        """Returns current constraint fulfillment status."""
        status = {}
        administered_df = pd.DataFrame(self.administered_items) if self.administered_items else pd.DataFrame()
        
        for constraint_type, constraints in self.blueprint['constraints'].items():
            status[constraint_type] = {}
            for value, required in constraints.items():
                if not administered_df.empty:
                    fulfilled = administered_df[administered_df[constraint_type] == value].shape[0]
                else:
                    fulfilled = 0
                status[constraint_type][value] = {
                    'fulfilled': fulfilled,
                    'required': required,
                    'ratio': fulfilled / required if required > 0 else 1.0,
                    'remaining': max(0, required - fulfilled)
                }
        return status

    def _calculate_adaptive_weight(self):
        """Calculate adaptive weight based on test progress and constraint urgency."""
        q_administered = len(self.administered_items)
        q_total = self.blueprint['total_questions']
        q_remaining = q_total - q_administered
        
        if q_remaining <= 0:
            return 0.0
            
        progress_ratio = q_administered / q_total
        
        if self.weighting_schedule['strategy'] == 'front_load':
            # Start high on info, end high on content
            base_weight = (self.weighting_schedule['base_weight_early'] + 
                          progress_ratio * (self.weighting_schedule['base_weight_late'] - 
                                          self.weighting_schedule['base_weight_early']))
        
        elif self.weighting_schedule['strategy'] == 'quota_driven':
            # Weight based on most urgent constraint
            constraint_status = self._get_constraint_status()
            max_urgency = 0.0
            for constraint_type, constraints in constraint_status.items():
                for value, status in constraints.items():
                    if status['remaining'] > 0:
                        urgency = status['remaining'] / q_remaining
                        max_urgency = max(max_urgency, urgency)
            base_weight = max_urgency * self.weighting_schedule['quota_multiplier']
        
        else:  # hybrid
            # Combine progress-based and quota-driven weighting
            progress_weight = (self.weighting_schedule['base_weight_early'] + 
                             progress_ratio * (self.weighting_schedule['base_weight_late'] - 
                                             self.weighting_schedule['base_weight_early']))
            
            constraint_status = self._get_constraint_status()
            max_urgency = 0.0
            for constraint_type, constraints in constraint_status.items():
                for value, status in constraints.items():
                    if status['remaining'] > 0:
                        urgency = status['remaining'] / q_remaining
                        max_urgency = max(max_urgency, urgency)
            
            quota_weight = max_urgency * self.weighting_schedule['quota_multiplier']
            base_weight = progress_weight + quota_weight
        
        return base_weight

    def _calculate_urgency_contribution(self, item):
        """Calculate urgency contribution for a specific item."""
        q_administered = len(self.administered_items)
        q_total = self.blueprint['total_questions']
        q_remaining = q_total - q_administered
        
        if q_remaining <= 0:
            return 0.0
            
        constraint_status = self._get_constraint_status()
        total_contribution = 0.0
        
        # Check each constraint type
        for constraint_type, constraints in self.blueprint['constraints'].items():
            if constraint_type in item and item[constraint_type] in constraints:
                value = item[constraint_type]
                status = constraint_status[constraint_type][value]
                
                if status['remaining'] > 0:
                    # Urgency is remaining requirement divided by remaining slots
                    urgency = status['remaining'] / q_remaining
                    total_contribution += urgency
        
        return total_contribution

    def _apply_diversity_penalty(self, item, base_score):
        """Apply penalty for recently administered items to encourage diversity."""
        if len(self.administered_items) < 2:
            return base_score
            
        # Check if this exact item was administered recently
        recent_items = self.administered_items[-3:]  # Last 3 items
        for recent_item in recent_items:
            if recent_item['item_id'] == item['item_id']:
                return base_score * 0.1  # Heavy penalty for exact repeats
        
        # Check for similar items (same topic + cognitive level)
        similarity_penalty = 1.0
        recent_combinations = [(ri['topic'], ri['cognitive_level']) for ri in recent_items]
        current_combo = (item['topic'], item['cognitive_level'])
        
        if current_combo in recent_combinations:
            penalty_factor = recent_combinations.count(current_combo) * 0.3
            similarity_penalty = max(0.4, 1.0 - penalty_factor)
        
        return base_score * similarity_penalty

    def select_next_item(self):
        """
        Selects the next best item using Combined Score Selection with Adaptive Weighting.
        """
        if self.remaining_items.empty:
            return None, "No items remaining."

        q_total = self.blueprint['total_questions']
        q_administered = len(self.administered_items)
        
        if q_administered >= q_total:
            return None, "Test length reached."

        # Calculate adaptive weight
        adaptive_weight = self._calculate_adaptive_weight()
        
        # Calculate combined scores for all remaining items
        scores = []
        for idx, item in self.remaining_items.iterrows():
            # Fisher Information
            fisher_info = self._fisher_information(self.theta, item['a'], item['b'], item['c'])
            
            # Urgency Contribution
            urgency_contrib = self._calculate_urgency_contribution(item)
            
            # Combined Score
            combined_score = fisher_info + adaptive_weight * urgency_contrib
            
            # Apply diversity penalty
            final_score = self._apply_diversity_penalty(item, combined_score)
            
            scores.append({
                'item_id': item['item_id'],
                'fisher_info': fisher_info,
                'urgency_contrib': urgency_contrib,
                'combined_score': combined_score,
                'final_score': final_score,
                'item': item
            })
        
        # Select item with highest final score
        best_item_data = max(scores, key=lambda x: x['final_score'])
        next_item = best_item_data['item']
        
        # Create detailed selection reasoning
        selection_reason = (
            f"Combined Score Selection: "
            f"Fisher={best_item_data['fisher_info']:.3f}, "
            f"Urgency={best_item_data['urgency_contrib']:.3f}, "
            f"Weight={adaptive_weight:.3f}, "
            f"Final Score={best_item_data['final_score']:.3f}"
        )
        
        return next_item, selection_reason

    def administer_item(self, item_id, user_answer_keys):
        """Records a response, updates theta, and logs the process with enhanced details."""
        item = self.qbank[self.qbank['item_id'] == item_id].iloc[0].to_dict()
        
        # Check correctness
        correct_keys = str(item['correct_answer']).split(';')
        is_correct = sorted(user_answer_keys) == sorted(correct_keys)
        
        theta_before = self.theta
        
        # Update state
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Remove item from the remaining pool
        item_index = self.remaining_items[self.remaining_items['item_id'] == item_id].index
        self.remaining_items.drop(item_index, inplace=True)
        
        # Update ability estimate
        self._update_theta_eap()
        theta_after = self.theta
        
        # Get current constraint status
        constraint_status = self._get_constraint_status()

        # Enhanced log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': item_id,
            'item_content': item['content'],
            'item_topic': item['topic'],
            'item_cognitive_level': item['cognitive_level'],
            'item_difficulty_b': item['b'],
            'item_discrimination_a': item['a'],
            'item_guessing_c': item['c'],
            'user_response': user_answer_keys,
            'correct_answer': correct_keys,
            'response_correct': 'Yes' if is_correct else 'No',
            'theta_before': theta_before,
            'theta_after': theta_after,
            'theta_change': theta_after - theta_before,
            'constraint_status': constraint_status,
            'timestamp': datetime.now().isoformat()
        }
        self.log.append(log_entry)

    def get_summary_stats(self):
        """Get summary statistics for the current test session."""
        if not self.administered_items:
            return {}
            
        administered_df = pd.DataFrame(self.administered_items)
        
        stats = {
            'total_questions': len(self.administered_items),
            'correct_answers': sum(self.responses),
            'accuracy': sum(self.responses) / len(self.responses) if self.responses else 0,
            'current_theta': self.theta,
            'topic_distribution': administered_df['topic'].value_counts().to_dict(),
            'cognitive_level_distribution': administered_df['cognitive_level'].value_counts().to_dict(),
            'difficulty_range': {
                'min': administered_df['b'].min(),
                'max': administered_df['b'].max(),
                'mean': administered_df['b'].mean()
            }
        }
        return stats

    def save_session_log(self, filename=None):
        """Save the complete session log to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cat_session_{timestamp}.json"
        
        session_data = {
            'test_info': {
                'start_time': self.test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'blueprint': self.blueprint,
                'weighting_schedule': self.weighting_schedule
            },
            'final_results': {
                'final_theta': self.theta,
                'total_questions': len(self.administered_items),
                'summary_stats': self.get_summary_stats()
            },
            'detailed_log': self.log
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        return filename