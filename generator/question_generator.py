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

class QuestionGenerator:
    """Generates IRT-calibrated multiple choice questions using LLM."""
    
    TECHNICAL_TOPICS = {
        'Python', 'Programming', 'Data Structures', 'Algorithms',
        'Machine Learning', 'Database', 'Git', 'Software Engineering',
        'Computer Architecture'
    }
    
    CONCEPTUAL_TOPICS = {
        'Probability', 'Statistics', 'Logic', 'Linear Algebra', 
        'Calculus', 'Mathematics'
    }
    
    DIFFICULTY_RANGES = {
        'very_easy': (-3, -1),
        'easy': (-1, 0),
        'moderate': (0, 1),
        'difficult': (1, 2),
        'very_difficult': (2, 3)
    }

    def __init__(self, irt_params_df, existing_questions_file=None):
        self.irt_params = irt_params_df
        self.irt_params['main_topic'] = (
            self.irt_params['concept_tag']
            .str.split('/')
            .str[0]
            .str.strip()
        )
        
        self.available_topics = self.irt_params['main_topic'].unique().tolist()
        self.existing_questions = self._load_existing_questions(existing_questions_file)
        self.topic_stats = self._compute_topic_stats()

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

    def _compute_topic_stats(self):
        """Compute statistical summary for each topic."""
        stats = {}
        for topic in self.available_topics:
            topic_data = self.irt_params[self.irt_params['main_topic'] == topic]
            stats[topic] = {
                'count': len(topic_data),
                'subtags': topic_data['concept_tag'].unique().tolist(),
                'a1_mean': topic_data['a1'].mean(),
                'a2_mean': topic_data['a2'].mean(),
                'b_mean': topic_data['b'].mean(),
                'a1_range': (topic_data['a1'].min(), topic_data['a1'].max()),
                'a2_range': (topic_data['a2'].min(), topic_data['a2'].max()),
                'b_range': (topic_data['b'].min(), topic_data['b'].max()),
            }
        return stats

    @staticmethod
    def _normalize_text(text):
        return ' '.join(text.lower().split())

    def get_primary_dimension(self, topic):
        """Determine whether topic uses a1 (conceptual) or a2 (technical)."""
        if topic in self.TECHNICAL_TOPICS:
            return 'a2'
        elif topic in self.CONCEPTUAL_TOPICS:
            return 'a1'
        
        topic_data = self.irt_params[self.irt_params['main_topic'] == topic]
        if len(topic_data) > 0:
            return 'a2' if topic_data['a2'].mean() > topic_data['a1'].mean() else 'a1'
        return 'a2'

    @staticmethod
    def describe_difficulty(b_param):
        if b_param < -1: return "very easy"
        elif b_param < 0: return "easy"
        elif b_param < 1: return "moderate"
        elif b_param < 2: return "difficult"
        return "very difficult"

    def _build_prompt(self, subtag, topic, b_param, dimension, a_param):
        difficulty_desc = self.describe_difficulty(b_param)
        difficulty_guide = self._get_difficulty_guidance(b_param)
        
        return f"""Create a {difficulty_desc} multiple-choice question about: {subtag}

Main Topic: {topic}
Difficulty: {b_param:.2f} ({difficulty_desc})
Discrimination (dimension {dimension}): {a_param:.2f}

Requirements:
- Question: 1-2 sentences, direct and clear
- Options: A, B, C, D (one correct)
- Difficulty level: {difficulty_guide}
- No special characters, backslashes, or LaTeX
- Make distractors plausible
- Focus on {topic} concepts

Return only valid JSON:
{{
  "question": "question text here",
  "options": {{
    "A": "option A",
    "B": "option B",
    "C": "option C",
    "D": "option D"
  }},
  "correct_answer": "A",
  "explanation": "brief explanation"
}}"""

    @staticmethod
    def _get_difficulty_guidance(b_param):
        if b_param < -1:
            return "Basic recall or simple definition"
        elif b_param < 0:
            return "Direct application of concept"
        elif b_param < 1:
            return "Requires reasoning or multiple steps"
        elif b_param < 2:
            return "Combines multiple concepts"
        return "Advanced understanding needed"

    def _call_llm(self, prompt, temperature, max_retries=3):
        """Make API call with retry logic."""
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are an expert test writer. Return only valid JSON with no markdown or extra text."},
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

    def generate_question(self, topic, subtag, dimension, a_param, b_param, temperature=0.7):
        """Generate a single question with specified IRT parameters."""
        prompt = self._build_prompt(subtag, topic, b_param, dimension, a_param)
        
        for attempt in range(3):
            try:
                content = self._call_llm(prompt, temperature)
                if not content:
                    continue
                
                question_data = self._parse_json_response(content)
                
                if not all(key in question_data for key in ['question', 'options', 'correct_answer', 'explanation']):
                    print(f"  [WARNING] Invalid structure, retrying...")
                    continue
                
                if self._normalize_text(question_data['question']) in self.existing_questions:
                    print(f"  [WARNING] Duplicate detected, retrying...")
                    continue
                
                # Add IRT parameters
                question_data['main_topic'] = topic
                question_data['concept_tag'] = subtag
                question_data['dimension'] = dimension
                question_data['a1'] = a_param if dimension == 'a1' else 0.0
                question_data['a2'] = a_param if dimension == 'a2' else 0.0
                question_data['b'] = b_param
                
                self._randomize_answer_position(question_data)
                self.existing_questions.add(self._normalize_text(question_data['question']))
                
                return question_data
            
            except RateLimitException:
                raise
            except Exception as e:
                print(f"  [ERROR] Attempt {attempt + 1} failed: {str(e)[:50]}")
        
        return None

    def generate_batch(self, n_questions, topic=None, variance_factor=0.2, 
                      difficulty_distribution=None, sampling_strategy='hybrid', hybrid_split=0.5):
        """Generate multiple questions with specified strategy."""
        questions = []
        failed_count = 0
        
        use_json = self._determine_sampling_strategy(n_questions, sampling_strategy, hybrid_split)
        
        for i in range(n_questions):
            current_topic = topic or np.random.choice(self.available_topics)
            
            if current_topic not in self.available_topics:
                print(f"\n[ERROR] Topic '{current_topic}' not found")
                return []
            
            topic_items = self.irt_params[self.irt_params['main_topic'] == current_topic]
            subtag = np.random.choice(topic_items['concept_tag'].unique())
            dimension = self.get_primary_dimension(current_topic)
            
            from_json = use_json[i]
            strategy_label = "JSON" if from_json else "IND"
            
            a_param, b_param = self._sample_parameters(
                topic_items, dimension, from_json, 
                variance_factor, difficulty_distribution
            )
            
            difficulty_desc = self.describe_difficulty(b_param)
            print(f"\n[{i+1}/{n_questions}] [{strategy_label}] {current_topic} ({dimension}, {difficulty_desc}, b={b_param:.2f})", end=" ")
            
            try:
                question = self.generate_question(current_topic, subtag, dimension, a_param, b_param)
                
                if question:
                    question['sampling_strategy'] = 'json_based' if from_json else 'independent'
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

    def _determine_sampling_strategy(self, n_questions, strategy, hybrid_split):
        """Create array indicating which questions use JSON vs independent sampling."""
        if strategy == 'hybrid':
            n_from_json = int(n_questions * hybrid_split)
            n_independent = n_questions - n_from_json
            use_json = np.array([True] * n_from_json + [False] * n_independent)
            np.random.shuffle(use_json)
        elif strategy == 'json_based':
            use_json = np.array([True] * n_questions)
        else:
            use_json = np.array([False] * n_questions)
        return use_json

    def _sample_parameters(self, topic_items, dimension, from_json, variance_factor, difficulty_distribution):
        """Sample IRT parameters based on strategy."""
        if len(topic_items) > 0:
            sample = topic_items.sample(1).iloc[0]
            base_a = sample['a1'] if dimension == 'a1' else sample['a2']
            
            a_param = np.clip(
                np.random.normal(base_a, abs(base_a) * variance_factor + 0.1), 
                0.1, 3.0
            )
            
            if from_json:
                b_param = np.clip(
                    np.random.normal(sample['b'], abs(sample['b']) * variance_factor + 0.3), 
                    -3, 3
                )
            else:
                if difficulty_distribution:
                    target_difficulty = np.random.choice(
                        list(self.DIFFICULTY_RANGES.keys()),
                        p=list(difficulty_distribution.values())
                    )
                    b_min, b_max = self.DIFFICULTY_RANGES[target_difficulty]
                    b_param = np.random.uniform(b_min, b_max)
                else:
                    b_param = np.random.uniform(-3, 3)
        else:
            a_param = np.random.uniform(0.5, 2.5)
            b_param = np.random.uniform(-3, 3)
        
        return a_param, b_param

    def display_question(self, question_data, question_number=None):
        """Print question in readable format."""
        print("\n" + "-" * 80)
        if question_number:
            print(f"Question {question_number}")
        print(f"Topic: {question_data['main_topic']} -> {question_data['concept_tag']}")
        print(f"Dimension: {question_data['dimension']} = {question_data[question_data['dimension']]:.2f}")
        print(f"Difficulty: {self.describe_difficulty(question_data['b'])} (b={question_data['b']:.2f})")
        print("-" * 80)
        print(f"\n{question_data['question']}\n")
        
        for opt in ['A', 'B', 'C', 'D']:
            marker = " [CORRECT]" if opt == question_data['correct_answer'] else ""
            print(f"{opt}. {question_data['options'][opt]}{marker}")
        
        print(f"\nExplanation: {question_data['explanation']}")
        print("-" * 80)

    def save_questions(self, questions, filename='generated_questions_mirt.json'):
        """Append questions to JSON file."""
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

    def list_topics(self):
        """Display available topics with stats."""
        print(f"\nAvailable Topics ({len(self.available_topics)}):")
        for idx, topic in enumerate(sorted(self.available_topics), 1):
            stats = self.topic_stats[topic]
            dimension = self.get_primary_dimension(topic)
            topic_type = "Technical" if topic in self.TECHNICAL_TOPICS else "Conceptual"
            print(f"{idx:3}. {topic:<30} (n={stats['count']:3}, dim={dimension}, {topic_type})")
            print(f"     b_range: [{stats['b_range'][0]:.2f}, {stats['b_range'][1]:.2f}]")
            for subtag in sorted(stats['subtags'])[:3]:
                print(f"       -> {subtag}")
            if len(stats['subtags']) > 3:
                print(f"       ... and {len(stats['subtags']) - 3} more")


