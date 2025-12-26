import pandas as pd
import numpy as np
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class RateLimitException(Exception):
    """Custom exception for API rate limit errors"""
    pass

class MultidimensionalIRTQuestionGenerator:
    def __init__(self, irt_params_df, existing_questions_file=None):
        """Initialize with Multidimensional IRT parameters dataframe"""
        self.irt_params = irt_params_df
        
        # Extract main topic from concept_tag (everything before '/')
        self.irt_params['main_topic'] = self.irt_params['concept_tag'].str.split('/').str[0].str.strip()
        
        self.available_topics = self.irt_params['main_topic'].unique().tolist()
        self.available_tags = irt_params_df['concept_tag'].unique().tolist()
        
        # Define which topics are technical (use a2) vs conceptual (use a1)
        self.technical_topics = {
            'Python', 'Programming', 'Data Structures', 'Algorithms',
            'Machine Learning', 'Database', 'Git', 'Software Engineering',
            'Computer Architecture'
        }
        
        self.conceptual_topics = {
            'Probability', 'Statistics', 'Logic', 'Linear Algebra', 
            'Calculus', 'Mathematics'
        }
        
        # Load existing questions to avoid duplication
        self.existing_questions = set()
        if existing_questions_file and os.path.exists(existing_questions_file):
            with open(existing_questions_file, 'r') as f:
                existing_data = json.load(f)
                for item in existing_data:
                    q_text = item.get('question_text') or item.get('question')
                    if q_text:
                        self.existing_questions.add(self._normalize_question(q_text))
            print(f"Loaded {len(self.existing_questions)} existing questions")
        
        # Analyze distributions by TOPIC (not tag)
        self.topic_stats = {}
        for topic in self.available_topics:
            topic_data = self.irt_params[self.irt_params['main_topic'] == topic]
            self.topic_stats[topic] = {
                'count': len(topic_data),
                'subtags': topic_data['concept_tag'].unique().tolist(),
                'a1_mean': topic_data['a1'].mean(),
                'a2_mean': topic_data['a2'].mean(),
                'b_mean': topic_data['b'].mean(),
                'a1_range': (topic_data['a1'].min(), topic_data['a1'].max()),
                'a2_range': (topic_data['a2'].min(), topic_data['a2'].max()),
                'b_range': (topic_data['b'].min(), topic_data['b'].max()),
            }

    def _normalize_question(self, question_text):
        """Normalize question text for comparison"""
        return ' '.join(question_text.lower().split())

    def get_dimension_for_topic(self, topic):
        """Determine which dimension (a1 or a2) should be used for a topic"""
        if topic in self.technical_topics:
            return 'a2'  # Technical questions use a2
        elif topic in self.conceptual_topics:
            return 'a1'  # Conceptual questions use a1
        else:
            # For unknown topics, check the IRT params to see which dimension is stronger
            topic_data = self.irt_params[self.irt_params['main_topic'] == topic]
            if len(topic_data) > 0:
                avg_a1 = topic_data['a1'].mean()
                avg_a2 = topic_data['a2'].mean()
                return 'a2' if avg_a2 > avg_a1 else 'a1'
            return 'a2'  # Default to a2

    def difficulty_to_description(self, b_param):
        """Convert b parameter to difficulty level"""
        if b_param < -1: return "very easy"
        elif b_param < 0: return "easy"
        elif b_param < 1: return "moderate"
        elif b_param < 2: return "difficult"
        else: return "very difficult"

    def is_question_duplicate(self, question_text):
        """Check if question already exists"""
        normalized = self._normalize_question(question_text)
        return normalized in self.existing_questions

    def list_available_topics(self):
        """Display all available topics"""
        print(f"\nAvailable Topics ({len(self.available_topics)}):")
        for idx, topic in enumerate(sorted(self.available_topics), 1):
            stats = self.topic_stats[topic]
            dimension = self.get_dimension_for_topic(topic)
            topic_type = "Technical" if topic in self.technical_topics else "Conceptual"
            print(f"{idx:3}. {topic:<30} (n={stats['count']:3}, dim={dimension}, {topic_type})")
            print(f"     b_range: [{stats['b_range'][0]:.2f}, {stats['b_range'][1]:.2f}]")
            # Show subtags
            for subtag in sorted(stats['subtags'])[:3]:  # Show first 3
                print(f"       → {subtag}")
            if len(stats['subtags']) > 3:
                print(f"       ... and {len(stats['subtags']) - 3} more")

    def generate_question(self, topic, subtag, dimension, a_param, b_param, temperature=0.7, max_retries=3):
        """
        Generate a single question measuring ONE dimension only
        
        Args:
            topic: Main topic (e.g., "Python", "Statistics")
            subtag: Full concept tag for context
            dimension: Either 'a1' or 'a2' (the dimension to measure)
            a_param: Discrimination parameter value
            b_param: Difficulty parameter
        
        Returns:
            question_data dict or None if failed
        
        Raises:
            RateLimitException: When API rate limit is reached
        """
        
        difficulty_desc = self.difficulty_to_description(b_param)
        
        # OPTIMIZED PROMPT
        prompt = f"""Create a {difficulty_desc} multiple-choice question about: {subtag}

Main Topic: {topic}
Difficulty: {b_param:.2f} ({difficulty_desc})
Discrimination (dimension {dimension}): {a_param:.2f}

RULES:
1. Question: 1-2 sentences, direct and clear
2. Options: A, B, C, D (one correct)
3. Difficulty: {self._get_difficulty_guide(b_param)}
4. NO special characters, backslashes, or LaTeX
5. Make distractors plausible
6. Focus on {topic} concepts

Return ONLY valid JSON:
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

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert test writer. Return ONLY valid JSON with no markdown or extra text."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=temperature + (attempt * 0.1),
                    max_tokens=600
                )
                
                content = response.choices[0].message.content.strip()
                
                # Clean markdown formatting
                content = content.replace("```json", "").replace("```", "").strip()
                
                # Robust JSON parsing
                try:
                    question_data = json.loads(content)
                except json.JSONDecodeError:
                    # Try fixing common issues
                    content = content.replace('\\', '\\\\')
                    content = content.replace('\\\\n', '\\n')
                    content = content.replace('\\\\\\\\', '\\\\')
                    try:
                        question_data = json.loads(content)
                    except:
                        # Last resort: remove backslashes
                        content = content.replace('\\', ' ')
                        question_data = json.loads(content)
                
                # Validate structure
                if not all(key in question_data for key in ['question', 'options', 'correct_answer', 'explanation']):
                    print(f"  ⚠ Invalid structure, retrying...")
                    continue
                
                # Check for duplicates
                if self.is_question_duplicate(question_data['question']):
                    print(f"  ⚠ Duplicate detected, retrying...")
                    continue
                
                # Add metadata - ONE dimension only
                question_data['main_topic'] = topic
                question_data['concept_tag'] = subtag
                question_data['dimension'] = dimension
                
                if dimension == 'a1':
                    question_data['a1'] = a_param
                    question_data['a2'] = 0.0
                else:  # dimension == 'a2'
                    question_data['a1'] = 0.0
                    question_data['a2'] = a_param
                
                question_data['b'] = b_param
                
                # Randomize correct answer position
                self._randomize_answer_position(question_data)
                
                # Add to existing questions
                self.existing_questions.add(self._normalize_question(question_data['question']))
                
                return question_data
                
            except Exception as e:
                error_msg = str(e)
                # Check for rate limit errors
                if 'rate_limit' in error_msg.lower() or '429' in error_msg or 'quota' in error_msg.lower():
                    print(f"\n\n{'='*80}")
                    print("⛔ RATE LIMIT REACHED!")
                    print(f"{'='*80}")
                    print(f"Error: {error_msg}")
                    print("\nStopping generation to prevent data loss...")
                    print("Partial results have NOT been saved.")
                    print(f"{'='*80}\n")
                    raise RateLimitException(f"API rate limit reached: {error_msg}")
                
                print(f"  ❌ Attempt {attempt + 1} failed: {str(e)[:50]}")
                if attempt == max_retries - 1:
                    return None
        
        return None

    def _get_difficulty_guide(self, b_param):
        """Get difficulty-specific guidance"""
        if b_param < -1:
            return "Basic recall or simple definition"
        elif b_param < 0:
            return "Direct application of concept"
        elif b_param < 1:
            return "Requires reasoning or multiple steps"
        elif b_param < 2:
            return "Combines multiple concepts"
        else:
            return "Advanced understanding needed"

    def _randomize_answer_position(self, question_data):
        """Randomize the position of the correct answer"""
        correct = question_data['correct_answer']
        options = question_data['options']
        
        new_position = np.random.choice(['A', 'B', 'C', 'D'])
        if new_position != correct:
            options[correct], options[new_position] = options[new_position], options[correct]
            question_data['correct_answer'] = new_position

    def generate_question_batch(self, n_questions, topic=None, 
                            variance_factor=0.2, difficulty_distribution=None,
                            sampling_strategy='hybrid', hybrid_split=0.5):
        """
        Generate multiple questions with progress tracking
        
        Args:
            n_questions: Number of questions to generate
            topic: Main topic to focus on
            variance_factor: How much to vary parameters
            difficulty_distribution: Dict like {'very_easy': 0.1, 'easy': 0.2, ...}
            sampling_strategy: 'json_based', 'independent', or 'hybrid'
            hybrid_split: If hybrid, fraction of questions from JSON (default 0.5 = 50%)
        
        Returns:
            list: Generated questions
        
        Raises:
            RateLimitException: When API rate limit is reached
        """
        questions = []
        failed_count = 0
        
        # Define difficulty ranges
        difficulty_ranges = {
            'very_easy': (-3, -1),
            'easy': (-1, 0),
            'moderate': (0, 1),
            'difficult': (1, 2),
            'very_difficult': (2, 3)
        }
        
        # Determine which questions use which strategy
        if sampling_strategy == 'hybrid':
            n_from_json = int(n_questions * hybrid_split)
            n_independent = n_questions - n_from_json
            # Create array: True = use JSON, False = use independent
            use_json = np.array([True] * n_from_json + [False] * n_independent)
            np.random.shuffle(use_json)
        elif sampling_strategy == 'json_based':
            use_json = np.array([True] * n_questions)
        else:  # 'independent'
            use_json = np.array([False] * n_questions)
        
        for i in range(n_questions):
            current_topic = topic if topic else np.random.choice(self.available_topics)
            
            if current_topic not in self.available_topics:
                print(f"\n❌ Topic '{current_topic}' not found!")
                return []
            
            topic_items = self.irt_params[self.irt_params['main_topic'] == current_topic]
            subtag = np.random.choice(topic_items['concept_tag'].unique())
            
            # ✅ FIX: Determine dimension based on topic type
            dimension = self.get_dimension_for_topic(current_topic)
            
            # Determine strategy for this question
            from_json = use_json[i]
            strategy_label = "JSON" if from_json else "IND"
            
            if len(topic_items) > 0:
                sample = topic_items.sample(1).iloc[0]
                base_a = sample['a1'] if dimension == 'a1' else sample['a2']
                
                # Always add some variance to discrimination
                a_param = np.clip(
                    np.random.normal(base_a, abs(base_a) * variance_factor + 0.1), 
                    0.1, 3.0
                )
                
                # **HYBRID LOGIC: Choose b parameter strategy**
                if from_json:
                    # Strategy 1: Sample from JSON with variance
                    b_param = np.clip(
                        np.random.normal(sample['b'], abs(sample['b']) * variance_factor + 0.3), 
                        -3, 3
                    )
                else:
                    # Strategy 2: Independent difficulty sampling
                    if difficulty_distribution:
                        target_difficulty = np.random.choice(
                            list(difficulty_ranges.keys()),
                            p=list(difficulty_distribution.values())
                        )
                        b_min, b_max = difficulty_ranges[target_difficulty]
                        b_param = np.random.uniform(b_min, b_max)
                    else:
                        # Uniform across all difficulties
                        b_param = np.random.uniform(-3, 3)
            else:
                # Fallback
                stats = self.topic_stats[current_topic]
                a_param = np.random.uniform(0.5, 2.5)
                b_param = np.random.uniform(*stats['b_range'])
                strategy_label = "FALL"
            
            difficulty_desc = self.difficulty_to_description(b_param)
            print(f"\n[{i+1}/{n_questions}] [{strategy_label}] {current_topic} ({dimension}, {difficulty_desc}, b={b_param:.2f})", end=" ")
            
            try:
                question = self.generate_question(
                    current_topic, subtag, dimension, a_param, b_param
                )
                
                if question:
                    # Add metadata about sampling strategy
                    question['sampling_strategy'] = 'json_based' if from_json else 'independent'
                    questions.append(question)
                    print("✓")
                else:
                    failed_count += 1
                    print("✗")
            
            except RateLimitException as e:
                # Rate limit reached - stop immediately
                print(f"\n\n⛔ Rate limit reached after generating {len(questions)} questions")
                print("Stopping generation to preserve existing data...")
                raise  # Re-raise to be caught in main execution
        
        if failed_count > 0:
            print(f"\n⚠ Failed: {failed_count}/{n_questions} questions")
        
        return questions

    def display_question(self, question_data, question_number=None):
        """Display a question in readable format"""
        print("\n" + "─" * 80)
        if question_number:
            print(f"Question {question_number}")
        print(f"Topic: {question_data['main_topic']} → {question_data['concept_tag']}")
        print(f"Dimension: {question_data['dimension']} = {question_data[question_data['dimension']]:.2f}")
        print(f"Difficulty: {self.difficulty_to_description(question_data['b'])} (b={question_data['b']:.2f})")
        print("─" * 80)
        print(f"\n{question_data['question']}\n")
        
        for opt in ['A', 'B', 'C', 'D']:
            marker = " ✓" if opt == question_data['correct_answer'] else ""
            print(f"{opt}. {question_data['options'][opt]}{marker}")
        
        print(f"\nExplanation: {question_data['explanation']}")
        print("─" * 80)

    def save_questions(self, questions, filename='generated_questions_mirt.json'):
        """Save questions to JSON file"""
        existing = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    existing = json.load(f)
                print(f"\n✓ Found {len(existing)} existing questions")
            except:
                pass
        
        all_questions = existing + questions
        
        with open(filename, 'w') as f:
            json.dump(all_questions, f, indent=2)
        
        print(f"✓ Saved {len(all_questions)} total questions ({len(questions)} new)")


def load_irt_params_from_json(json_file):
    """Load MIRT parameters from JSON"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Ensure required columns
    if 'concept_tag' not in df.columns:
        df['concept_tag'] = 'general'
    if 'a1' not in df.columns:
        df['a1'] = df.get('a', 1.0)
    if 'a2' not in df.columns:
        df['a2'] = 0.0
    
    return df[['item', 'a1', 'a2', 'b', 'concept_tag']]


