import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.integrate import quad

class CATSimulator:
    """
    A Computerized Adaptive Testing (CAT) Simulator.

    This class manages the logic for an adaptive test, including:
    - Loading a question bank.
    - Selecting items based on information maximization.
    - Estimating examinee ability using Expected A Posteriori (EAP) scoring.
    - Maintaining the state of the test for a single session.
    """
    def __init__(self, qbank_path):
        """Initializes the CAT simulator with a question bank."""
        self.qbank = pd.read_csv(qbank_path)
        self.remaining_items = self.qbank.copy()
        self.administered_items = []
        self.responses = []
        self.theta = 0.0  # Initial ability estimate
        self.log = []
        # The test length is now defined directly, blueprint for content is removed.
        self.test_length = 15

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

    def select_next_item(self):
        """
        Selects the next best item.
        - For the first question, it randomly picks from the top 5 most informative items.
        - For all subsequent questions, it picks the single item with the Maximum Fisher Information.
        """
        if len(self.administered_items) >= self.test_length:
            return None, "Test length reached."
        if self.remaining_items.empty:
            return None, "No items remaining."

        # Calculate Fisher Information for all remaining items at the current theta
        self.remaining_items['info'] = self.remaining_items.apply(
            lambda row: self._fisher_information(self.theta, row['a'], row['b'], row['c']),
            axis=1
        )
        
        # --- NEW LOGIC ---
        is_first_question = not self.administered_items
        
        if is_first_question:
            # For the first question, find the top 5 most informative items and sample one
            # This prevents the test from always starting with the exact same question.
            top_n_items = self.remaining_items.nlargest(5, 'info')
            next_item = top_n_items.sample(1).iloc[0].to_dict()
            selection_reason = "Randomly selected from the top 5 most informative starting items."
        else:
            # For all other questions, select the one with the absolute highest information
            best_item_id = self.remaining_items['info'].idxmax()
            next_item = self.remaining_items.loc[best_item_id].to_dict()
            selection_reason = "Selected for Maximum Fisher Information from all remaining items."

        return next_item, selection_reason

    def administer_item(self, item_id, user_answer_keys):
        """Records a response, updates theta, and logs the process."""
        item = self.qbank[self.qbank['item_id'] == item_id].iloc[0].to_dict()
        
        correct_keys = str(item['correct_answer']).split(';')
        is_correct = sorted(user_answer_keys) == sorted(correct_keys)
        
        theta_before = self.theta
        
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        item_index = self.remaining_items[self.remaining_items['item_id'] == item_id].index
        self.remaining_items.drop(item_index, inplace=True)
        
        self._update_theta_eap()
        theta_after = self.theta

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
            'theta_change': theta_after - theta_before
        }
        self.log.append(log_entry)