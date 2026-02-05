# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from backend.app.core.config import get_settings
# settings = get_settings()

# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,
#     echo=settings.DEBUG
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     """Database session dependency"""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import get_settings
import threading

settings = get_settings()

# CRITICAL: Add proper connection pool settings for high concurrency
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=100,                    # Increased from default 5
    max_overflow=50,                 # Increased from default 10
    pool_timeout=10,                 # Timeout for getting connection
    pool_pre_ping=True,              # Verify connection before using
    pool_recycle=1800,               # Recycle connections every 30 minutes
    pool_use_lifo=True,              # Use LIFO for better performance
    echo=settings.DEBUG              # Keep debug mode as configured
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Thread-local storage for sessions (alternative approach)
# This ensures each thread gets its own session
_sessions = threading.local()

def get_db():
    """
    Database session dependency.
    Creates a new session for each request and ensures it's closed.
    
    NOTE: This should be called fresh for every request - do NOT reuse sessions!
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up any lingering connections
        engine.dispose()