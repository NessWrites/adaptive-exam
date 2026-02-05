# tests/conftest.py
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database.postgresql.connection import Base, get_db
from backend.app.services.qpool_services import QPoolService

# 1. SETUP TEST DATABASE (In-Memory SQLite for logic, or use a separate Postgres DB)
# Note: SQLite doesn't support ARRAY types well. For this specific project 
# (using Postgres ARRAY), it is better to mock the Session or use a real local Postgres test DB.
# For simplicity here, I will demonstrate mocking the DB Session in the individual tests 
# to avoid complex Docker setup instructions.

@pytest.fixture
def mock_qpool(mocker):
    """
    Intersects any call to QPoolService and returns a fake question.
    This prevents hitting your Free Tier LLM API during tests.
    """
    mock_service = MagicMock(spec=QPoolService)
    
    # Mock the paraphrase_question_sync method
    mock_service.paraphrase_question_sync.return_value = {
        'variants': [{
            'variant_stem': "This is a MOCKED paraphrased question.",
            'answer': "A",
            'distractors': ["Wrong 1", "Wrong 2", "Wrong 3"]
        }]
    }
    
    # Patch the class in exam_service.py so when it calls QPoolService(), it gets our mock
    mocker.patch("backend.app.services.exam_service.QPoolService", return_value=mock_service)
    return mock_service

@pytest.fixture
def client():
    """FastAPI Test Client"""
    return TestClient(app)