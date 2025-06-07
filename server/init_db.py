import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from server.database import users_engine, languages_engine, UsersBase, LanguagesBase, users_metadata, languages_metadata
    from server.models import DBUser, Token, Language
except ImportError:
    from database import users_engine, languages_engine, UsersBase, LanguagesBase, users_metadata, languages_metadata
    from models import DBUser, Token, Language

def init_db():
    # Clear existing metadata to prevent table creation in wrong databases
    users_metadata.clear()
    languages_metadata.clear()
    
    # Re-import models to ensure they're bound to the correct metadata
    import importlib
    import sys
    from sqlalchemy import inspect
    
    if 'server.models' in sys.modules:
        importlib.reload(sys.modules['server.models'])
    elif 'models' in sys.modules:
        importlib.reload(sys.modules['models'])
    
    # Create tables only if they don't exist
    inspector = inspect(users_engine)
    
    # Check and create users tables if they don't exist
    if not inspector.has_table('users'):
        users_metadata.create_all(bind=users_engine)
        print("Created users table")
    
    # Check and create languages tables if they don't exist
    if not inspector.has_table('languages'):
        languages_metadata.create_all(bind=languages_engine)
        print("Created languages table")
    
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
