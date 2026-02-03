"""
IRT computation engine for 2D MIRT model
"""
import re
from typing import List, Tuple, Union

import numpy as np
from scipy.stats import multivariate_normal


class IRTEngine:
    """IRT computation engine for 2D MIRT model"""
    
    # Prior distribution parameters
    PRIOR_MEAN = np.array([0.0, 0.0])
    PRIOR_COV = np.array([[1.0, 0.5], [0.5, 1.0]])
    
    # Probability clipping bounds
    MIN_PROBABILITY = 1e-9
    MAX_PROBABILITY = 1 - 1e-9
    
    # Default EAP samples
    DEFAULT_EAP_SAMPLES = 2000
    
    # Ability interpretation thresholds
    EXCEPTIONAL_THRESHOLD = 1.5
    ABOVE_AVERAGE_THRESHOLD = 0.5
    AVERAGE_THRESHOLD = -0.5
    BELOW_AVERAGE_THRESHOLD = -1.5
    
    @staticmethod
    def mirt_2pl_probability(theta: np.ndarray, a_values: List[float], b_value: float) -> float:
        """
        Calculate probability of correct response using 2PL MIRT model.
        
        Formula: P(θ) = 1 / (1 + exp(-(a1*θ1 + a2*θ2 - b)))
        
        Args:
            theta: Ability vector [theta_math, theta_tech]
            a_values: Discrimination parameters [a1, a2]
            b_value: Difficulty parameter
            
        Returns:
            Probability of correct response (clipped to avoid numerical issues)
        """
        a1, a2 = a_values
        exponent = a1 * theta[0] + a2 * theta[1] - b_value
        probability = 1 / (1 + np.exp(-exponent))
        return np.clip(probability, IRTEngine.MIN_PROBABILITY, IRTEngine.MAX_PROBABILITY)
    
    @staticmethod
    def fisher_information_matrix(theta: np.ndarray, a_values: List[float], b_value: float) -> float:
        """
        Calculate Fisher Information for item selection.
        
        Args:
            theta: Current ability estimate
            a_values: Item discrimination parameters
            b_value: Item difficulty parameter
            
        Returns:
            Trace of information matrix (scalar measure of information)
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
        
        Formula: L(θ|responses) = Π P(θ)^response * (1-P(θ))^(1-response)
        
        Args:
            theta: Ability vector
            responses: List of binary responses (1=correct, 0=incorrect)
            items: List of item dictionaries with 'a_values' and 'b_value'
            
        Returns:
            Likelihood value
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
        n_samples: int = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update ability estimates using Expected A Posteriori (EAP).
        
        Args:
            responses: List of binary responses
            items: List of item parameters
            n_samples: Number of samples for EAP estimation
            
        Returns:
            Tuple of (theta, theta_se):
                - theta: [theta_math, theta_tech]
                - theta_se: [se_math, se_tech]
        """
        if not responses:
            return np.array([0.0, 0.0]), np.array([1.0, 1.0])
        
        if n_samples is None:
            n_samples = IRTEngine.DEFAULT_EAP_SAMPLES
        
        # Generate samples from prior distribution
        theta_samples = np.random.multivariate_normal(
            mean=IRTEngine.PRIOR_MEAN, 
            cov=IRTEngine.PRIOR_COV, 
            size=n_samples
        )
        
        # Calculate likelihoods for each sample
        likelihoods = np.array([
            IRTEngine.likelihood(theta_sample, responses, items) 
            for theta_sample in theta_samples
        ])
        
        # Calculate prior densities
        prior_densities = multivariate_normal.pdf(
            theta_samples, 
            mean=IRTEngine.PRIOR_MEAN, 
            cov=IRTEngine.PRIOR_COV
        )
        
        # Compute posterior weights
        posterior = likelihoods * prior_densities
        weights = posterior / np.sum(posterior)
        
        # Calculate EAP estimate (weighted mean)
        theta = np.sum(theta_samples * weights.reshape(-1, 1), axis=0)
        
        # Calculate standard error (weighted variance)
        deviation = theta_samples - theta
        variance = np.sum(weights.reshape(-1, 1) * (deviation ** 2), axis=0)
        theta_se = np.sqrt(variance)
        
        return theta, theta_se
    
    @staticmethod
    def interpret_ability(theta_val: float) -> str:
        """
        Interpret theta score into human-readable category.
        
        Args:
            theta_val: Ability estimate
            
        Returns:
            Interpretation string
        """
        if theta_val > IRTEngine.EXCEPTIONAL_THRESHOLD:
            return "Exceptional"
        elif theta_val > IRTEngine.ABOVE_AVERAGE_THRESHOLD:
            return "Above Average"
        elif theta_val > IRTEngine.AVERAGE_THRESHOLD:
            return "Average"
        elif theta_val > IRTEngine.BELOW_AVERAGE_THRESHOLD:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def normalize_string(text: str) -> str:
        """
        Normalize string for answer comparison.
        """
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
            user_answer: User's response 
            correct_answer: Correct answer 
            options: List of option texts
            
        Returns:
            True if correct, False otherwise
        """
        # Generate option labels (A, B, C, D, ...)
        option_labels = [chr(65 + i) for i in range(len(options))]
        
        # Parse correct answer into indices
        correct_indices = IRTEngine._parse_answer_to_indices(
            correct_answer, options, option_labels
        )
        
        if not correct_indices:
            return False
        
        # Parse user answer into indices
        user_indices = IRTEngine._parse_user_answer_to_indices(
            user_answer, option_labels
        )
        
        if user_indices is None:
            return False
        
        # Compare indices
        return user_indices == correct_indices
    
    @staticmethod
    def _parse_answer_to_indices(
        answer: Union[str, List[str]], 
        options: List[str], 
        option_labels: List[str]
    ) -> set:
        """
        Parse answer (letter or text) into set of option indices.
        
        Args:
            answer: Answer as letter(s) or text
            options: List of option texts
            option_labels: List of option labels 
            
        Returns:
            Set of option indices
        """
        # Normalize to list
        if isinstance(answer, list):
            answers = answer
        else:
            answers = [answer]
        
        indices = set()
        
        for ans in answers:
            ans_clean = ans.strip()
            
            # Check if it's already a letter
            if ans_clean.upper() in option_labels:
                idx = option_labels.index(ans_clean.upper())
                indices.add(idx)
                continue
            
            # Otherwise, find matching option by normalized text
            ans_normalized = IRTEngine.normalize_string(ans_clean)
            
            for idx, option in enumerate(options):
                option_normalized = IRTEngine.normalize_string(option)
                if option_normalized == ans_normalized:
                    indices.add(idx)
                    break
        
        return indices
    
    @staticmethod
    def _parse_user_answer_to_indices(
        user_answer: Union[str, List[str]], 
        option_labels: List[str]
    ) -> Union[set, None]:
        """
        Parse user answer (letters) into set of option indices.
        
        Args:
            user_answer: User's answer as letter(s)
            option_labels: List of option labels
            
        Returns:
            Set of indices or None if invalid
        """
        try:
            if isinstance(user_answer, list):
                indices = set()
                for letter in user_answer:
                    idx = option_labels.index(letter.upper())
                    indices.add(idx)
                return indices
            else:
                idx = option_labels.index(user_answer.upper())
                return {idx}
        except (ValueError, AttributeError):
            return None