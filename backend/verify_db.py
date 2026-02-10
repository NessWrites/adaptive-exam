#!/usr/bin/env python3
"""
Database verification script before load testing
Checks: tables exist, schemas correct, indexes created
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ Import engine from connection.py
from backend.app.database.postgresql.connection import engine

from sqlalchemy import inspect, text

def check_database():
    print("\n" + "="*60)
    print("DATABASE VERIFICATION SCRIPT")
    print("="*60)
    
    inspector = inspect(engine)
    
    # 1. Check tables exist
    print("\n[1] Checking tables...")
    required_tables = ['exam_sessions', 'questions', 'responses']
    existing_tables = inspector.get_table_names()
    
    for table in required_tables:
        if table in existing_tables:
            print(f"  ✓ Table '{table}' exists")
        else:
            print(f"  ✗ Table '{table}' MISSING - CREATE TABLES FIRST")
            return False
    
    # 2. Check columns in responses table
    print("\n[2] Checking response table schema...")
    response_columns = {col['name'] for col in inspector.get_columns('responses')}
    required_columns = {
        'response_id', 
        'session_id', 
        'question_id', 
        'user_answer', 
        'is_correct', 
        'theta_math_after', 
        'theta_tech_after'
    }
    
    if required_columns.issubset(response_columns):
        print(f"  ✓ All columns present: {len(response_columns)} columns")
    else:
        missing = required_columns - response_columns
        print(f"  ✗ Missing columns: {missing}")
        return False
    
    # 3. Check indexes
    print("\n[3] Checking indexes...")
    indexes = inspector.get_indexes('responses')
    index_names = {idx['name'] for idx in indexes}
    
    required_indexes = {
        'ix_response_session_user_answer',
        'ix_response_session_question'
    }
    
    if required_indexes.issubset(index_names):
        print(f"  ✓ All required indexes present: {required_indexes}")
    else:
        missing_idx = required_indexes - index_names
        print(f"  ⚠ Missing indexes: {missing_idx}")
        print(f"     → Run migration to add: alembic upgrade head")
    
    print("\n  All indexes on 'responses' table:")
    if indexes:
        for idx in indexes:
            print(f"    - {idx['name']}: {idx['column_names']}")
    else:
        print(f"    (No indexes found)")
    
    # 4. Count existing data
    print("\n[4] Database counts...")
    try:
        with engine.connect() as conn:
            sessions = conn.execute(text("SELECT COUNT(*) FROM exam_sessions")).scalar()
            questions = conn.execute(text("SELECT COUNT(*) FROM questions")).scalar()
            responses = conn.execute(text("SELECT COUNT(*) FROM responses")).scalar()
            
            print(f"  - exam_sessions: {sessions}")
            print(f"  - questions: {questions}")
            print(f"  - responses: {responses}")
    except Exception as e:
        print(f"  ✗ Error reading counts: {e}")
    
    # 5. Check connection pool settings
    print("\n[5] Connection pool configuration...")
    try:
        print(f"  - Pool size: {engine.pool.size()}")
        print(f"  - Max overflow: {engine.pool._overflow}")
        print(f"  - Pool timeout: {engine.pool.timeout()}")
        print(f"  - Pre-ping enabled: {engine.pool._pre_ping}")
        print(f"  - Pool recycle: {engine.pool._recycle}")
    except AttributeError as e:
        print(f"  ⚠ Could not read all pool settings: {e}")
    
    print("\n" + "="*60)
    print("✓ DATABASE READY FOR LOAD TESTING")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)