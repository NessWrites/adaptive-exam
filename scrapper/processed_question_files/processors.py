import json
import os
import time
import google.generativeai as genai
from tqdm import tqdm
import logging
import glob

# --- Configuration ---
INPUT_DIRECTORY = '.' # Directory to search for .json files
PROCESSED_SUFFIX = '_processed.json' # Suffix to add to processed files
CACHE_FILE_PATH = 'gemini_cache.json'
MODEL_NAME = 'gemini-2.5-flash-preview-09-2025'
RETRIES = 3
# Base delay for exponential backoff (in seconds)
BASE_DELAY = 5 
# Rate limit delay to stay under 10 RPM (60s / 10 req = 6s) + 0.1s buffer
RATE_LIMIT_DELAY = 6.1 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Gemini API System Instruction and Schema ---
# This system instruction tells the model exactly what to do and what format to use.
SYSTEM_INSTRUCTION = """
You are an expert in AI and Data Science education. Your task is to classify questions based on two dimensions: topic and cognitive level.
You MUST respond ONLY with a valid JSON object matching the provided schema.

1.  **Topic Dimension:** Choose the *single best* topic from this list:
    * 'ANN' (Artificial Neural Networks)
    * 'CNN' (Convolutional Neural Networks)
    * 'Ensemble Models' (e.g., Random Forest, Boosting)
    * 'Linear Models' (e.g., Linear/Logistic Regression, SVM, Least Squares)
    * 'MLOps' (Model Deployment, Monitoring, Lifecycle)
    * 'Statistics' (e.g., Hypothesis testing, p-values, distributions, PCA)
    * 'Probabilities' (e.g., Bayes' theorem, conditional probability)
    * 'Natural Language Processing' (NLP, e.g., Transformers, text processing)
    * 'Unsupervised Learning' (e.g., Clustering, Dimensionality Reduction)
    * 'General ML Concepts' (e.g., Overfitting, bias-variance, evaluation metrics)
    * 'Math' (e.g., Linear Algebra, Calculus)
    * 'Computer Vision' (e.g., Image processing, object detection, CV-related CNNs)
    * 'Decision Trees' (e.g., CART, ID3, C4.5)
    * 'Other' (If no other category fits)

2.  **Cognitive Dimension:** Choose the *single best* cognitive level from this list:
    * 'Knowledge': Recalling facts, definitions, or simple concepts. (e.g., "What is...")
    * 'Application': Using a concept or method in a concrete situation. (e.g., "Calculate...", "Apply the formula...")
    * 'Analysis': Breaking down information, comparing/contrasting, or inferring. (e.g., "Why does...", "Compare...", "What is the primary objective...")
"""

# This schema forces the model to output clean, predictable JSON.
GEMINI_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "topic_dimension": {
            "type": "STRING",
            "enum": [
                'ANN', 'CNN', 'Ensemble Models', 'Linear Models', 'MLOps',
                'Statistics', 'Probabilities', 'Natural Language Processing',
                'Unsupervised Learning', 'General ML Concepts', 'Math',
                'Computer Vision', 'Decision Trees', 'Other'
            ]
        },
        "cognitive_dimension": {
            "type": "STRING",
            "enum": ['Knowledge', 'Application', 'Analysis']
        }
    },
    "required": ["topic_dimension", "cognitive_dimension"]
}

# --- Helper Functions ---

def load_json(filepath):
    """Loads a JSON file from the given path."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"File not found: {filepath}. Returning empty structure.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {filepath}. Returning empty structure.")
        return {}

def save_json(data, filepath):
    """Saves data to a JSON file at the given path."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logging.error(f"Could not write to file {filepath}: {e}")

def load_cache():
    """Loads the question processing cache from CACHE_FILE_PATH."""
    return load_json(CACHE_FILE_PATH)

def save_cache(cache):
    """Saves the cache to CACHE_FILE_PATH."""
    save_json(cache, CACHE_FILE_PATH)

def extract_unique_questions(data):
    """Extracts unique questions (text and img_url) from the raw data structure."""
    unique_questions = {} # Store as {q_text: {q_text, img_url}}
    if not isinstance(data, dict):
        logging.error("Input data is not a dictionary as expected. Cannot extract questions.")
        return []
        
    for student_name, student_data in data.items():
        if 'questions' in student_data and isinstance(student_data['questions'], list):
            for question in student_data['questions']:
                if 'question_text' in question:
                    q_text = question['question_text']
                    if q_text not in unique_questions:
                        # Store the minimal object needed
                        unique_questions[q_text] = {
                            "question_text": q_text,
                            "img_url": question.get("img_url") # Use .get() for safety
                        }
    
    return list(unique_questions.values()) # Return a list of dicts

def get_dimensions_from_gemini(model, question_text):
    """
    Calls the Gemini API to get dimensions for a single question text.
    Includes exponential backoff retry logic.
    """
    logging.info(f"Calling Gemini for: {question_text[:50]}...")
    for attempt in range(RETRIES):
        try:
            # The model is already configured with system instructions and JSON mode
            response = model.generate_content(question_text)
            
            # Extract and parse the JSON text
            response_json = json.loads(response.text)
            
            # Validate required keys are present
            if 'topic_dimension' in response_json and 'cognitive_dimension' in response_json:
                return response_json
            else:
                logging.warning(f"Gemini response missing keys for question: {question_text[:50]}...")
                
        except Exception as e:
            logging.error(f"Gemini API call failed (Attempt {attempt + 1}/{RETRIES}): {e}")
            if attempt < RETRIES - 1:
                # --- MODIFIED ---
                # Implement exponential backoff
                sleep_time = BASE_DELAY * (2 ** attempt) 
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                # --- END MODIFIED ---
            
    logging.error(f"Failed to process question after {RETRIES} retries: {question_text[:50]}...")
    return {'topic_dimension': 'Error', 'cognitive_dimension': 'Error'}

