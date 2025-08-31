import logging
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv
import sys
import os
# Load environment variables from .env
load_dotenv()

# Access the variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


#Setup the project root path
ROOT_DIR =  Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.database.postgresql.connection import DatabaseManager, DATABASE_URL


# Set up logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

#Database URL fro SQLAlchemy
database_url = DATABASE_URL

#create engine

engine = create_engine(database_url)


# Connection parameters for DatabaseManager
connection_params = {
    "host": DB_HOST,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT
}

def test_database_connection():
    # Test DatabaseManager (psycopg2)
    db_manager = DatabaseManager(connection_params)
    
    try:
        # Test connection
        db_manager.connect()
        cursor = db_manager.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()
        logger.info(f"Query result: {result['test']}")
        cursor.close()
        
        # Test closure
        db_manager.close()
        
        # Verify connection is closed by attempting another query
        try:
            cursor = db_manager.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT 1 AS test")
            logger.error("Connection was not properly closed, query succeeded")
        except psycopg2.Error:
            logger.info("Connection properly closed, query failed as expected")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    
    # Test SQLAlchemy engine
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1 AS test").fetchone()
            logger.info(f"SQLAlchemy query result: {result[0]}")
    except Exception as e:
        logger.error(f"SQLAlchemy connection failed: {e}")

if __name__ == "__main__":
    test_database_connection()