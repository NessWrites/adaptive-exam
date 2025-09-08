import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

class CATSimulator:
    def __init__(self, qbank_path):
        self.qbank = pd.read_csv(qbank_path)
        self.remaining_items = self.qbank.copy()
        self.administered_items = []
        self.responses = []
        self.theta = 0.0  # Initial ability estimate

    def _irt_3pl(self, theta, a, b, c):
        """Calculates the probability of a correct response using the 3PL model."""
        return c + (1 - c) / (1 + np.exp(-1.7 * a * (theta - b)))

    def _fisher_information(self, theta, a, b, c):
        """Calculates the Fisher Information for a single item."""
        p = self._irt_3pl(theta, a, b, c)
        if p == 1.0: p = 0.9999 # Avoid division by zero
        q = 1 - p
        return (1.7**2) * (a**2) * (q / p) * ((p - c)**2 / (1 - c)**2)

    def _log_likelihood(self, theta, responses, administered_params):
        """Log-likelihood function for the observed responses."""
        log_like = 0.0
        for i, u in enumerate(responses):
            a, b, c = administered_params[i]
            p = self._irt_3pl(theta, a, b, c)
            # Add small epsilon to avoid log(0)
            p = np.clip(p, 1e-9, 1 - 1e-9)
            if u == 1:
                log_like += np.log(p)
            else:
                log_like += np.log(1 - p)
        # Add a prior to stabilize the estimate, especially at the beginning
        # This is a simple Bayesian MAP estimation with a standard normal prior
        log_like += norm.logpdf(theta, 0, 2)
        return -log_like # We minimize the negative log-likelihood

    def _update_theta(self):
        """Update the ability estimate (theta) using Maximum Likelihood Estimation."""
        if not self.responses:
            return

        administered_params = [
            (item['a'], item['b'], item['c']) for item in self.administered_items
        ]
        
        # We use optimization to find the theta that maximizes the likelihood
        result = minimize(
            self._log_likelihood,
            x0=self.theta, # Start search from current theta
            args=(self.responses, administered_params),
            method='Nelder-Mead'
        )
        self.theta = result.x[0]

    def select_next_item(self):
        """Selects the next best item based on Maximum Fisher Information."""
        if self.remaining_items.empty:
            return None

        # Calculate information for all remaining items at the current theta
        self.remaining_items['info'] = self.remaining_items.apply(
            lambda row: self._fisher_information(self.theta, row['a'], row['b'], row['c']),
            axis=1
        )
        
        # Select the item with the highest information
        best_item_id = self.remaining_items['info'].idxmax()
        next_item = self.remaining_items.loc[best_item_id]
        return next_item

    def administer_item(self, item_id, is_correct):
        """Records a response and updates the state."""
        item = self.qbank[self.qbank['item_id'] == item_id].iloc[0]
        
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Remove from remaining pool
        self.remaining_items.drop(
            self.remaining_items[self.remaining_items['item_id'] == item_id].index,
            inplace=True
        )
        
        # Update ability estimate after the response
        self._update_theta()