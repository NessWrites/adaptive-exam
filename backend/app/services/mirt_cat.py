import json
import numpy as np
from scipy.stats import multivariate_normal
from typing import Optional, Tuple, List, Dict, Any

class MIRT_CAT_Exam:
    """
    2 Dimensional MIRT CAT Exam System
    """
    
    def __init__(self, item_bank_path: str, min_items: int = 10, 
                 max_items: int = 40, target_se: float = 0.30):
        # Load JSON file
        try:
            with open(item_bank_path, 'r', encoding='utf-8') as f:
                self.item_bank = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load item bank: {str(e)}")
        
        # Initialize test state
        self.remaining_items = self.item_bank.copy()
        self.administered_items = []
        self.responses = []
        
        # Initialize 2D ability estimates
        self.theta_se = np.array([1.0, 1.0])
        self.theta = np.array([0.0, 0.0])
         
        # Test length parameters
        self.min_items = min_items
        self.max_items = max_items
        self.target_se = target_se
        
        # Content tracking
        self.math_count = 0
        self.tech_count = 0
        
        # Test completion tracking
        self.test_completed = False
        self.completion_reason = None
        
        self.log = []
        self.current_item = None
        
    def mirt_2pl_probability(self, theta: np.ndarray, item: Dict) -> float:
        """Calculate probability of correct response using 2PL MIRT model."""
        a = item['a']
        a1 = a[0]
        a2 = a[1]
        b = item['b']
        
        exponent = a1 * theta[0] + a2 * theta[1] - b
        probability = 1 / (1 + np.exp(-exponent))
        
        return np.clip(probability, 1e-9, 1-1e-9)
    
    def fisher_information_matrix(self, theta: np.ndarray, item: Dict) -> float:
        """Calculate Fisher Information for item selection."""
        p = self.mirt_2pl_probability(theta, item)
        q = 1 - p
        
        a_vector = item['a']
        scaling = p * q
        information_matrix = scaling * np.outer(a_vector, a_vector)
        
        return np.trace(information_matrix)
    
    def likelihood(self, theta: np.ndarray, responses: List[int], 
                   items: List[Dict]) -> float:
        """Calculate likelihood of responses given theta."""
        log_likelihood = 1.0
        
        for response, item in zip(responses, items):
            p = self.mirt_2pl_probability(theta, item)
            if response == 1:
                log_likelihood *= p
            else:
                log_likelihood *= (1 - p)
                
        return log_likelihood
    
    def update_theta_eap(self):
        """Update ability estimates using Expected A Posteriori (EAP)."""
        if not self.responses:
            return
        
        n_samples = 2000
        
        # Prior: N(0, Σ) with correlation
        prior_mean = np.array([0, 0])
        prior_cov = np.array([[1.0, 0.5],
                              [0.5, 1.0]])
        
        # Generate samples
        theta_samples = np.random.multivariate_normal(
            mean=prior_mean, cov=prior_cov, size=n_samples
        )
        
        # Calculate likelihoods
        likelihoods = np.array([
            self.likelihood(theta_sample, self.responses, self.administered_items) 
            for theta_sample in theta_samples
        ])
        
        # Prior densities        
        prior_densities = multivariate_normal.pdf(
            theta_samples, mean=prior_mean, cov=prior_cov
        )
        
        # Posterior weights
        posterior = likelihoods * prior_densities
        weights = posterior / np.sum(posterior)
        
        # EAP estimate
        self.theta = np.sum(theta_samples * weights.reshape(-1, 1), axis=0)
        
        # Standard error
        deviation = theta_samples - self.theta
        variance = np.sum(weights.reshape(-1, 1) * (deviation ** 2), axis=0)
        self.theta_se = np.sqrt(variance)
    
    def check_stopping_rule(self) -> Tuple[bool, Optional[str]]:
        """Check if test should stop based on SE targets."""
        n_items = len(self.administered_items)
        
        if n_items < self.min_items:
            return False, None
        
        if n_items >= self.max_items:
            return True, f"Maximum {self.max_items} items reached"
        
        math_se_met = self.theta_se[0] <= self.target_se
        tech_se_met = self.theta_se[1] <= self.target_se
        
        if math_se_met and tech_se_met:
            return True, f"SE targets achieved: Math SE={self.theta_se[0]:.3f}, Tech SE={self.theta_se[1]:.3f}"
        
        return False, None
        
    def select_next_item(self) -> Tuple[Optional[Dict], Optional[str]]:
        """Select next item based on maximum Fisher Information."""
        should_stop, reason = self.check_stopping_rule()
        if should_stop:
            self.test_completed = True
            self.completion_reason = reason
            return None, reason
        
        if not self.remaining_items:
            self.test_completed = True
            self.completion_reason = "No more items available"
            return None, "No more items available"
        
        # Content balancing
        n_items = len(self.administered_items)
        
        if n_items < self.min_items:
            projected_total = self.min_items
        else:
            projected_total = min(n_items + 10, self.max_items)
        
        target_math = projected_total // 2
        target_tech = projected_total // 2
        
        math_needed = target_math - self.math_count
        tech_needed = target_tech - self.tech_count
        
        # Filter items based on content needs
        if tech_needed > 0 and math_needed == 0:
            candidate_items = [item for item in self.remaining_items if item['a'][0] == 0]
        elif math_needed > 0 and tech_needed == 0:
            candidate_items = [item for item in self.remaining_items if item['a'][1] == 0]
        else:
            candidate_items = self.remaining_items
        
        if not candidate_items:
            return None, "No items available for required content"
        
        # Calculate information for each candidate
        item_info = []
        for item in candidate_items:
            info = self.fisher_information_matrix(self.theta, item)
            item_info.append((item, info))
        
        # Sort by information (descending)
        item_info.sort(key=lambda x: x[1], reverse=True)
        
        # First item: random from top 5
        if len(self.administered_items) == 0:
            top_items = item_info[:min(5, len(item_info))]
            selected_item, info = top_items[np.random.randint(len(top_items))]
        else:
            selected_item, info = item_info[0]
        
        return selected_item, None
    
    def normalize_string(self, text: Any) -> str:
        """Normalize string for comparison."""
        if not isinstance(text, str):
            return str(text)
        return ''.join(text.split()).lower()
    
    def check_answer(self, user_answer: Any, item: Dict) -> Optional[bool]:
        """Check if user's answer is correct."""
        if 'correct_answer' not in item or 'options' not in item:
            return None
        
        correct_answer = item['correct_answer']
        options = item['options']
        
        # Determine if this is MSQ
        if isinstance(correct_answer, list):
            correct_answers = correct_answer
            is_msq = len(correct_answers) > 1
        elif isinstance(correct_answer, str) and ',' in correct_answer:
            correct_answers = [ans.strip() for ans in correct_answer.split(',')]
            is_msq = len(correct_answers) > 1
        else:
            correct_answers = [correct_answer]
            is_msq = False
        
        # Handle MSQ
        if is_msq and isinstance(user_answer, list):
            try:
                user_option_texts = []
                for letter in user_answer:
                    user_index = ['A', 'B', 'C', 'D'].index(letter)
                    if user_index >= len(options):
                        return None
                    user_option_texts.append(options[user_index])
                
                user_normalized = set(self.normalize_string(text) for text in user_option_texts)
                correct_normalized = set(self.normalize_string(text) for text in correct_answers)
                
                return user_normalized == correct_normalized
                
            except (ValueError, IndexError):
                return None
        
        # Handle MCQ
        elif not is_msq and isinstance(user_answer, str):
            try:
                user_index = ['A', 'B', 'C', 'D'].index(user_answer)
                if user_index >= len(options):
                    return None
                user_option_text = options[user_index]
            except (ValueError, IndexError):
                return None
            
            user_normalized = self.normalize_string(user_option_text)
            correct_normalized = self.normalize_string(correct_answers[0])
            
            return user_normalized == correct_normalized
        else:
            return False
    
    def record_response(self, user_answer: Any, is_correct: bool) -> Tuple[np.ndarray, np.ndarray]:
        """Record response and update abilities."""
        if self.current_item is None:
            return np.array([0.0, 0.0]), np.array([1.0, 1.0])
        
        theta_before = self.theta.copy()
        se_before = self.theta_se.copy()
        
        # Store response
        self.administered_items.append(self.current_item)
        self.responses.append(1 if is_correct else 0)
        
        # Update content counts
        if self.current_item['a'][1] == 0:
            self.math_count += 1
        else:
            self.tech_count += 1
        
        # Remove from remaining
        item_id = self.current_item.get('unique_id', self.current_item.get('item'))
        self.remaining_items = [i for i in self.remaining_items 
                               if i.get('unique_id', i.get('item')) != item_id]
        
        # Update ability estimates
        self.update_theta_eap()
        
        # Log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': self.current_item.get('unique_id', self.current_item.get('item')),
            'response': 'Correct' if is_correct else 'Incorrect',
            'user_answer': user_answer,
            'correct_answer': self.current_item.get('correct_answer', 'N/A'),
            'theta_before': theta_before.tolist(),
            'theta_after': self.theta.tolist(),
            'se_before': se_before.tolist(),
            'se_after': self.theta_se.tolist(),
        }
        
        self.log.append(log_entry)
        
        return theta_before, se_before
    
    @staticmethod
    def is_msq_item(item: Dict) -> bool:
        """Check if item is multiple select question."""
        if 'correct_answer' not in item:
            return False
        
        correct_answer = item['correct_answer']
        if isinstance(correct_answer, list) and len(correct_answer) > 1:
            return True
        elif isinstance(correct_answer, str) and ',' in correct_answer:
            answers = [ans.strip() for ans in correct_answer.split(',')]
            return len(answers) > 1
        
        return False