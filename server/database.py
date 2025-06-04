from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
import os

# Get the absolute path to the database files
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
os.makedirs(DB_DIR, exist_ok=True)

# Database URLs
USERS_DB_PATH = os.path.join(DB_DIR, 'users.db')
LANGUAGES_DB_PATH = os.path.join(DB_DIR, 'languages.db')

USERS_DATABASE_URL = f"sqlite:///{os.path.abspath(USERS_DB_PATH)}"
LANGUAGES_DATABASE_URL = f"sqlite:///{os.path.abspath(LANGUAGES_DB_PATH)}"

# Create engines with different isolation levels to prevent table locking
users_engine = create_engine(
    USERS_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

languages_engine = create_engine(
    LANGUAGES_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

# Create session factories with autocommit=False for better transaction control
UsersSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=users_engine
)

LanguagesSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=languages_engine
)

# Create separate metadata for each database
users_metadata = MetaData()
languages_metadata = MetaData()

# Create base classes with separate metadata
UsersBase = declarative_base(metadata=users_metadata)
LanguagesBase = declarative_base(metadata=languages_metadata)

def get_users_db() -> Generator[Session, None, None]:
    """Dependency for getting users database session"""
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_language_db() -> Generator[Session, None, None]:
    """Dependency for getting languages database session"""
    db = LanguagesSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Backward compatibility
engine = users_engine
language_engine = languages_engine
SessionLocal = UsersSessionLocal
language_session = LanguagesSessionLocal
Base = UsersBase  # For backward compatibility