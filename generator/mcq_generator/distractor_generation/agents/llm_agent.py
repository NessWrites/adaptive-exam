
# agents/llm_agent.py
import json
import re
from typing import List, Dict
from ..config import Config
import logging 
from ..utils import text_similarity
logging.basicConfig(level=logging.INFO)

class LLMAgent:
    """Pure LLM agent for generating all types of distractors."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = self._init_groq_client()
    
    def _init_groq_client(self):
        """Initialize Groq client if available."""
        if not self.config.USE_LLM:
            return None
        
        try:
            from groq import Groq
            if not self.config.GROQ_API_KEY:
                print("⚠️  GROQ_API_KEY not set")
                return None
            logging.info("Groq client initialized successfully.")
            return Groq(api_key=self.config.GROQ_API_KEY)
            
        except ImportError:
            logging.info("Groq client not installed")
            print("⚠️  groq package not installed")
            return None
        except Exception as e:
            print(f"⚠️  Error initializing Groq: {e}")
            return None
    
    def generate(self, stem: str, answer: str, q_type: str, concept_tag: str = "") -> List[Dict]:
        """Generate distractors using only LLM."""
        if not self.client:
            return self._generate_fallback(answer)
        
        prompt = self._build_prompt(stem, answer, q_type, concept_tag)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You generate high-quality multiple-choice distractors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.MAX_TOKENS
            )
            logging.info("LLM response received successfully.")
            return self._parse_response(
                response.choices[0].message.content,
                answer,
                concept_tag
            )
            
        except Exception as e:
            print(f"⚠️  LLM Error: {e}")
            return self._generate_fallback(answer)
            
    def _build_prompt(self, stem: str, answer: str, q_type: str, concept_tag: str) -> str:
        return f"""
        You are an expert educational assessment designer.

        TASK:
        Generate exactly 4 high-quality distractors for the following multiple-choice question.

        QUESTION:
        {stem}

        CORRECT ANSWER:
        {answer}

        QUESTION TYPE:
        {q_type}

        CONCEPT TAG:
        {concept_tag}

        DISTRACTOR DESIGN RULES:
        1. Each distractor must represent a **common student misconception** related to "{concept_tag}".
        2. Distractors must be **tricky, witty, and highly plausible**. They should require deep thought to eliminate.
        3. Do NOT repeat or paraphrase the correct answer.
        4. Avoid trivial, absurd, or obviously wrong options. Make the student think!
        5. Generate exactly **4 distractors**.

        TYPE-SPECIFIC RULES:
        - If the question is **numerical**:
        - Distractors should result from common calculation mistakes or misapplying a formula
        - Values should be numerically close to the correct answer
        - If the question is **theoretical or conceptual**:
        - Distractors should reflect deep misunderstandings, subtle partial truths, or convincingly misapplied definitions

        OUTPUT FORMAT:
        Return ONLY a valid JSON array (no extra text).

        Each distractor must follow this schema:

        [
        {{
            "text": "<distractor option>",
            "type": "{q_type}",
            "source": "llm",
            "rationale": "<specific misconception that leads to this answer>"
        }}
        ]

        IMPORTANT:
        - Use double quotes only (valid JSON).
        - Do not include explanations outside the JSON.
        - Ensure rationales clearly describe the misconception.
        """
    
    # In llm_agent.py, fix the parsing:
    def _parse_response(self, response: str, correct_answer: str, concept_tag: str) -> List[Dict]:
        response = response.strip()
        
        # Clean the response - remove markdown code blocks
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            data = json.loads(response)
            if not isinstance(data, list):
                print(f"❌ LLM response not a list: {type(data)}")
                return []
            
            distractors = []
            for item in data:
                if isinstance(item, dict) and "text" in item:
                    text = str(item["text"]).strip()
                    if not text or text.lower() == correct_answer.lower():
                        continue
                        
                    distractors.append({
                        "text": text,
                        "type": item.get("type", "llm"),
                        "source": "llm",
                        "rationale": item.get("rationale", f"LLM-generated for {concept_tag}"),
                        "_sim": text_similarity(text, correct_answer)
                    })
            
            return distractors
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM JSON: {e}")
            print(f"Response was: {response[:200]}...")
            return []
        
    
    def _generate_fallback(self, answer: str) -> List[Dict]:
        """Generate generic fallback distractors."""
        return [
            {
                "text": f"A common error students make with: {answer}",
                "type": "misconception",
                "source": "hybrid_fallback",
                "rationale": "Generic misconception",
                "_sim": 0.3
            },
            {
                "text": f"An incorrect variation of: {answer}",
                "type": "semantic",
                "source": "hybrid_fallback",
                "rationale": "Generic semantic variation",
                "_sim": 0.4
            }
        ]    