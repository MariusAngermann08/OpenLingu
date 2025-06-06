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
    
    if 'server.models' in sys.modules:
        importlib.reload(sys.modules['server.models'])
    elif 'models' in sys.modules:
        importlib.reload(sys.modules['models'])
    
    # Drop all existing tables to ensure clean slate
    with users_engine.begin() as conn:
        users_metadata.drop_all(bind=conn)
    with languages_engine.begin() as conn:
        languages_metadata.drop_all(bind=conn)
    
    # Create users database tables with correct schema
    users_metadata.create_all(bind=users_engine)
    
    # Create languages database tables
    languages_metadata.create_all(bind=languages_engine)
    
    # Verify the schema was created correctly
    from sqlalchemy import inspect
    
    inspector = inspect(users_engine)
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    
    print("\nDatabase tables created successfully!")
    print(f"Users database location: {os.path.abspath('db/users.db')}")
    print(f"Tables in users database: {list(users_metadata.tables.keys())}")
    print(f"Users table columns: {', '.join(users_columns)}")
    print(f"\nLanguages database location: {os.path.abspath('db/languages.db')}")
    print(f"Tables in languages database: {list(languages_metadata.tables.keys())}")
    
    if set(users_columns) != {'username', 'email', 'hashed_password', 'disabled'}:
        print("\nWARNING: Users table schema does not match expected schema!")

if __name__ == "__main__":
    init_db()
