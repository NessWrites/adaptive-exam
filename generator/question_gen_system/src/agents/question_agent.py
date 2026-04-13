import json
import google.generativeai as genai
from typing import Dict
from generator.question_gen_system.src.agents.prompt_registry import DOMAIN_PERSONAS

class HydrationAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initializes Google GenAI (Gemini).
        Using gemini-2.5-flash as it is fast and supports JSON mode.
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    async def hydrate(self,domain: str, concept: str, level: int, skeleton: str, num_questions: int) -> Dict:
        """
        Calls Gemini to turn a skeleton into a robust, solvable question.
        """
        persona = DOMAIN_PERSONAS.get(domain.lower(), DOMAIN_PERSONAS['math'])

        prompt = f"""
            {persona}

            Task: Hydrate the provided {domain} exam question skeleton into {num_questions} complete, unique exam questions. 

            Rules for Generation:
            1. Uniqueness: Vary the contexts, realistic values, and scenarios for each question while maintaining the core logic of the skeleton.
            2. Robustness: Ensure the math, logic, and phrasing are perfectly robust and solvable.
            3. Bloom's Taxonomy: strictly adhere to the cognitive complexity of the specified Bloom Level.
            4. Formatting: Return the output strictly as a JSON object containing a single key "questions" mapping to an array of strings. 
            5. No Preamble: Do not include markdown formatting (like ```json), conversational text, or explanations. Just output the raw JSON.

            Input Details:
            - Concept ID: {concept}
            - Bloom Level: {level}
            - Skeleton: {skeleton}

            Required JSON Structure:
            {{
             "questions": [
               "Full text of question 1...",
               "Full text of question 2...",
               "Full text of question 3..."
             ]
            }}
            """

        try:
            # Gemini's generate_content is synchronous by default; 
            # for a true async FastAPI app, we wrap it in a thread or use a loop
            response = self.model.generate_content(prompt)
            
            # Gemini returns the string in response.text
            result = json.loads(response.text)
            
            # Extract tokens
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "usage_metadata"):
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            
            result["usage"] = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens
            }
            return result
            
        except Exception as e:
            return {
                "error": "Failed to hydrate question with Google GenAI",
                "details": str(e)
            }