# Main execution
if __name__ == "__main__":
    print("="*80)
    print("MULTIDIMENSIONAL IRT QUESTION GENERATOR (FIXED DIMENSION ASSIGNMENT)")
    print("="*80)
    
    # UPDATE THIS PATH
    json_filename = r'D:\Internship\IRT\adaptive-exam\data\2pl_mirt.json'
    
    try:
        print(f"\nLoading parameters from {json_filename}...")
        irt_params = load_irt_params_from_json(json_filename)
        print(f"✓ Loaded {len(irt_params)} parameters")
        print(f"✓ Found {len(irt_params['concept_tag'].unique())} unique tags")
        
        # Initialize generator
        generator = MultidimensionalIRTQuestionGenerator(
            irt_params,
            existing_questions_file='generated_questions_mirt.json'
        )
        
        # Show available topics
        generator.list_available_topics()
        
        # Define target topics based on your actual dataset
        target_topics = [
            'Data Structures',
            'Algorithms',
            'Database',
            'Git',
            'Software Engineering',
            'Computer Architecture',
            'Linear Algebra',
            'Calculus',
            'Logic',
            'Probability',
            'Statistics',
            'Machine Learning',
            'Python',
            'Programming'
            ]
            
            
        
        
        # Verify topics exist
        available_topics_set = set(generator.available_topics)
        missing_topics = [topic for topic in target_topics if topic not in available_topics_set]
        
        if missing_topics:
            print("\n⚠ Missing topics:", missing_topics)
            print("\nAvailable topics:")
            for topic in sorted(generator.available_topics):
                print(f"  - {topic}")
        
        target_topics = [topic for topic in target_topics if topic in available_topics_set]
        print(f"\n✓ Proceeding with {len(target_topics)} topics")
        
        # Generate questions
        all_questions = []
        questions_per_topic = 20  # Adjust as needed
        rate_limit_reached = False
        
        for i, topic in enumerate(target_topics, 1):
            if rate_limit_reached:
                print(f"\n⚠ Skipping remaining topics due to rate limit")
                break
                
            print(f"\n{'='*80}")
            print(f"Topic {i}/{len(target_topics)}: {topic}")
            print(f"{'='*80}")
            
            balanced_difficulty = {
                'very_easy': 0.05,      # 5%
                'easy': 0.15,           # 15%
                'moderate': 0.30,       # 30%
                'difficult': 0.35,      # 35%
                'very_difficult': 0.15  # 15%
            }
            
            try:
                topic_questions = generator.generate_question_batch(
                    n_questions=questions_per_topic,
                    topic=topic,
                    difficulty_distribution=balanced_difficulty,
                    sampling_strategy='hybrid',
                    hybrid_split=0.5,
                    variance_factor=0.2
                )
                    
                all_questions.extend(topic_questions)
                print(f"✓ Generated {len(topic_questions)} questions")
            
            except RateLimitException as e:
                print(f"\n{'='*80}")
                print(f"⛔ RATE LIMIT REACHED - STOPPING GENERATION")
                print(f"{'='*80}")
                print(f"Successfully generated before rate limit: {len(all_questions)} questions")
                print(f"Completed topics: {i-1}/{len(target_topics)}")
                print(f"Remaining topics: {len(target_topics) - i}")
                rate_limit_reached = True
                break
            
        # Save whatever we generated (even if rate limit was hit)
        if len(all_questions) > 0:
            output_filename = 'generated_topic_questions_mirt.json'
            print(f"\n{'='*80}")
            if rate_limit_reached:
                print(f"💾 SAVING PARTIAL RESULTS")
                print(f"{'='*80}")
                print(f"Saving {len(all_questions)} successfully generated questions...")
            generator.save_questions(all_questions, output_filename)
            
            if rate_limit_reached:
                print(f"\n✓ Partial results saved successfully!")
                print(f"You can resume generation later for the remaining {len(target_topics) - i} topics")
                print(f"{'='*80}\n")
        else:
            print(f"\n⚠ No questions were generated before rate limit was reached")
            print(f"Nothing to save.")
        
        # Only show detailed analysis if we have questions
        if len(all_questions) > 0 and not rate_limit_reached:
            
            # Display samples
            print("\n" + "="*80)
            print("SAMPLE QUESTIONS (one per topic)")
            print("="*80)
            
            # Show one sample per topic
            for topic in target_topics[:5]:  # Show first 5 topics
                topic_qs = [q for q in all_questions if q['main_topic'] == topic]
                if topic_qs:
                    generator.display_question(topic_qs[0])
            
            # Dimension validation check
            print(f"\n{'='*80}")
            print(f"DIMENSION ASSIGNMENT VALIDATION")
            print(f"{'='*80}")
            
            for topic in target_topics:
                topic_qs = [q for q in all_questions if q['main_topic'] == topic]
                if topic_qs:
                    dimensions = [q['dimension'] for q in topic_qs]
                    dim_counts = {d: dimensions.count(d) for d in set(dimensions)}
                    expected_dim = generator.get_dimension_for_topic(topic)
                    status = "✓" if len(dim_counts) == 1 and expected_dim in dim_counts else "✗"
                    print(f"{status} {topic:<30} Expected: {expected_dim}, Got: {dim_counts}")
            
            # Sampling strategy breakdown
            print(f"\n{'='*80}")
            print(f"SAMPLING STRATEGY BREAKDOWN")
            print(f"{'='*80}")

            json_based = [q for q in all_questions if q.get('sampling_strategy') == 'json_based']
            independent = [q for q in all_questions if q.get('sampling_strategy') == 'independent']

            print(f"\nJSON-based questions: {len(json_based)} ({len(json_based)/len(all_questions)*100:.1f}%)")
            print(f"Independent questions: {len(independent)} ({len(independent)/len(all_questions)*100:.1f}%)")

            # Difficulty distribution by strategy
            for strategy, questions_subset in [('JSON-based', json_based), ('Independent', independent)]:
                print(f"\n{strategy} Difficulty Distribution:")
                b_ranges = {
                    'very easy (b < -1)': sum(1 for q in questions_subset if q['b'] < -1),
                    'easy (-1 ≤ b < 0)': sum(1 for q in questions_subset if -1 <= q['b'] < 0),
                    'moderate (0 ≤ b < 1)': sum(1 for q in questions_subset if 0 <= q['b'] < 1),
                    'difficult (1 ≤ b < 2)': sum(1 for q in questions_subset if 1 <= q['b'] < 2),
                    'very difficult (b ≥ 2)': sum(1 for q in questions_subset if q['b'] >= 2),
                }
                for difficulty, count in b_ranges.items():
                    if len(questions_subset) > 0:
                        print(f"  • {difficulty}: {count} ({count/len(questions_subset)*100:.1f}%)")
        else:
            print(f"\n{'='*80}")
            print("⚠ IMPORTANT: Existing data file was NOT modified")
            print(f"Generated {len(all_questions)} questions are NOT saved")
            print("Please check your API rate limits and try again later")
            print(f"{'='*80}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_filename}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()