def load_irt_params(json_file):
    """Load MIRT parameters from JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    if 'concept_tag' not in df.columns:
        df['concept_tag'] = 'general'
    if 'a1' not in df.columns:
        df['a1'] = df.get('a', 1.0)
    if 'a2' not in df.columns:
        df['a2'] = 0.0
    
    return df[['item', 'a1', 'a2', 'b', 'concept_tag']]


def main():
    print("="*80)
    print("IRT Question Generator")
    print("="*80)
    
    json_filename = os.path.join('data', '2pl_mirt.json')
    
    try:
        print(f"\nLoading parameters from {json_filename}...")
        irt_params = load_irt_params(json_filename)
        print(f"[OK] Loaded {len(irt_params)} parameters")
        
        generator = QuestionGenerator(
            irt_params,
            existing_questions_file='generated_questions_mirt.json'
        )
        
        generator.list_topics()
        
        target_topics = [
            'Data Structures', 'Algorithms', 'Database', 'Git',
            'Software Engineering', 'Computer Architecture',
            'Linear Algebra', 'Calculus', 'Logic',
            'Probability', 'Statistics', 'Machine Learning',
            'Python', 'Programming'
        ]
        
        available = set(generator.available_topics)
        target_topics = [t for t in target_topics if t in available]
        print(f"\n[OK] Proceeding with {len(target_topics)} topics")
        
        all_questions = []
        questions_per_topic = 20
        
        balanced_difficulty = {
            'very_easy': 0.05,
            'easy': 0.15,
            'moderate': 0.30,
            'difficult': 0.35,
            'very_difficult': 0.15
        }
        
        for i, topic in enumerate(target_topics, 1):
            print(f"\n{'='*80}")
            print(f"Topic {i}/{len(target_topics)}: {topic}")
            print(f"{'='*80}")
            
            try:
                topic_questions = generator.generate_batch(
                    n_questions=questions_per_topic,
                    topic=topic,
                    difficulty_distribution=balanced_difficulty,
                    sampling_strategy='hybrid',
                    hybrid_split=0.5,
                    variance_factor=0.2
                )
                
                all_questions.extend(topic_questions)
                print(f"[OK] Generated {len(topic_questions)} questions")
            
            except RateLimitException:
                print(f"\n[RATE LIMIT] Reached limit. Saving {len(all_questions)} questions...")
                break
        
        if all_questions:
            generator.save_questions(all_questions, 'generated_topic_questions_mirt.json')
            
            # Show samples
            print("\n" + "="*80)
            print("Sample Questions")
            print("="*80)
            for topic in target_topics[:5]:
                topic_qs = [q for q in all_questions if q['main_topic'] == topic]
                if topic_qs:
                    generator.display_question(topic_qs[0])
    
    except FileNotFoundError:
        print(f"[ERROR] File not found: {json_filename}")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()