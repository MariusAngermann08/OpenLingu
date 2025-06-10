from sqlalchemy import create_engine, MetaData, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base, scoped_session
from typing import Generator, Optional, Any
import os
import time
import threading
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
import logging

# Set up logging with a more appropriate level for production
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and above by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the absolute path to the database files
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
os.makedirs(DB_DIR, exist_ok=True)

# Database URLs
USERS_DB_PATH = os.path.join(DB_DIR, 'users.db')
LANGUAGES_DB_PATH = os.path.join(DB_DIR, 'languages.db')

USERS_DATABASE_URL = f"sqlite:///{os.path.abspath(USERS_DB_PATH)}"
LANGUAGES_DATABASE_URL = f"sqlite:///{os.path.abspath(LANGUAGES_DB_PATH)}"

# Configure SQLite connection parameters
sqlite_connect_args = {
    "check_same_thread": False,
    "timeout": 30,  # 30 seconds timeout for database operations
    "isolation_level": "IMMEDIATE"  # Better concurrency control
}

def create_db_engine(db_url: str) -> Any:
    """Create a database engine with proper configuration."""
    try:
        engine = create_engine(
            db_url,
            connect_args=sqlite_connect_args,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30
        )
        
        # Configure SQLite PRAGMAs
        @event.listens_for(engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
            
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine for {db_url}", exc_info=True)
        raise

# Create database engines
users_engine = create_db_engine(USERS_DATABASE_URL)
languages_engine = create_db_engine(LANGUAGES_DATABASE_URL)

def test_connection(engine) -> bool:
    """Test database connection with a simple query."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        logger.debug(f"Database connection test failed: {e}")
        return False

# Create thread-local session factories with improved configuration
UsersSessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=users_engine,
        expire_on_commit=True
    ),
    scopefunc=threading.current_thread
)

LanguagesSessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=languages_engine,
        expire_on_commit=True
    ),
    scopefunc=threading.current_thread
)

# Context manager for database sessions
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions with automatic cleanup"""
    db = UsersSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
        UsersSessionLocal.remove()  # Clean up the scoped session

# Create separate metadata for each database
users_metadata = MetaData()
languages_metadata = MetaData()

# Create base classes with separate metadata
UsersBase = declarative_base(metadata=users_metadata)
LanguagesBase = declarative_base(metadata=languages_metadata)

def get_users_db() -> Generator[Session, None, None]:
    """Dependency for getting users database session"""
    from sqlalchemy import text
    db = UsersSessionLocal()
    try:
        # Set SQLite busy timeout to 30 seconds
        db.execute(text("PRAGMA busy_timeout = 30000"))  # 30 seconds
        db.commit()
        yield db
    except Exception as e:
        logger.debug(f"Error in get_users_db: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        # Clean up the scoped session
        UsersSessionLocal.remove()

def get_languages_db() -> Generator[Session, None, None]:
    """Dependency for getting languages database session"""
    from sqlalchemy import text
    db = LanguagesSessionLocal()
    try:
        # Set SQLite busy timeout to 30 seconds
        db.execute(text("PRAGMA busy_timeout = 30000"))  # 30 seconds
        db.commit()
        yield db
    except Exception as e:
        logger.debug(f"Error in get_languages_db: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        # Clean up the scoped session
        LanguagesSessionLocal.remove()

# Backward compatibility
engine = users_engine
language_engine = languages_engine
SessionLocal = UsersSessionLocal
language_session = LanguagesSessionLocal
Base = UsersBase  # For backward compatibility