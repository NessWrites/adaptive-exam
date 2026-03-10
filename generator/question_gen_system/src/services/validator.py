from generator.question_gen_system.src.agents.prompt_registry import validator_task, system_message
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from typing import Dict, List

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY_FOR_VALIDATION")
MODEL_NAME = os.getenv("VALIDATOR_MODEL")

def system_prompt(batch: List[Dict]):

    formatted_questions = []
    for idx, row in enumerate(batch):
        formatted_questions.append(
            {
                "id": idx,
                "question" : row.question,
                "context" : row.context,
                "bloom_level" : row.bloom_level
            }
        )
    prompt = f"""
        You are given a dataset where each row is completely independent of the others.
        {validator_task}
        Evaluate the following questions for accuracy and clarity.
        IMPORTANT:
        - Process EACH row independently.
        - Do NOT use information from other rows.
        - Return results in the SAME ORDER as input.
        - Output must be valid JSON.
        - no extra language needed like [Here is the evaluation of the given questions based on the provided context and Bloom\'s Taxonomy levels:\n\n\n] completely avoid.

        INPUT_DATA:
        {json.dumps(formatted_questions, indent=2)}
        """
    return prompt



def validate_batch(batch):
    prompt = system_prompt(batch)
    
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
    
    response = model.generate_content(prompt, generation_config = {
        "response_mime_type" : "application/json",
        "temperature" : 0.0
    }
    )

    content = response.text

    try:
        scores = json.loads(content)
    except Exception as e:
        raise ValueError(e)
    
    validated_rows = []
    for score in scores:
        row = batch[score['id']].model_dump()
        row['bloom_score'] = score['bloom_score']
        row["context_score"] = score['context_score']
        row['reason'] = score['reason']
        row['total_marks'] = score['total_marks']

        validated_rows.append(row)
    
    return validated_rows