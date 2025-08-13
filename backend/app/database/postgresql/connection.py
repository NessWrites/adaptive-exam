# PostgreSQL Connection 
from sqlalchemy import create_engine
import os

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://user:password@localhost/dbname")
engine = create_engine(POSTGRES_URI)

print(" PostgreSQL connection initialized")
