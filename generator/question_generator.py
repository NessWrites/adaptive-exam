import pandas as pd
import numpy as np
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class RateLimitException(Exception):
    pass


class PretestQuestionGenerator:
    """Generates questions in strict database format with pretest status."""
    
    TECHNICAL_TOPICS = {
        'Python', 'Programming', 'Data Structures', 'Algorithms',
        'Machine Learning', 'Database', 'Git', 'Software Engineering',
        'Computer Architecture'
    }
    
    CONCEPTUAL_TOPICS = {
        'Probability', 'Statistics', 'Logic', 'Linear Algebra', 
        'Calculus', 'Mathematics'
    }
    
    # Domain mapping for database
    DOMAIN_MAPPING = {
        'Python': 'programming',
        'Programming': 'programming',
        'Data Structures': 'computer_science',
        'Algorithms': 'computer_science',
        'Machine Learning': 'data_science',
        'Database': 'computer_science',
        'Git': 'programming',
        'Software Engineering': 'computer_science',
        'Computer Architecture': 'computer_science',
        'Probability': 'math',
        'Statistics': 'math',
        'Logic': 'math',
        'Linear Algebra': 'math',
        'Calculus': 'math',
        'Mathematics': 'math'
    }

    def __init__(self, irt_params_df=None, existing_questions_file=None):
        """
        Initialize generator. Can work with or without IRT params.
        
        Args:
            irt_params_df: Optional DataFrame with IRT parameters for reference
            existing_questions_file: Optional file to check for duplicates
        """
        self.irt_params = irt_params_df
        self.existing_questions = self._load_existing_questions(existing_questions_file)
        
        if irt_params_df is not None:
            self.irt_params['main_topic'] = (
                self.irt_params['concept_tag']
                .str.split('/')
                .str[0]
                .str.strip()
            )
            self.available_topics = self.irt_params['main_topic'].unique().tolist()
        else:
            # Use predefined topics if no IRT params provided
            self.available_topics = list(self.TECHNICAL_TOPICS | self.CONCEPTUAL_TOPICS)

    def _load_existing_questions(self, filepath):
        """Load existing questions to prevent duplicates."""
        questions = set()
        if filepath and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data:
                    q_text = item.get('question_text') or item.get('question')
                    if q_text:
                        questions.add(self._normalize_text(q_text))
            print(f"Loaded {len(questions)} existing questions")
        return questions

    @staticmethod
    def _normalize_text(text):
        """Normalize text for duplicate detection."""
        return ' '.join(text.lower().split())

    def _get_domain(self, topic):
        """Get database domain for a topic."""
        return self.DOMAIN_MAPPING.get(topic, 'general')

    def _get_concept_tag(self, topic, subtag=None):
        """Generate concept tag for database."""
        if subtag:
            return subtag
        
        # Default concept tags if not provided
        default_tags = {
            'Python': 'python/basics',
            'Programming': 'programming/fundamentals',
            'Data Structures': 'data_structures/arrays',
            'Algorithms': 'algorithms/sorting',
            'Machine Learning': 'ml/supervised_learning',
            'Database': 'database/sql',
            'Git': 'git/version_control',
            'Software Engineering': 'software_eng/design_patterns',
            'Computer Architecture': 'comp_arch/processors',
            'Probability': 'probability/distributions',
            'Statistics': 'statistics/inference',
            'Logic': 'logic/propositional',
            'Linear Algebra': 'linear_algebra/matrices',
            'Calculus': 'calculus/derivatives',
            'Mathematics': 'mathematics/general'
        }
        return default_tags.get(topic, f'{topic.lower()}/general')

    def _build_prompt(self, topic, concept_tag, difficulty_level):
        """Build LLM prompt for question generation."""
        difficulty_guidance = {
            'easy': 'Basic recall or simple definition. Straightforward application.',
            'moderate': 'Requires reasoning or connecting concepts. Multiple steps needed.',
            'difficult': 'Complex problem requiring deep understanding. Combines multiple concepts.'
        }
        
        guidance = difficulty_guidance.get(difficulty_level, difficulty_guidance['moderate'])
        
        return f"""Create a {difficulty_level} multiple-choice question about: {topic}

Concept: {concept_tag}
Difficulty: {difficulty_level}

Requirements:
- Question: 1-2 clear sentences
- Exactly 4 options: A, B, C, D (one correct)
- Difficulty: {guidance}
- No special characters, backslashes, or LaTeX
- Make distractors plausible but clearly wrong
- Focus on {topic} concepts
- Question should be self-contained

Return ONLY valid JSON with NO markdown formatting:
{{
  "question_text": "clear question here",
  "options": {{
    "A": "option A text",
    "B": "option B text",
    "C": "option C text",
    "D": "option D text"
  }},
  "correct_answer": "A",
  "explanation": "brief explanation of why the answer is correct"
}}"""

    def _call_llm(self, prompt, temperature=0.7, max_retries=3):
        """Make API call with retry logic."""
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are an expert test writer. Return ONLY valid JSON with no markdown, no code blocks, no extra text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature + (attempt * 0.1),
                    max_tokens=600
                )
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                error_msg = str(e)
                if any(term in error_msg.lower() for term in ['rate_limit', '429', 'quota']):
                    raise RateLimitException(f"API rate limit reached: {error_msg}")
                
                if attempt == max_retries - 1:
                    raise
        return None

    def _parse_json_response(self, content):
        """Parse LLM response with fallback cleaning."""
        # Remove markdown code blocks
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try fixing common issues
            content = content.replace('\\', '\\\\').replace('\\\\n', '\\n').replace('\\\\\\\\', '\\\\')
            try:
                return json.loads(content)
            except:
                content = content.replace('\\', ' ')
                return json.loads(content)

    def _randomize_answer_position(self, question_data):
        """Shuffle correct answer to random position."""
        correct = question_data['correct_answer']
        options = question_data['options']
        
        new_position = np.random.choice(['A', 'B', 'C', 'D'])
        if new_position != correct:
            options[correct], options[new_position] = options[new_position], options[correct]
            question_data['correct_answer'] = new_position

    def generate_pretest_question(self, topic, concept_tag=None, difficulty_level='moderate', 
                                   min_responses_needed=100, temperature=0.7):
        """
        Generate a single question in strict database format.
        
        Args:
            topic: Main topic area
            concept_tag: Specific concept tag (generated if None)
            difficulty_level: 'easy', 'moderate', or 'difficult'
            min_responses_needed: Number of responses needed for calibration
            temperature: LLM temperature
            
        Returns:
            Dict in database format with pretest status
        """
        if concept_tag is None:
            concept_tag = self._get_concept_tag(topic)
        
        domain = self._get_domain(topic)
        prompt = self._build_prompt(topic, concept_tag, difficulty_level)
        
        for attempt in range(3):
            try:
                content = self._call_llm(prompt, temperature)
                if not content:
                    continue
                
                question_data = self._parse_json_response(content)
                
                # Validate structure
                required_keys = ['question_text', 'options', 'correct_answer', 'explanation']
                if not all(key in question_data for key in required_keys):
                    print(f"  [WARNING] Invalid structure, retrying...")
                    continue
                
                # Check for duplicates
                if self._normalize_text(question_data['question_text']) in self.existing_questions:
                    print(f"  [WARNING] Duplicate detected, retrying...")
                    continue
                
                # Randomize answer position
                self._randomize_answer_position(question_data)
                
                # Format in STRICT DATABASE FORMAT
                db_question = {
                    # Core fields
                    'domain': domain,
                    'concept_tag': concept_tag,
                    'question_text': question_data['question_text'],
                    'options': question_data['options'],
                    'correct_answer': question_data['correct_answer'],
                    'question_type': 'MCQ',
                    
                    # PLACEHOLDER IRT parameters (will be calibrated)
                    'a_values': [0.0, 0.0],  # [a1, a2] - will be estimated
                    'b_value': 0.0,           # difficulty - will be estimated
                    
                    # PRETEST STATUS
                    'calibration_status': 'pretest',
                }
                
                # Track as existing
                self.existing_questions.add(self._normalize_text(question_data['question_text']))
                
                return db_question
            
            except RateLimitException:
                raise
            except Exception as e:
                print(f"  [ERROR] Attempt {attempt + 1} failed: {str(e)[:100]}")
        
        return None

    def generate_batch(self, n_questions, topic=None, difficulty_distribution=None, 
                      min_responses_needed=100):
        """
        Generate multiple questions in database format.
        
        Args:
            n_questions: Number of questions to generate
            topic: Specific topic (random if None)
            difficulty_distribution: Dict of {'easy': 0.2, 'moderate': 0.5, 'difficult': 0.3}
            min_responses_needed: Responses needed for calibration
            
        Returns:
            List of questions in database format
        """
        questions = []
        failed_count = 0
        
        # Default difficulty distribution
        if difficulty_distribution is None:
            difficulty_distribution = {
                'easy': 0.20,
                'moderate': 0.50,
                'difficult': 0.30
            }
        
        # Generate difficulty levels for all questions
        difficulty_levels = np.random.choice(
            list(difficulty_distribution.keys()),
            size=n_questions,
            p=list(difficulty_distribution.values())
        )
        
        for i in range(n_questions):
            # Select topic
            current_topic = topic or np.random.choice(self.available_topics)
            
            if current_topic not in self.available_topics:
                print(f"\n[ERROR] Topic '{current_topic}' not found")
                return questions
            
            # Get concept tag
            if self.irt_params is not None:
                topic_items = self.irt_params[self.irt_params['main_topic'] == current_topic]
                if len(topic_items) > 0:
                    concept_tag = np.random.choice(topic_items['concept_tag'].unique())
                else:
                    concept_tag = self._get_concept_tag(current_topic)
            else:
                concept_tag = self._get_concept_tag(current_topic)
            
            difficulty = difficulty_levels[i]
            
            print(f"\n[{i+1}/{n_questions}] {current_topic} ({difficulty})", end=" ")
            
            try:
                question = self.generate_pretest_question(
                    topic=current_topic,
                    concept_tag=concept_tag,
                    difficulty_level=difficulty,
                    min_responses_needed=min_responses_needed
                )
                
                if question:
                    questions.append(question)
                    print("[OK]")
                else:
                    failed_count += 1
                    print("[FAILED]")
            
            except RateLimitException:
                print(f"\n\n[RATE LIMIT] Reached limit after generating {len(questions)} questions")
                raise
        
        if failed_count > 0:
            print(f"\n[WARNING] Failed: {failed_count}/{n_questions} questions")
        
        return questions

    def save_questions(self, questions, filename='pretest_questions.json'):
        """Save questions to JSON file."""
        existing = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    existing = json.load(f)
                print(f"\n[OK] Found {len(existing)} existing questions")
            except:
                pass
        
        all_questions = existing + questions
        
        with open(filename, 'w') as f:
            json.dump(all_questions, f, indent=2)
        
        print(f"[OK] Saved {len(all_questions)} total questions ({len(questions)} new)")
        return filename

    def display_question(self, question_data, question_number=None):
        """Display question in readable format."""
        print("\n" + "-" * 80)
        if question_number:
            print(f"Question {question_number}")
        print(f"Domain: {question_data['domain']}")
        print(f"Topic: {question_data['main_topic']} -> {question_data['concept_tag']}")
        print(f"Difficulty: {question_data['difficulty_level']}")
        print(f"Status: {question_data['calibration_status']}")
        print(f"IRT Params: a_values={question_data['a_values']}, b_value={question_data['b_value']}")
        print(f"Responses: {question_data['current_responses']}/{question_data['min_responses_needed']}")
        print("-" * 80)
        print(f"\n{question_data['question_text']}\n")
        
        for opt in ['A', 'B', 'C', 'D']:
            marker = " [CORRECT]" if opt == question_data['correct_answer'] else ""
            print(f"{opt}. {question_data['options'][opt]}{marker}")
        
        print(f"\nExplanation: {question_data['explanation']}")
        print("-" * 80)


