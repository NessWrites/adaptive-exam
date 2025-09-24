# backend/app/dependencies.py
from typing import Generator
from sqlalchemy.orm import Session
from .database.postgresql.connection import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()