import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from scipy.integrate import quad

class CATSimulator:
    """
    A Computerized Adaptive Testing (CAT) Simulator.

    This class manages the logic for an adaptive test, including:
    - Loading a question bank.
    - Selecting items based on content balancing (SCS) and information maximization.
    - Estimating examinee ability using Expected A Posteriori (EAP) scoring.
    - Maintaining the state of the test for a single session.
    """
    def __init__(self, qbank_path):
        """Initializes the CAT simulator with a question bank and a test blueprint."""
        self.qbank = pd.read_csv(qbank_path)
        self.remaining_items = self.qbank.copy()
        self.administered_items = []
        self.responses = []
        self.theta = 0.0  # Initial ability estimate
        self.log = []

        # Define the test blueprint for content balancing (15 questions total)
        self.blueprint = {
            'total_questions': 15,
            'constraints': {
                'topic': {'ANN': 3, 'MLOps': 2, 'Ensemble Models': 2, 'CNN': 2},
                'cognitive_level': {'Application': 4, 'Analysis': 3}
            }
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
        
        # Numerator: integral of theta * L(theta) * prior(theta)
        # Denominator: integral of L(theta) * prior(theta)
        
        def numerator_integrand(t):
            likelihood = self._likelihood_function(t, self.responses, administered_params)
            prior = norm.pdf(t, 0, 2) # Using a slightly wider prior
            return t * likelihood * prior

        def denominator_integrand(t):
            likelihood = self._likelihood_function(t, self.responses, administered_params)
            prior = norm.pdf(t, 0, 2)
            return likelihood * prior
        
        # Perform numerical integration over a plausible range of theta
        integration_range = [-4, 4]
        numerator, _ = quad(numerator_integrand, *integration_range)
        denominator, _ = quad(denominator_integrand, *integration_range)

        if denominator > 1e-9: # Avoid division by zero
            self.theta = numerator / denominator

    def select_next_item(self):
        """
        Selects the next best item using Sequential Constraint Satisfaction (SCS).
        1. Calculates urgency for all content constraints.
        2. Filters the item pool by the most urgent constraint.
        3. Selects the item with Maximum Fisher Information from the filtered pool.
        """
        if self.remaining_items.empty:
            return None, "No items remaining."

        # --- SCS Logic ---
        urgency_scores = {}
        q_num_total = self.blueprint['total_questions']
        q_num_administered = len(self.administered_items)
        remaining_in_test = q_num_total - q_num_administered

        if remaining_in_test <= 0:
             return None, "Test length reached."

        # 1. Calculate urgency for all constraints
        for constraint_type, constraints in self.blueprint['constraints'].items():
            for value, required_count in constraints.items():
                administered_df = pd.DataFrame(self.administered_items)
                if not administered_df.empty:
                    fulfilled_count = administered_df[administered_df[constraint_type] == value].shape[0]
                else:
                    fulfilled_count = 0
                
                if fulfilled_count < required_count:
                    urgency = (required_count - fulfilled_count) / remaining_in_test
                    urgency_scores[f"{constraint_type}|{value}"] = urgency
        
        # 2. Find the most urgent constraint and filter the pool
        filtered_pool = self.remaining_items
        selection_reason = "No urgent constraints. Selected for max info from all remaining items."

        if urgency_scores:
            # Sort by urgency, descending
            most_urgent = sorted(urgency_scores.items(), key=lambda item: item[1], reverse=True)
            
            for constraint_key, _ in most_urgent:
                constraint_type, value = constraint_key.split('|')
                
                # Try to filter by the most urgent constraint
                candidate_pool = self.remaining_items[self.remaining_items[constraint_type] == value]
                
                if not candidate_pool.empty:
                    filtered_pool = candidate_pool
                    selection_reason = (f"Urgent constraint: '{value}' for '{constraint_type}'. "
                                      f"Pool filtered to {len(filtered_pool)} items.")
                    break # Found a workable constraint

        # --- Maximum Fisher Information Logic ---
        # 3. Calculate information for all items in the (potentially filtered) pool
        filtered_pool['info'] = filtered_pool.apply(
            lambda row: self._fisher_information(self.theta, row['a'], row['b'], row['c']),
            axis=1
        )
        
        # Select the item with the highest information
        if filtered_pool.empty: # Fallback if filtering results in an empty set
             self.remaining_items['info'] = self.remaining_items.apply(
                lambda row: self._fisher_information(self.theta, row['a'], row['b'], row['c']), axis=1)
             best_item_id = self.remaining_items['info'].idxmax()
             next_item = self.remaining_items.loc[best_item_id]
             selection_reason += " (Fallback to all items as filtered pool was empty)"
        else:
             best_item_id = filtered_pool['info'].idxmax()
             next_item = filtered_pool.loc[best_item_id]

        return next_item, selection_reason

    def administer_item(self, item_id, user_answer_keys):
        """Records a response, updates theta, and logs the process."""
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

        # Log the entire step
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': item_id,
            'item_content': item['content'],
            'item_difficulty_b': item['b'],
            'response_correct': 'Yes' if is_correct else 'No',
            'theta_before': theta_before,
            'theta_after': theta_after,
            'theta_change': theta_after - theta_before
        }
        self.log.append(log_entry)
