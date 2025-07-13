from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from models import Base
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://statify_user:statify_password@statify_postgres:5432/statify")

# Handle Heroku postgres URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_recycle=300
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For testing
def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()