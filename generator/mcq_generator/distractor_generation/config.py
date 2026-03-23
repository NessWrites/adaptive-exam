# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq API Key (get from: https://console.groq.com/keys)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Groq Model (options: mixtral-8x7b-32768, llama2-70b-4096, gemma-7b-it)
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # LLM Settings
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    USE_LLM = bool(GROQ_API_KEY)  # Only use LLM if Groq key is available
    
    # Agent settings
    ENABLE_MISCONCEPTION_AGENT = True
    # ENABLE_LOGIC_AGENT = True
    ENABLE_NUMERIC_AGENT = True
    ENABLE_SIMILARITY_AGENT = True
    AGENT_TYPE='hybrid' 
    USE_DATABASE= True 
    
    # Distractor settings
    MAX_DISTRACTORS_PER_QUESTION =4
    MIN_SIMILARITY = 0.1
    MAX_SIMILARITY = 0.85
    
    # File paths
    MISCONCEPTIONS_DB_PATH = "distractor_db.json"
    
    # For backward compatibility
    LLM_MODEL = GROQ_MODEL  # Alias for compatibility
    # OPENAI_API_KEY = ""  # Empty since we're not using OpenAI
    
    QUESTIONS_PATH = "ques.json"
    OUTPUT_PATH = "ques_with_distractors.json"
    validate=lambda self: None  # Placeholder for validate method
    MAX_TOKENS: int = 1000  









# # config.py
# import os
# from dataclasses import dataclass
# from typing import Optional, List

# @dataclass
# class Config:
#     """Configuration for distractor generation."""
#     # LLM Settings
#     USE_LLM: bool = True
#     GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
#     GROQ_MODEL: str = "llama-3.3-70b-versatile"
#     LLM_TEMPERATURE: float = 0.7
#     MAX_TOKENS: int = 500
    
#     # Agent Settings
#     AGENT_TYPE: str = "hybrid"  # "numeric", "llm", or "hybrid"
#     MAX_DISTRACTORS_PER_QUESTION: int = 4
#     MIN_SIMILARITY: float = 0.15
#     MAX_SIMILARITY: float = 0.85
    
#     # Database Settings
#     MISCONCEPTIONS_DB_PATH: str = "data/misconceptions_db.json"
#     USE_DATABASE: bool = True
    
#     # File Paths
#     QUESTIONS_PATH: str = "questions.json"
#     OUTPUT_PATH: str = "questions_with_distractors.json"
    
#     def validate(self):
#         """Validate configuration."""
#         if self.USE_LLM and not self.GROQ_API_KEY:
#             print("⚠️  GROQ_API_KEY not found. LLM will be disabled.")
#             self.USE_LLM = False
        
#         if self.AGENT_TYPE not in ["numeric", "llm", "hybrid"]:
#             print(f"⚠️  Invalid AGENT_TYPE: {self.AGENT_TYPE}. Defaulting to 'hybrid'")
#             self.AGENT_TYPE = "hybrid"