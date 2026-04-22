"""
DistractorConfigAdapter

Bridges the gap between the main app's Pydantic BaseSettings and the
distractor app's plain Config class.

DistractorManager only reads these attributes from Config:
  - USE_LLM, GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, MAX_TOKENS
  - AGENT_TYPE, MAX_DISTRACTORS_PER_QUESTION
  - USE_DATABASE, MISCONCEPTIONS_DB_PATH

This adapter exposes exactly those attributes without polluting Settings.
"""

import os
from pathlib import Path
from functools import lru_cache


# Absolute path to distractor_db.json — resolved relative to THIS file's location.
# Adjust the number of .parents[N] to match your actual repo layout.

_MCQ_GENERATOR_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_DB_PATH = str(
    _MCQ_GENERATOR_DIR / "distractor_generation" / "distractor_db.json"
)


class DistractorConfigAdapter:
    """
    A plain-class Config interface for the DistractorManager.
    Reads from environment variables with sensible defaults.
    Does NOT inherit from Pydantic BaseSettings (by design).
    """

    # LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("DISTRACTOR_MAX_TOKENS", "1000"))
    USE_LLM: bool = bool(GROQ_API_KEY)

    # Agent settings
    AGENT_TYPE: str = os.getenv("DISTRACTOR_AGENT_TYPE", "hybrid")
    MAX_DISTRACTORS_PER_QUESTION: int = int(
        os.getenv("MAX_DISTRACTORS_PER_QUESTION", "4")
    )

    # Database settings
    USE_DATABASE: bool = os.getenv("DISTRACTOR_USE_DATABASE", "true").lower() == "true"
    MISCONCEPTIONS_DB_PATH: str = os.getenv(
        "MISCONCEPTIONS_DB_PATH", _DEFAULT_DB_PATH
    )

    # Alias for compatibility with distractor app
    LLM_MODEL: str = GROQ_MODEL

    def validate(self) -> None:
        """Mirrors the validate() method on the original Config."""
        if self.USE_LLM and not self.GROQ_API_KEY:
            print("⚠️  GROQ_API_KEY not set. LLM distractor generation disabled.")
            self.USE_LLM = False
        if self.AGENT_TYPE not in ("numeric", "llm", "hybrid"):
            self.AGENT_TYPE = "hybrid"


@lru_cache(maxsize=1)
def get_distractor_config() -> DistractorConfigAdapter:
    """
    Singleton factory — mirrors the pattern of get_settings() in your main config.
    Safe to call multiple times; only one instance is created.
    """
    cfg = DistractorConfigAdapter()
    cfg.validate()
    return cfg