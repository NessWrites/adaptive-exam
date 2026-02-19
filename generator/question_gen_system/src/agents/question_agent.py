import json
import google.generativeai as genai
from typing import Dict
from generator.question_gen_system.src.agents.prompt_registry import DOMAIN_PERSONAS

class HydrationAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initializes Google GenAI (Gemini).
        Using gemini-1.5-flash as it is fast and supports JSON mode.
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    async def hydrate(self,domain: str, concept: str, level: int, skeleton: str) -> Dict:
        """
        Calls Gemini to turn a skeleton into a robust, solvable question.
        """
        persona = DOMAIN_PERSONAS.get(domain.lower(), DOMAIN_PERSONAS['math'])

        prompt = f"""
        {persona}
        Task: Hydrate this {domain} skeletion into a complete exam question.

        Rules:
        1. Use realistic values for the context.
        2. Ensure the math/logic is robust
        3. Return result strictly in JSON format.

        Input Details:
        - Concept ID: {concept}
        - Bloom Level: {level}
        - Skeleton: {skeleton}

        Required JSON structure:
        {{
            "scenario_expansion": "Brief technical context",
            "final_question": "Complete question text with math values",
            "solution_steps": ["Step 1...", "Step 2..."],
            "final_answer": "Short answer"
        }}
        """

        try:
            # Gemini's generate_content is synchronous by default; 
            # for a true async FastAPI app, we wrap it in a thread or use a loop
            response = self.model.generate_content(prompt)
            
            # Gemini returns the string in response.text
            return json.loads(response.text)
            
        except Exception as e:
            return {
                "error": "Failed to hydrate question with Google GenAI",
                "details": str(e)
            }