# --- Main Execution ---

def main():
    """Main function to run the processing script."""
    
    # 1. Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY environment variable not set.")
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set the variable and try again. See README.md for instructions.")
        return

    # 2. Configure Gemini
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": GEMINI_SCHEMA
        }
        
        model = genai.GenerativeModel(
            MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=generation_config
        )
    except Exception as e:
        logging.error(f"Failed to configure Gemini model: {e}")
        return

    logging.info("Gemini model configured successfully.")

    # 3. Load Cache and Find Files
    cache = load_cache()
    logging.info(f"Loaded {len(cache)} items from cache.")

    all_json_files = glob.glob(os.path.join(INPUT_DIRECTORY, '*.json'))
    input_files_to_process = []
    
    for f in all_json_files:
        # Use os.path.basename to handle files in subdirs if INPUT_DIRECTORY is complex
        filename = os.path.basename(f)
        if filename.endswith(PROCESSED_SUFFIX) or filename == CACHE_FILE_PATH:
            logging.info(f"Skipping {f} (cache or already processed).")
            continue
        input_files_to_process.append(f)
    
    if not input_files_to_process:
        logging.warning(f"No new .json files found in '{INPUT_DIRECTORY}'. Exiting.")
        return
        
    logging.info(f"Found {len(input_files_to_process)} JSON files to process.")

    # 4. Phase 1: Aggregate All Unique Questions
    all_data = {} # To store loaded JSON data in memory {filepath: data}
    all_unique_questions = {} # To store unique question objects {q_text: {q_text, img_url}}

    for filepath in tqdm(input_files_to_process, desc="Phase 1/3: Aggregating questions"):
        data = load_json(filepath)
        if not data:
            logging.warning(f"Could not load data from {filepath}, skipping.")
            continue
        
        all_data[filepath] = data
        file_unique_q_objects = extract_unique_questions(data) # This is now a list of dicts
        
        for q_obj in file_unique_q_objects:
            q_text = q_obj["question_text"]
            if q_text not in all_unique_questions:
                all_unique_questions[q_text] = q_obj # Store the whole object

    unique_q_list = list(all_unique_questions.values()) # This is the list of dicts
    logging.info(f"Found {len(unique_q_list)} total unique questions across {len(all_data)} files.")

    # 5. Phase 2: Process Unique Questions (using cache)
    dimension_map = {}
    new_questions_processed = 0

    try:
        # Loop over the list of unique question objects
        for q_obj in tqdm(unique_q_list, desc="Phase 2/3: Processing questions"):
            q_text = q_obj["question_text"]
            img_url = q_obj.get("img_url")

            # --- RULE 1: Check for image URL ---
            if img_url:
                logging.info(f"Image found for: {q_text[:50]}... Setting to 'Other'/'Analysis'.")
                dimension_map[q_text] = {'topic_dimension': 'Other', 'cognitive_dimension': 'Analysis'}
                continue # Move to the next question
            
            # --- RULE 2: Check cache ---
            # Also check if the cached value is "Error", if so, re-process
            if q_text in cache and cache[q_text].get('topic_dimension') != 'Error':
                dimension_map[q_text] = cache[q_text]
            
            # --- RULE 3: Call API ---
            else:
                dimensions = get_dimensions_from_gemini(model, q_text)
                dimension_map[q_text] = dimensions
                cache[q_text] = dimensions # Cache result (even if it's 'Error')
                new_questions_processed += 1
                
                # Save cache immediately after each new API call
                if new_questions_processed % 1 == 0: # Save every 1 new item
                    save_cache(cache)
                
                # --- MODIFIED ---
                # Add a sleep to respect the 10 RPM free tier limit
                logging.info(f"Pausing for {RATE_LIMIT_DELAY}s to respect rate limit...")
                time.sleep(RATE_LIMIT_DELAY) 
                # --- END MODIFIED ---
    
    except KeyboardInterrupt:
        logging.warning("Script interrupted. Saving cache...")
        save_cache(cache)
        print("\nProcess interrupted. Cache saved. Exiting.")
        return
    finally:
        # Final cache save
        save_cache(cache)
        logging.info(f"Processing complete. {new_questions_processed} new questions processed and cached.")

    # 6. Phase 3: Re-inject Dimensions into Original Data and Save
    logging.info("Phase 3/3: Injecting dimensions and saving files...")
    for filepath, data in all_data.items():
        for student_name, student_data in data.items():
            if 'questions' in student_data and isinstance(student_data['questions'], list):
                for question in student_data['questions']:
                    q_text = question.get('question_text')
                    if q_text in dimension_map:
                        question['topic_dimension'] = dimension_map[q_text].get('topic_dimension')
                        question['cognitive_dimension'] = dimension_map[q_text].get('cognitive_dimension')
        
        # 7. Save Processed Data
        base, _ = os.path.splitext(filepath)
        output_filepath = f"{base}{PROCESSED_SUFFIX}"
        save_json(data, output_filepath)
        logging.info(f"Successfully saved processed data to {output_filepath}")

    print(f"\nDone! Processed {len(all_data)} files.")

if __name__ == "__main__":
    main()

