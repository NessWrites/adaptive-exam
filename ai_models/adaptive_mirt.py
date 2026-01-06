import json
import numpy as np
from scipy.stats import multivariate_normal
import os
import re
from dotenv import load_dotenv
from pathlib import Path


class MIRT_CAT_Exam:
    """
    2 Dimensional MIRT CAT Exam System with SE-based stopping.
    Administers adaptive test to actual test-takers using JSON question bank.
    """
    
    def __init__(self, item_bank_path, min_items=10, max_items=40, target_se=0.30):
        """
        Initializes the exam system with the item bank from JSON.
        
        Parameters:
        item_bank_path (str): Path to the JSON file containing the item bank.
        min_items (int): Minimum number of items to administer (default: 10)
        max_items (int): Maximum number of items to administer (default: 40)
        target_se (float): Target standard error for stopping (default: 0.30)
        """
        
        # Load JSON file
        with open(item_bank_path, 'r', encoding='utf-8') as f:
            self.item_bank = json.load(f)
        
        # Initialize test state
        self.remaining_items = self.item_bank.copy()
        self.administered_items = []
        self.responses = []
        
        # Initialize 2D ability estimates
        self.theta_se = np.array([1.0, 1.0])
        self.theta = np.array([0.0, 0.0])
         
        # Test length parameters (SE-BASED)
        self.min_items = min_items
        self.max_items = max_items
        self.target_se = target_se
        
        # Content tracking (50/50 balance)
        self.math_count = 0
        self.tech_count = 0
        
        # Test completion tracking
        self.test_completed = False
        self.completion_reason = None
        
        self.log = []
        
        print(f"✓ Exam system initialized with {len(self.item_bank)} items.")
        print(f"  Test range: {self.min_items}-{self.max_items} items")
        print(f"  Target SE: {self.target_se} for both dimensions")
        print(f"  Content balance: 50% Math / 50% Technical")
        
    def mirt_2pl_probability(self, theta, item):
        """Calculate probability of correct response using 2PL MIRT model."""
        a = item['a']
        a1 = a[0]
        a2 = a[1]
        b = item['b']
        
        exponent = a1 * theta[0] + a2 * theta[1] - b
        probability = 1 / (1 + np.exp(-exponent))
        
        return np.clip(probability, 1e-9, 1-1e-9)
    
    def fisher_information_matrix(self, theta, item):
        """Calculate Fisher Information for item selection."""
        p = self.mirt_2pl_probability(theta, item)
        q = 1 - p
        
        a_vector = item['a']
        scaling = p * q
        information_matrix = scaling * np.outer(a_vector, a_vector)
        
        return np.trace(information_matrix)
    
    def likelihood(self, theta, responses, items):
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
    
    def check_stopping_rule(self):
        """
        Check if test should stop based on SE targets.
        
        Returns:
        tuple: (should_stop, reason)
        """
        n_items = len(self.administered_items)
        
        # Must administer minimum items
        if n_items < self.min_items:
            return False, None
        
        # Stop if reached maximum items
        if n_items >= self.max_items:
            return True, f"Maximum {self.max_items} items reached"
        
        # Check if both SE targets are met
        math_se_met = self.theta_se[0] <= self.target_se
        tech_se_met = self.theta_se[1] <= self.target_se
        
        if math_se_met and tech_se_met:
            return True, f"SE targets achieved: Math SE={self.theta_se[0]:.3f}, Tech SE={self.theta_se[1]:.3f}"
        
        return False, None
        
    def select_next_item(self):
        """Select next item based on maximum Fisher Information with SE stopping."""
        
        # Check stopping rules (NEW)
        should_stop, reason = self.check_stopping_rule()
        if should_stop:
            self.test_completed = True
            self.completion_reason = reason
            return None, reason
        
        if not self.remaining_items:
            self.test_completed = True
            self.completion_reason = "No more items available"
            return None, "No more items available"
        
        # Content balancing (dynamic 50/50)
        n_items = len(self.administered_items)
        
        # Project expected total
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
            constraint_reason = "Need Tech items only"
        elif math_needed > 0 and tech_needed == 0:
            candidate_items = [item for item in self.remaining_items if item['a'][1] == 0]
            constraint_reason = "Need Math items only"
        else:
            candidate_items = self.remaining_items
            constraint_reason = "No content constraints"
        
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
            reason = "First item: randomly selected from top 5"
        else:
            # Maximum information
            selected_item, info = item_info[0]
            reason = f"Max info = {info:.4f} at θ=[{self.theta[0]:.2f}, {self.theta[1]:.2f}]. {constraint_reason}"
        
        return selected_item, reason
    
    def display_question(self, item, question_num):
        """Display question to the test-taker."""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        print("\n" + "="*70)
        print(f"QUESTION {question_num}")
        print("="*70)
        
        # Show progress with SE status
        print(f"Progress: {len(self.administered_items)}/{self.min_items} minimum")
        if len(self.administered_items) >= self.min_items:
            math_status = "✓" if self.theta_se[0] <= self.target_se else "✗"
            tech_status = "✓" if self.theta_se[1] <= self.target_se else "✗"
            print(f"SE Status: Math {math_status} ({self.theta_se[0]:.3f}), Tech {tech_status} ({self.theta_se[1]:.3f})")
        
        print("="*70)
        
        # Content type
        if item['a'][1] == 0:
            print(" [MATH QUESTION]")
        else:
            print("[TECHNICAL QUESTION]")
        
        # Check if multiple correct answers (MSQ)
        is_msq =  item.get('question_type','MSQ') =='MSQ'
        
        if is_msq:
            print("[MULTIPLE SELECT QUESTION - Select ALL correct answers]")
        
        print(f"\nId: {item.get('unique_id', 'N/A')}")
        
        # Display image URL if available
        if 'image_url' in item and item['image_url']:
            print("\n" + "─"*70)
            print(" IMAGE REFERENCE:")
            print(f"    {item['image_url']}")
            print("─"*70)
        
        # Display question text
        print(f"\n{item['question_text']}\n")
        
        # Display options if available
        if 'options' in item and item['options']:
            options = item['options']
            option_labels = ['A', 'B', 'C', 'D']
            
            for i, option in enumerate(options):
                if i < len(option_labels):
                    print(f"{option_labels[i]}. {option}")
            print()
            return options, is_msq
        
        return None, False
    
    def get_user_response(self, options, is_msq=False):
        """Get response from user."""
        if options:
            # Multiple choice
            valid_choices = ['A', 'B', 'C', 'D'][:len(options)]
            
            if is_msq:
                print("(This is a Multiple Select Question - you can select multiple answers)")
                print(f"Enter your answers separated by commas (e.g., A,B,D) or together (e.g., ABD)")
                
                while True:
                    answer = input(f"Your answer(s) ({'/'.join(valid_choices)}): ").strip().upper()
                    
                    # Remove spaces, commas, and split into individual letters
                    answer = answer.replace(" ", "").replace(",", "")
                    selected = list(answer)
                    
                    # Validate all selections
                    if all(letter in valid_choices for letter in selected) and len(selected) > 0:
                        return sorted(selected)  # Return sorted list like ['A', 'B', 'D']
                    print(f"Invalid input. Please enter valid options from {', '.join(valid_choices)}")
            else:
                # Single choice (MCQ)
                while True:
                    answer = input(f"Your answer ({'/'.join(valid_choices)}): ").strip().upper()
                    if answer in valid_choices:
                        return answer
                    print(f"Invalid input. Please enter {' or '.join(valid_choices)}.")
        else:
            # Open-ended (for future expansion)
            return input("Your answer: ").strip()
    
    def normalize_string(self, text):
        """Normalize string for comparison - remove ALL non-alphanumeric except spaces."""
        if not isinstance(text, str):
            return str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove all punctuation and special characters, keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Collapse multiple spaces to single space and trim
        text = ' '.join(text.split())
        
        return text

    def check_answer(self, user_answer, item):
        """Check if user's answer is correct using index-based comparison."""
        if 'correct_answer' not in item or 'options' not in item:
            return None
        
        correct_answer = item['correct_answer']
        options = item['options']
        option_labels = ['A', 'B', 'C', 'D']
        
        # Determine if this is MSQ (multiple correct answers)
        # FIXED: For MSQ, correct_answer should be a list in JSON
        # Don't split strings on commas - commas might be part of the answer text!
        if isinstance(correct_answer, list):
            is_msq = len(correct_answer) > 1
            correct_answers = correct_answer
        else:
            # Single correct answer (string) - don't split on commas!
            # Example: "Hypothesis testing (e.g., t-test)." contains a comma but is ONE answer
            correct_answers = [correct_answer]
            is_msq = False
        
        # BUILD CORRECT INDICES SET
        correct_indices = set()
        
        for correct_text in correct_answers:
            correct_text_clean = correct_text.strip()
            
            # First, check if it's a letter (A, B, C, D)
            if correct_text_clean.upper() in option_labels:
                idx = option_labels.index(correct_text_clean.upper())
                correct_indices.add(idx)
                continue
            
            # Otherwise, find matching option by normalized text
            correct_normalized = self.normalize_string(correct_text_clean)
            
            for idx, option in enumerate(options):
                option_normalized = self.normalize_string(option)
                if option_normalized == correct_normalized:
                    correct_indices.add(idx)
                    break
        
        # If we couldn't find any correct indices, something is wrong
        if not correct_indices:
            print(f"WARNING: Could not match correct answer to any option!")
            print(f"Correct answer from JSON: {correct_answers}")
            print(f"Available options: {options}")
            return None
        
        # BUILD USER INDICES SET
        if isinstance(user_answer, list):
            # MSQ: user_answer is ['A', 'B', 'D']
            try:
                user_indices = set()
                for letter in user_answer:
                    idx = option_labels.index(letter.upper())
                    user_indices.add(idx)
            except ValueError:
                return False
        else:
            # MCQ: user_answer is 'A'
            try:
                idx = option_labels.index(user_answer.upper())
                user_indices = {idx}
            except ValueError:
                return False
        
        # COMPARE INDICES
        return user_indices == correct_indices

    
    def administer_item(self, item, user_answer, is_correct):
        """Record response and update abilities."""
        
        theta_before = self.theta.copy()
        se_before = self.theta_se.copy()
        
        # Store response
        self.administered_items.append(item)
        self.responses.append(1 if is_correct else 0)
        
        # Update content counts
        if item['a'][1] == 0:
            self.math_count += 1
        else:
            self.tech_count += 1
        
        # Remove from remaining
        item_id = item.get('unique_id', None) 
        self.remaining_items = [i for i in self.remaining_items if i.get('unique_id') != item_id]
        
        # Update ability estimates
        self.update_theta_eap()
        
        # Log entry
        log_entry = {
            'q_num': len(self.administered_items),
            'item_id': item.get('unique_id', None) ,
            'form': item.get('form', 'N/A'),
            'content_type': 'Math' if item['a'][1] == 0 else 'Technical',
            'concept_tag': item.get('concept_tag', 'N/A'),
            'response': 'Correct' if is_correct else 'Incorrect',
            'user_answer': user_answer,
            'correct_answer': item.get('correct_answer', 'N/A'),
            'theta_before': theta_before.copy(),
            'theta_after': self.theta.copy(),
            'theta_change': self.theta - theta_before,
            'se_before': se_before.copy(),
            'se_after': self.theta_se.copy(),
            'se_target_met': {
                'math': self.theta_se[0] <= self.target_se,
                'tech': self.theta_se[1] <= self.target_se
            }
        }
        
        self.log.append(log_entry)
        
        # Show feedback
        print("\n" + "-"*70)
        if is_correct:
            print("✓ CORRECT!")
        else:
            print("✗ INCORRECT")
            
            # Show what user selected (for MSQ)
            if isinstance(user_answer, list):
                print(f"  You selected: {', '.join(user_answer)}")
            
            if 'correct_answer' in item:
                # Handle multiple correct answers
                correct_answer = item['correct_answer']
                options = item.get('options', [])
                
                # Parse correct answers (now properly - list or single string)
                if isinstance(correct_answer, list):
                    correct_answers = correct_answer
                else:
                    correct_answers = [correct_answer]
                
                # Display all correct answers
                try:
                    correct_letters_and_texts = []
                    
                    # Find matching options using normalization
                    for correct_text in correct_answers:
                        correct_normalized = self.normalize_string(correct_text)
                        for idx, option in enumerate(options):
                            option_normalized = self.normalize_string(option)
                            if correct_normalized == option_normalized:
                                letter = ['A', 'B', 'C', 'D'][idx]
                                correct_letters_and_texts.append((letter, option))
                                break
                    
                    if len(correct_letters_and_texts) > 1:
                        letters = ', '.join([l for l, _ in correct_letters_and_texts])
                        print(f"  Correct answers: {letters}")
                        for letter, text in correct_letters_and_texts:
                            print(f"    {letter}. {text}")
                    elif len(correct_letters_and_texts) == 1:
                        letter, text = correct_letters_and_texts[0]
                        print(f"  Correct answer: {letter}. {text}")
                    else:
                        # Fallback if no match found
                        print(f"  Correct answer: {correct_answer}")
                except (ValueError, IndexError) as e:
                    print(f"  Correct answer: {correct_answer}")
        
        print(f"\nCurrent Ability Estimates:")
        math_status = "✓" if self.theta_se[0] <= self.target_se else "✗"
        tech_status = "✓" if self.theta_se[1] <= self.target_se else "✗"
        print(f"  Math (θ₁):  {self.theta[0]:>6.3f}  (SE = {self.theta_se[0]:.3f}) {math_status}")
        print(f"  Tech (θ₂):  {self.theta[1]:>6.3f}  (SE = {self.theta_se[1]:.3f}) {tech_status}")
        print("-"*70)
        
        input("\nPress Enter to continue...")
    
    def run_exam(self):
        """Run the complete adaptive exam."""
        print("\n" + "="*70)
        print("WELCOME TO THE 2D MIRT ADAPTIVE EXAM")
        print("="*70)
        print(f"\nTest Configuration:")
        print(f"  • Minimum items: {self.min_items}")
        print(f"  • Maximum items: {self.max_items}")
        print(f"  • Target SE: {self.target_se}")
        print(f"\nThe test adapts to your ability level and will stop when")
        print(f"measurement precision is achieved (or maximum items reached).")
        print("\nYou will receive immediate feedback after each question.")
        print("\nGood luck!")
        input("\nPress Enter to begin...")
        
        # Administer test
        question_num = 0
        for i in range(self.max_items):
            # Select item
            item, reason = self.select_next_item()
            
            if item is None:
                print(f"\n{'='*70}")
                print(f"TEST ENDED: {reason}")
                print(f"{'='*70}")
                input("\nPress Enter to view results...")
                break
            
            question_num += 1
            
            # Display question
            result = self.display_question(item, question_num)
            if result:
                options, is_msq = result
            else:
                options, is_msq = None, False
            
            # Get response
            user_answer = self.get_user_response(options, is_msq)
            
            # Check answer
            is_correct = self.check_answer(user_answer, item)
            
            if is_correct is None:
                print("Warning: Could not verify answer (no answer key)")
                is_correct = False
            
            # Record and update
            self.administer_item(item, user_answer, is_correct)
        
        # Show final results
        self.print_final_results()
    
    def print_final_results(self):
        """Display final exam results."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "="*70)
        print("EXAM COMPLETE - FINAL RESULTS")
        print("="*70)
        
        print(f"\nCompletion Reason: {self.completion_reason}")
        print(f"Questions Answered: {len(self.administered_items)} (range: {self.min_items}-{self.max_items})")
        print(f"Correct Responses:  {sum(self.responses)}/{len(self.responses)}")
        print(f"Accuracy:           {(sum(self.responses)/len(self.responses)*100):.1f}%")
        
        # Content breakdown
        print("\n" + "="*70)
        print("CONTENT BREAKDOWN")
        print("="*70)
        total = len(self.administered_items)
        math_pct = (self.math_count / total * 100) if total > 0 else 0
        tech_pct = (self.tech_count / total * 100) if total > 0 else 0
        print(f"Math Questions:      {self.math_count} ({math_pct:.1f}%)")
        print(f"Technical Questions: {self.tech_count} ({tech_pct:.1f}%)")
        
        print("\n" + "="*70)
        print("ABILITY ESTIMATES")
        print("="*70)
        
        math_achieved = "✓ ACHIEVED" if self.theta_se[0] <= self.target_se else "✗ NOT MET"
        tech_achieved = "✓ ACHIEVED" if self.theta_se[1] <= self.target_se else "✗ NOT MET"
        
        print(f"\n Math Ability (θ₁):  {self.theta[0]:>7.3f}")
        print(f"   Standard Error:     {self.theta_se[0]:>7.3f}  (Target: {self.target_se:.3f}) {math_achieved}")
        print(f"   Reliability:        {(1 - self.theta_se[0]**2):>7.3f}")
        print(f"   Interpretation:     {self._interpret_ability(self.theta[0])}")
        
        print(f"\n Tech Ability (θ₂):  {self.theta[1]:>7.3f}")
        print(f"   Standard Error:     {self.theta_se[1]:>7.3f}  (Target: {self.target_se:.3f}) {tech_achieved}")
        print(f"   Reliability:        {(1 - self.theta_se[1]**2):>7.3f}")
        print(f"   Interpretation:     {self._interpret_ability(self.theta[1])}")
        
        print("\n" + "="*70)
        print("SCORE INTERPRETATION GUIDE")
        print("="*70)
        print("  > 1.5   : Exceptional")
        print("  0.5-1.5 : Above Average")
        print(" -0.5-0.5 : Average")
        print(" -1.5--0.5: Below Average")
        print("  < -1.5  : Needs Improvement")
        print("="*70 + "\n")
        
        # Ask if user wants detailed log
        save_log = input("Save detailed log to JSON? (y/n): ").strip().lower()
        if save_log == 'y':
            self.save_log()
    
    def _interpret_ability(self, theta_val):
        """Interpret theta score."""
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
    
    def save_log(self, filename='exam_log.json'):
        """Save exam log to JSON file."""
        if not self.log:
            print("No log data to save.")
            return
        
        # Prepare data for export
        log_data = []
        for entry in self.log:
            log_entry = {
                'question_num': entry['q_num'],
                'item_id': entry['item_id'],
                'form': entry['form'],
                'content_type': entry['content_type'],
                'concept_tag': entry['concept_tag'],
                'response': entry['response'],
                'user_answer': entry['user_answer'],
                'correct_answer': entry['correct_answer'],
                'theta_math_before': float(entry['theta_before'][0]),
                'theta_tech_before': float(entry['theta_before'][1]),
                'theta_math_after': float(entry['theta_after'][0]),
                'theta_tech_after': float(entry['theta_after'][1]),
                'theta_math_change': float(entry['theta_change'][0]),
                'theta_tech_change': float(entry['theta_change'][1]),
                'se_math_before': float(entry['se_before'][0]),
                'se_tech_before': float(entry['se_before'][1]),
                'se_math_after': float(entry['se_after'][0]),
                'se_tech_after': float(entry['se_after'][1]),
                'se_target_met_math': entry['se_target_met']['math'],
                'se_target_met_tech': entry['se_target_met']['tech'],
            }
            log_data.append(log_entry)
        
        # Add summary
        export_data = {
            'summary': {
                'completion_reason': self.completion_reason,
                'total_questions': len(self.administered_items),
                'min_items': self.min_items,
                'max_items': self.max_items,
                'target_se': self.target_se,
                'correct_responses': sum(self.responses),
                'accuracy': sum(self.responses) / len(self.responses),
                'final_theta_math': float(self.theta[0]),
                'final_theta_tech': float(self.theta[1]),
                'final_se_math': float(self.theta_se[0]),
                'final_se_tech': float(self.theta_se[1]),
                'se_target_achieved_math': self.theta_se[0] <= self.target_se,
                'se_target_achieved_tech': self.theta_se[1] <= self.target_se,
                'math_questions': self.math_count,
                'tech_questions': self.tech_count
            },
            'log': log_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ Log saved to {filename}")


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    # Path to your JSON question bank
    root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(dotenv_path=root / ".env")
    
    qbank_path = os.getenv("ITEM_BANK_PATH")
    
    # Create exam instance with SE-based stopping
    # You can customize these parameters:
    exam = MIRT_CAT_Exam(
        qbank_path,
        min_items=10,      # Minimum questions
        max_items=40,      # Maximum questions  
        target_se=0.30     # Stop when both SEs ≤ 0.30
    )
    
    # Run the exam
    exam.run_exam()