from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://root:root@db:5432/healthmate_ai_db") 

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables defined in models.py
def create_db_tables():

    from . import models

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # For production, you might want a more sophisticated logging system
        # For now, we'll keep a basic print for errors, but expect success.
        print(f"ERROR: Failed to create database tables during startup: {e}")