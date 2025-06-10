import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Type, TypeVar, Any
from sqlalchemy import inspect, event, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging with a more appropriate level for production
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and above by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # This specific logger will show INFO and above

try:
    from server.database import (
        users_engine, languages_engine, 
        UsersBase, LanguagesBase, 
        users_metadata, languages_metadata,
        test_connection
    )
    from server.models import DBUser, Token, Language
except ImportError:
    from database import (
        users_engine, languages_engine, 
        UsersBase, LanguagesBase, 
        users_metadata, languages_metadata,
        test_connection
    )
    from models import DBUser, Token, Language

def wait_for_db(engine, max_retries: int = 5, retry_delay: int = 1) -> bool:
    """Wait for the database to be available.
    
    Args:
        engine: SQLAlchemy engine to test
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            if test_connection(engine):
                logger.debug("Database connection successful")
                return True
        except Exception as e:
            logger.debug(f"Database connection attempt {attempt}/{max_retries} failed")
            
        if attempt < max_retries:
            logger.debug(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    logger.error(f"Failed to connect to database after {max_retries} attempts")
    return False

def init_db() -> None:
    """Initialize the database with required tables."""
    logger.info("Initializing database...")
    
    # Wait for databases to be ready
    logger.info("Waiting for users database to be ready...")
    if not wait_for_db(users_engine):
        raise RuntimeError("Failed to connect to users database")
    
    logger.debug("Users database is ready")
    
    logger.info("Waiting for languages database to be ready...")
    if not wait_for_db(languages_engine):
        raise RuntimeError("Failed to connect to languages database")
    
    logger.debug("Languages database is ready")
    
    # Clear existing metadata to prevent table creation in wrong databases
    users_metadata.clear()
    languages_metadata.clear()
    
    # Re-import models to ensure they're bound to the correct metadata
    try:
        import importlib
        if 'server.models' in sys.modules:
            importlib.reload(sys.modules['server.models'])
        elif 'models' in sys.modules:
            importlib.reload(sys.modules['models'])
    except Exception as e:
        logger.warning(f"Failed to reload models: {e}")
    
    # Create tables with error handling
    try:
        logger.debug("Checking if database tables exist...")
        
        # Create users tables if they don't exist
        inspector = inspect(users_engine)
        if not inspector.has_table('users'):
            logger.info("Creating users table (first run)...")
            users_metadata.create_all(bind=users_engine)
            logger.debug("Created users table")
        
        # Create languages tables if they don't exist
        if not inspector.has_table('languages'):
            logger.info("Creating languages table (first run)...")
            languages_metadata.create_all(bind=languages_engine)
            logger.debug("Created languages table")
            
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise
    
    # Verify the schema
    try:
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        print("\nDatabase initialization complete!")
        print(f"Users database location: {os.path.abspath('db/users.db')}")
        print(f"Tables in users database: {list(users_metadata.tables.keys())}")
        print(f"Users table columns: {', '.join(users_columns)}")
        print(f"\nLanguages database location: {os.path.abspath('db/languages.db')}")
        print(f"Tables in languages database: {list(languages_metadata.tables.keys())}")
        
        if set(users_columns) != {'username', 'email', 'hashed_password', 'disabled'}:
            print("\nWARNING: Users table schema does not match expected schema!")
    except Exception as e:
        print(f"\nWarning: Could not verify database schema: {str(e)}")

if __name__ == "__main__":
    init_db()
