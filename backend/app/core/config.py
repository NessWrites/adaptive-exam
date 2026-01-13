from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os 
root = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=root/ ".env")


class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "MIRT CAT Exam API"
    API_VERSION: str = "1.0.0"
    API_DEBUG: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Exam Settings
    DEFAULT_ITEM_BANK_PATH: str = os.getenv('BASE_ITEM_PATH')
    DEFAULT_MIN_ITEMS: int = 10
    DEFAULT_MAX_ITEMS: int = 40
    DEFAULT_TARGET_SE: float = 0.30


settings = Settings()