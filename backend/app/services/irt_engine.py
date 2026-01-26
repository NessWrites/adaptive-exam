import numpy as np
from scipy.stats import multivariate_normal
from typing import List, Tuple, Union
import re


class IRTEngine:
    """IRT computation engine for 2D MIRT model"""
    
    @staticmethod
    def mirt_2pl_probability(theta: np.ndarray, a_values: List[float], b_value: float) -> float:
        """
        Calculate probability of correct response using 2PL MIRT model.
        
        P(θ) = 1 / (1 + exp(-(a1*θ1 + a2*θ2 - b)))
        """
        a1, a2 = a_values
        exponent = a1 * theta[0] + a2 * theta[1] - b_value
        probability = 1 / (1 + np.exp(-exponent))
        return np.clip(probability, 1e-9, 1 - 1e-9)
    
    @staticmethod
    def fisher_information_matrix(theta: np.ndarray, a_values: List[float], b_value: float) -> float:
        """
        Calculate Fisher Information for item selection.
        Returns trace of information matrix.
        """
        p = IRTEngine.mirt_2pl_probability(theta, a_values, b_value)
        q = 1 - p
        
        a_vector = np.array(a_values)
        scaling = p * q
        information_matrix = scaling * np.outer(a_vector, a_vector)
        
        return np.trace(information_matrix)
    
    @staticmethod
    def likelihood(theta: np.ndarray, responses: List[int], items: List[dict]) -> float:
        """
        Calculate likelihood of responses given theta.
        
        L(θ|responses) = Π P(θ)^response * (1-P(θ))^(1-response)
        """
        log_likelihood = 1.0
        
        for response, item in zip(responses, items):
            p = IRTEngine.mirt_2pl_probability(
                theta, 
                item['a_values'], 
                item['b_value']
            )
            
            if response == 1:
                log_likelihood *= p
            else:
                log_likelihood *= (1 - p)
        
        return log_likelihood
    
    @staticmethod
    def update_theta_eap(
        responses: List[int], 
        items: List[dict], 
        n_samples: int = 2000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update ability estimates using Expected A Posteriori (EAP).
        
        Returns:
            theta: [theta_math, theta_tech]
            theta_se: [se_math, se_tech]
        """
        if not responses:
            return np.array([0.0, 0.0]), np.array([1.0, 1.0])
        
        # Prior: N(0, Σ) with correlation
        prior_mean = np.array([0, 0])
        prior_cov = np.array([[1.0, 0.5],
                              [0.5, 1.0]])
        
        # Generate samples from prior
        theta_samples = np.random.multivariate_normal(
            mean=prior_mean, 
            cov=prior_cov, 
            size=n_samples
        )
        
        # Calculate likelihoods for each sample
        likelihoods = np.array([
            IRTEngine.likelihood(theta_sample, responses, items) 
            for theta_sample in theta_samples
        ])
        
        # Prior densities
        prior_densities = multivariate_normal.pdf(
            theta_samples, 
            mean=prior_mean, 
            cov=prior_cov
        )
        
        # Posterior weights
        posterior = likelihoods * prior_densities
        weights = posterior / np.sum(posterior)
        
        # EAP estimate
        theta = np.sum(theta_samples * weights.reshape(-1, 1), axis=0)
        
        # Standard error
        deviation = theta_samples - theta
        variance = np.sum(weights.reshape(-1, 1) * (deviation ** 2), axis=0)
        theta_se = np.sqrt(variance)
        
        return theta, theta_se
    
    @staticmethod
    def interpret_ability(theta_val: float) -> str:
        """Interpret theta score"""
        if theta_val > 1.5:
            return "Exceptional"
        elif theta_val > 0.5:
            return "Above Average"
        elif theta_val > -0.5:
            return "Average"
        elif theta_val > -1.5:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def normalize_string(text: str) -> str:
        """Normalize string for answer comparison"""
        if not isinstance(text, str):
            return str(text)
        
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def check_answer(
        user_answer: Union[str, List[str]], 
        correct_answer: Union[str, List[str]], 
        options: List[str]
    ) -> bool:
        """
        Check if user's answer is correct using index-based comparison.
        
        Args:
            user_answer: User's response (letter(s) like 'A' or ['A', 'B'])
            correct_answer: Correct answer (letter(s) or text)
            options: List of option texts
            
        Returns:
            True if correct, False otherwise
        """
        # Generate option labels
        option_labels = [chr(65 + i) for i in range(len(options))]  # A, B, C, D, ...
        
        # Normalize correct answers to list
        if isinstance(correct_answer, list):
            correct_answers = correct_answer
        else:
            correct_answers = [correct_answer]
        
        # Build correct indices set
        correct_indices = set()
        
        for correct_text in correct_answers:
            correct_text_clean = correct_text.strip()
            
            # Check if it's already a letter (A, B, C, etc.)
            if correct_text_clean.upper() in option_labels:
                idx = option_labels.index(correct_text_clean.upper())
                correct_indices.add(idx)
                continue
            
            # Otherwise, find matching option by normalized text
            correct_normalized = IRTEngine.normalize_string(correct_text_clean)
            
            for idx, option in enumerate(options):
                option_normalized = IRTEngine.normalize_string(option)
                if option_normalized == correct_normalized:
                    correct_indices.add(idx)
                    break
        
        if not correct_indices:
            return False
        
        # Build user indices set
        if isinstance(user_answer, list):
            try:
                user_indices = set()
                for letter in user_answer:
                    idx = option_labels.index(letter.upper())
                    user_indices.add(idx)
            except (ValueError, AttributeError):
                return False
        else:
            try:
                idx = option_labels.index(user_answer.upper())
                user_indices = {idx}
            except (ValueError, AttributeError):
                return False
        
        # Compare indices
        return user_indices == correct_indices