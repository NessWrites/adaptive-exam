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


# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from backend.app.core.config import get_settings
# import threading

# settings = get_settings()

# # CRITICAL: Add proper connection pool settings for high concurrency
# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_size=100,                    # Increased from default 5
#     max_overflow=50,                 # Increased from default 10
#     pool_timeout=10,                 # Timeout for getting connection
#     pool_pre_ping=True,              # Verify connection before using
#     pool_recycle=1800,               # Recycle connections every 30 minutes
#     pool_use_lifo=True,              # Use LIFO for better performance
#     echo=settings.DEBUG              # Keep debug mode as configured
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# # Thread-local storage for sessions (alternative approach)
# # This ensures each thread gets its own session
# _sessions = threading.local()

# def get_db():
#     """
#     Database session dependency.
#     Creates a new session for each request and ensures it's closed.
    
#     NOTE: This should be called fresh for every request - do NOT reuse sessions!
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#         # Clean up any lingering connections
#         engine.dispose() 


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import get_settings

settings = get_settings()

# Connection pool settings optimized for local testing
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,                    # Good for local testing (up to 20 concurrent)
    max_overflow=10,                 # Allow 10 extra connections if needed
    pool_timeout=30,                 # Wait up to 30s for connection
    pool_pre_ping=True,              # Verify connections are alive
    pool_recycle=3600,               # Recycle connections every hour
    echo=settings.DEBUG              # Log SQL if DEBUG=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Database session dependency.
    
    CRITICAL: Creates a new session per request and properly closes it.
    
    DO NOT call engine.dispose() here - it destroys the connection pool!
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # ✅ Just close the session, NOT the engine!
        # The connection returns to the pool for reuse