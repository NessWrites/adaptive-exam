"""
DistractorBridge

Responsibility: Orchestrate the DistractorManager and produce a
finalized options dict ready for PostgreSQL persistence.

This is the ONLY file in the main app that knows about DistractorManager.
All coupling to the distractor app is contained here.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Tuple

from generator.mcq_generator.services.distractor_config_adapter import (
    DistractorConfigAdapter,
    get_distractor_config,
)

# Import the distractor app after making it a package (Step 1)
from generator.mcq_generator.distractor_generation.distractor_manager import DistractorManager

logger = logging.getLogger(__name__)

# Minimum acceptable distractors before fallback triggers
_MIN_DISTRACTORS = 3
_OPTION_KEYS = ["A", "B", "C", "D"]

# Keywords that signal a mathematical/numeric question type
_NUMERIC_SIGNALS = {
    "time complexity", "space complexity", "big o", "o(", "θ(", "ω(",
    "probability", "expected value", "mean", "variance",
}


class DistractorBridge:
    """
    Async-safe bridge between MCQService and DistractorManager.

    Injected into MCQService via FastAPI's dependency injection system.
    One instance per request (or singleton — both work since DistractorManager
    is stateless per-call).
    """

    def __init__(self, config: Optional[DistractorConfigAdapter] = None):
        self.config = config or get_distractor_config()
        # DistractorManager is instantiated once per bridge instance.
        # It is cheap to construct (just loads a JSON file).
        self._manager = DistractorManager(self.config)

    # ------------------------------------------------------------------ #
    # PUBLIC API                                                           #
    # ------------------------------------------------------------------ #

    async def build_options_dict(
        self,
        stem: str,
        correct_answer: str,
        concept_tag: str,
        domain: str,
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Main entry point called by MCQService.

        Args:
            stem:           The MCQ question text from Gemini.
            correct_answer: The correct answer text from Gemini (no letter prefix).
            concept_tag:    e.g. "binary_search", "recursion", "time_complexity"
            domain:         e.g. "Computer Science", "Mathematics"

        Returns:
            Tuple of:
              options_dict:       {"A": "...", "B": "...", "C": "...", "D": "..."}
              correct_answer_dict: {"key": "B", "text": "..."}  ← for DB storage
        """
        question_dict = self._build_question_dict(stem, correct_answer, concept_tag)

        # Run the synchronous DistractorManager in a thread pool.
        # asyncio.to_thread is available in Python 3.9+.
        # For 3.8 compatibility, use: loop.run_in_executor(None, ...)
        try:
            raw_distractors: List[Dict] = await asyncio.to_thread(
                self._manager.generate_distractors, question_dict
            )
            logger.info(
                "DistractorManager returned %d distractors for concept '%s'",
                len(raw_distractors),
                concept_tag,
            )
        except Exception as exc:
            logger.error(
                "DistractorManager raised an exception: %s. Triggering fallback.",
                exc,
                exc_info=True,
            )
            raw_distractors = []

        # Apply fallback if insufficient distractors were produced
        distractor_texts = self._extract_texts(raw_distractors)
        if len(distractor_texts) < _MIN_DISTRACTORS:
            distractor_texts = self._apply_fallback(
                correct_answer=correct_answer,
                concept_tag=concept_tag,
                existing=distractor_texts,
            )

        # Take exactly 3 distractors (correct_answer fills the 4th slot)
        final_distractors = distractor_texts[:_MIN_DISTRACTORS]

        return self._assemble_options(correct_answer, final_distractors)

    # ------------------------------------------------------------------ #
    # PRIVATE HELPERS                                                      #
    # ------------------------------------------------------------------ #

    def _build_question_dict(
        self,
        stem: str,
        correct_answer: str,
        concept_tag: str,
    ) -> Dict:
        """
        Translate MCQCoreLLMOutput fields into the Dict contract
        that DistractorManager.generate_distractors() expects.
        """
        return {
            "stem": stem,
            "answer": correct_answer,
            "concept_tag": concept_tag,
            # Infer question type so NumericAgent is triggered for numeric answers
            "type": self._infer_question_type(correct_answer, concept_tag),
        }

    @staticmethod
    def _infer_question_type(correct_answer: str, concept_tag: str) -> str:
        """
        Heuristic: if the answer looks numeric, or the concept tag signals
        a numeric domain, use "mathematical" to trigger the NumericAgent.
        Otherwise use "conceptual".
        """
        answer_lower = correct_answer.strip().lower()
        tag_lower = concept_tag.lower()

        # Purely numeric answer (integer, float, fraction, Big-O notation)
        import re
        is_numeric_answer = bool(
            re.match(r'^[\d\.\+\-\/\(\)OΘΩon\s\*\^logn]+$', answer_lower)
        )
        has_numeric_tag = any(sig in tag_lower for sig in _NUMERIC_SIGNALS)

        if is_numeric_answer or has_numeric_tag:
            return "mathematical"
        return "conceptual"

    @staticmethod
    def _extract_texts(raw_distractors: List[Dict]) -> List[str]:
        """
        Extract the 'text' field from DistractorManager's output dicts.
        Filter out any empty or malformed entries.
        """
        texts = []
        for d in raw_distractors:
            if isinstance(d, dict):
                text = d.get("text", "").strip()
                if text:
                    texts.append(text)
        return texts

    @staticmethod
    def _apply_fallback(
        correct_answer: str,
        concept_tag: str,
        existing: List[str],
    ) -> List[str]:
        """
        Fallback distractor generation when DistractorManager returns < 3 results.

        Strategy (in order of preference):
          1. Pad with generic but plausible misconception templates
          2. Never produce duplicates
          3. Never produce the correct answer

        These are intentionally generic — they signal to instructors that
        manual review is needed (tracked by the 'source' field in the DB).
        """
        fallback_templates = [
            f"A common misconception about {concept_tag}",
            f"An incorrect application of {concept_tag} principles",
            f"A frequently confused alternative to: {correct_answer}",
            f"A partial understanding of {concept_tag} that leads to an error",
        ]

        result = list(existing)  # copy
        for template in fallback_templates:
            if len(result) >= _MIN_DISTRACTORS:
                break
            if template not in result and template != correct_answer:
                result.append(template)
                logger.warning(
                    "Fallback distractor used for concept '%s': '%s'",
                    concept_tag,
                    template,
                )

        return result

    @staticmethod
    def _assemble_options(
        correct_answer: str,
        distractor_texts: List[str],
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Shuffle the correct answer and 3 distractors into A/B/C/D.

        Returns:
            options_dict:        {"A": "text", "B": "text", "C": "text", "D": "text"}
            correct_answer_dict: {"key": "C", "text": "the correct text"}
        """
        pool = [correct_answer] + distractor_texts[:_MIN_DISTRACTORS]
        random.shuffle(pool)

        options_dict: Dict[str, str] = {
            key: text for key, text in zip(_OPTION_KEYS, pool)
        }

        # Find which letter the correct answer landed on
        correct_key = next(
            key for key, text in options_dict.items() if text == correct_answer
        )
        correct_answer_dict = {"key": correct_key, "text": correct_answer}

        return options_dict, correct_answer_dict