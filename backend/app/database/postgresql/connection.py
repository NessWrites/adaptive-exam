from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# Set up logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
# Database URL (adjust password if needed)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatabaseManager:
    def __init__(self, connection_params: dict[str,str]):
        """_summary_

		Args:
			connection_params (dict[str,str]): host, database, user, password, port
		"""
        self.connection_params = connection_params
        self.conn = None
        
    def connect(self):
        """Establish Database Connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    def close(self):
        """Close database connection """
        if self.conn:
            self.conn.close()
            logger.info("Database connection is closed")
            

            