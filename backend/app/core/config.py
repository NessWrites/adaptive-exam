from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os
import dotenv
from dotenv import load_dotenv

root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=root / ".env")


class Settings(BaseSettings):
    """Application settings"""
    
    DATABASE_URL: str=os.getenv('DATABASE_URL')
    DEBUG: bool = False
    
    # Exam configuration
    N_ADAPTIVE_QUESTIONS: int = 40
    
    




@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()