"""
SIMPLE Numeric Agent
Handles:
- Integers      → 35
- Floats        → 12.5
- Fractions     → 1/2
"""

import re
from typing import List, Dict
from fractions import Fraction
import logging

logging.basicConfig(level=logging.INFO)

class NumericAgent:
    def generate(self, correct_answer: str, n: int = 4) -> List[Dict]:
        correct_answer = correct_answer.strip()
        distractors = []

        # ---------- FRACTION ----------
        if self._is_fraction(correct_answer):
            return self._fraction_distractors(correct_answer, n)

        # ---------- INTEGER / FLOAT ----------
        try:
            if '.' in correct_answer:
                value = float(correct_answer)
                is_integer = False
            else:
                value = int(correct_answer)
                is_integer = True
        except ValueError:
            return []

        common_errors = self._numeric_errors(value, is_integer)

        for wrong_value in common_errors:
            if len(distractors) >= n:
                break

            if wrong_value == value:
                continue

            text = (
                str(int(wrong_value)) if is_integer
                else f"{wrong_value:.2f}"
            )

            distractors.append({
                "text": text,
                "type": "numeric_error",
                "source": "numeric_agent",
                "rationale": "Common arithmetic mistake"
            })

            logging.info(f"Generated numeric distractor: {text}")

        return distractors[:n]

    # ---------- HELPERS ----------

    def _is_fraction(self, text: str) -> bool:
        return bool(re.match(r'^[0-9]+/[0-9]+$', text))

    def _fraction_distractors(self, answer: str, n: int) -> List[Dict]:
        frac = Fraction(answer)
        num, den = frac.numerator, frac.denominator

        candidates = set()

        # Common student mistakes
        candidates.add(f"{num*2}/{den*2}")     # not simplified
        candidates.add(f"{num}/{den*2}")       # denominator error
        candidates.add(f"{num*2}/{den}")       # numerator error

        if num > 1 and den > 1:
            candidates.add(f"{num+1}/{den+1}") # wrong reduction

        # Decimal confusion
        candidates.add(f"{float(frac)}")

        distractors = []
        for c in candidates:
            if len(distractors) >= n:
                break
            if c == answer:
                continue

            distractors.append({
                "text": c,
                "type": "numeric_error",
                "source": "numeric_agent",
                "rationale": "Fraction simplification mistake"
            })

            logging.info(f"Generated fraction distractor: {c}")

        return distractors[:n]

    def _numeric_errors(self, value, is_integer):
        if is_integer:
            return [
                value + 1,
                max(0, value - 1),
                value * 2,
                value // 2 if value > 1 else 1,
                value + 10,
                max(0, value - 10),
            ]
        else:
            return [
                value + 0.1,
                max(0, value - 0.1),
                value * 2,
                value / 2,
                value * 1.1,
                value * 0.9,
            ]
