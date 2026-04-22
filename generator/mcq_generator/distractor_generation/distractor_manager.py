# distractor_manager.py

import re
import logging
from typing import List, Dict
from .config import Config
from .agents.numeric_agent import NumericAgent
from .agents.llm_agent import LLMAgent
from .agents.hybrid_agent import HybridAgent
from .utils import token_similarity,text_similarity

logging.basicConfig(level=logging.INFO)


class DistractorManager:
    """
    Central controller for distractor generation and validation.

    Handles:
    - pure numeric answers (e.g. 3, 3.14, 1/2)
    - numeric-like answers (e.g. 78%, Approximately 68%)
    - textual answers (conceptual, theoretical, coding)
    """

    def __init__(self, config: Config):
        self.config = config
        self.numeric_agent = NumericAgent()
        self.llm_agent = LLMAgent(config) if config.USE_LLM else None

        if config.USE_LLM and config.AGENT_TYPE == "hybrid":
            self.hybrid_agent = HybridAgent(config, self.llm_agent)
            logging.info("Hybrid agent initialized.")
        else:
            self.hybrid_agent = None
            logging.info("Hybrid agent not initialized.")

    # ============================================================
    # PUBLIC API
    # ============================================================
    def generate_distractors(self, question: Dict) -> List[Dict]:
        """
        Generate distractors and apply category-aware validation.
        """
        answer = question["answer"]
        q_type = question["type"]
        concept_tag = question.get("concept_tag", "")

        category = self._answer_category(answer)
        logging.info(f"Answer category detected: {category}")

        # -------- Agent selection --------
        if category == "pure_numeric" and q_type == "mathematical":
            logging.info("Using NumericAgent.")
            distractors = self.numeric_agent.generate(answer)

        elif self.config.AGENT_TYPE == "hybrid" and self.hybrid_agent:
            logging.info("Using HybridAgent.")
            distractors = self.hybrid_agent.generate(
                stem=question["stem"],
                answer=answer,
                q_type=q_type,
                concept_tag=concept_tag
            )

        elif self.config.AGENT_TYPE == "llm" and self.llm_agent:
            logging.info("Using LLMAgent.")
            distractors = self.llm_agent.generate(
                stem=question["stem"],
                answer=answer,
                q_type=q_type,
                concept_tag=concept_tag
            )

        else:
            distractors = []

        # -------- Validation --------
        filtered = self._filter_distractors(
            distractors=distractors,
            correct_answer=answer,
            category=category
        )

        return filtered[: self.config.MAX_DISTRACTORS_PER_QUESTION]

    # ============================================================
    # ANSWER CLASSIFICATION
    # ============================================================
    def _is_purely_numeric(self, text: str) -> bool:
        """
        Matches answers that are ONLY numeric.
        """
        patterns = [
            r'^[0-9]+$',             # 7
            r'^[0-9]+\.[0-9]+$',     # 3.14
            r'^[0-9]+/[0-9]+$',      # 1/2
            r'^π$',                  # π
            r'^e$',                  # e
            r'^[0-9]+π$',            # 25π
        ]
        text = text.strip().lower()
        return any(re.match(p, text) for p in patterns)

    def _is_numeric_like(self, text: str) -> bool:
        """
        Numeric values mixed with words, units, or approximations.
        """
        text = text.strip().lower()
        if self._is_purely_numeric(text):
            return False
        return bool(re.search(r'\d', text))

    def _answer_category(self, answer: str) -> str:
        """
        Categorize the answer for validation logic.
        """
        if self._is_purely_numeric(answer):
            return "pure_numeric"
        elif self._is_numeric_like(answer):
            return "numeric_like"
        return "textual"

    # ============================================================
    # NUMERIC HELPERS
    # ============================================================
    def _extract_number(self, text: str):
        """
        Extract first numeric value from text.
        """
        match = re.search(r'\d+(\.\d+)?', text)
        return float(match.group()) if match else None

    # ============================================================
    # FILTERING / VALIDATION
    # ============================================================
    def _filter_distractors(
        self,
        distractors: List[Dict],
        correct_answer: str,
        category: str
    ) -> List[Dict]:
        """
        Category-aware distractor validation.
        """
        valid = []
        seen = set()
        correct_key = correct_answer.strip().lower()
        correct_num = self._extract_number(correct_answer)

        for d in distractors:
            if not isinstance(d, dict):
                continue

            text = d.get("text", "")
            if not isinstance(text, str):
                continue

            text = text.strip()
            if not text:
                continue

            key = text.lower()

            # ---- Deduplication ----
            if key in seen or key == correct_key:
                continue
            seen.add(key)

            # similarity = text_similarity(text, correct_answer)
            
            char_sim = text_similarity(text, correct_answer)
            token_sim = token_similarity(text, correct_answer)

            # ====================================================
            # CATEGORY-SPECIFIC VALIDATION
            # ====================================================
            if category == "textual":
                # Conceptual / theoretical / coding answers
                if char_sim > 0.9 and token_sim > 0.8:
                    continue

            elif category == "numeric_like":
                # Allow high similarity; compare numeric values instead
                distractor_num = self._extract_number(text)
                if (
                    correct_num is not None
                    and distractor_num is not None
                    and correct_num == distractor_num
                ):
                    continue

            elif category == "pure_numeric":
                # NumericAgent already handles numeric variation
                pass

            # ---- Normalize fields ----
            d["text"] = text
            d["_sim"] = char_sim,token_sim
            d.setdefault("type", category)
            d.setdefault("source", "generated")
            d.setdefault("rationale", "Plausible misconception-based distractor")
            d["_score"] = (0.7 * token_sim) - (0.5 * char_sim)
            valid.append(d)

        # Prefer mid-similarity distractors
        # valid.sort(key=lambda x: abs(x["_sim"] - 0.5))
        
        valid.sort(key=lambda x: x["_score"], reverse=True)
        return valid