def generate_new_questions_llm(n_questions=50, topics=None, output_file='pretest_questions.json'):
    """
    Generate new questions using LLM in strict database format.
    
    Args:
        n_questions: Number of questions to generate (default: 50)
        topics: List of topics to cover (default: all available)
        output_file: Output filename
        
    Returns:
        List of questions in database format
    """
    print("="*80)
    print("Pretest Question Generator")
    print("="*80)
    
    # Optional: Load existing IRT params for reference
    json_filename = os.path.join('data', '2pl_mirt.json')
    irt_params = None
    
    if os.path.exists(json_filename):
        try:
            print(f"\nLoading IRT params from {json_filename}...")
            with open(json_filename, 'r') as f:
                data = json.load(f)
            irt_params = pd.DataFrame(data)
            if 'concept_tag' not in irt_params.columns:
                irt_params['concept_tag'] = 'general'
            if 'a1' not in irt_params.columns:
                irt_params['a1'] = irt_params.get('a', 1.0)
            if 'a2' not in irt_params.columns:
                irt_params['a2'] = 0.0
            irt_params = irt_params[['item', 'a1', 'a2', 'b', 'concept_tag']]
            print(f"[OK] Loaded {len(irt_params)} IRT parameters for reference")
        except Exception as e:
            print(f"[WARNING] Could not load IRT params: {e}")
            print("[INFO] Proceeding without IRT reference")
    
    # Initialize generator
    generator = PretestQuestionGenerator(
        irt_params_df=irt_params,
        existing_questions_file=output_file
    )
    
    # Use provided topics or default set
    if topics is None:
        topics = [
            'Calculus', 'Linear Algebra', 'Probability', 'Statistics',
            'Algorithms', 'Data Structures', 'Python', 'Machine Learning',
            'Database', 'Software Engineering'
        ]
    
    # Filter to available topics
    available = set(generator.available_topics)
    topics = [t for t in topics if t in available]
    
    print(f"\n[INFO] Generating {n_questions} questions across {len(topics)} topics")
    print(f"[INFO] Topics: {', '.join(topics)}")
    
    # Balanced difficulty distribution
    difficulty_dist = {
        'easy': 0.25,
        'moderate': 0.50,
        'difficult': 0.25
    }
    
    new_questions = []
    
    try:
        # Generate questions for each topic
        questions_per_topic = max(1, n_questions // len(topics))
        
        for topic in topics:
            print(f"\n{'='*80}")
            print(f"Topic: {topic}")
            print(f"{'='*80}")
            
            topic_questions = generator.generate_batch(
                n_questions=questions_per_topic,
                topic=topic,
                difficulty_distribution=difficulty_dist,
                min_responses_needed=100  # Need 100 responses to calibrate
            )
            
            new_questions.extend(topic_questions)
            
            if len(new_questions) >= n_questions:
                new_questions = new_questions[:n_questions]
                break
        
        # Save questions
        if new_questions:
            filename = generator.save_questions(new_questions, output_file)
            
            print(f"\n{'='*80}")
            print(f"✓ Added {len(new_questions)} pretest questions")
            print(f"✓ Saved to: {filename}")
            print(f"{'='*80}")
            
            # Display sample questions
            print("\nSample Questions:")
            for i, q in enumerate(new_questions[:3], 1):
                generator.display_question(q, question_number=i)
            
            return new_questions
        else:
            print("\n[ERROR] No questions generated")
            return []
    
    except RateLimitException as e:
        print(f"\n[RATE LIMIT] {e}")
        print(f"[INFO] Saving {len(new_questions)} questions generated so far...")
        if new_questions:
            generator.save_questions(new_questions, output_file)
        return new_questions
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Main function to generate pretest questions."""
    
    # Example 1: Generate 50 questions
    questions = generate_new_questions_llm(
        n_questions=50,
        topics=['Calculus', 'Python', 'Algorithms', 'Statistics', 'Machine Learning'],
        output_file='pretest_questions.json'
    )
    
    print(f"\n{'='*80}")
    print(f"Generation Complete!")
    print(f"Total questions: {len(questions)}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()