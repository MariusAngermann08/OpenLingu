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
    
    # Create users database tables
    users_metadata.create_all(bind=users_engine)
    
    # Create languages database tables
    languages_metadata.create_all(bind=languages_engine)
    
    print("Database tables created successfully!")
    print(f"Users database location: {os.path.abspath('db/users.db')}")
    print(f"Tables in users database: {list(users_metadata.tables.keys())}")
    print(f"Languages database location: {os.path.abspath('db/languages.db')}")
    print(f"Tables in languages database: {list(languages_metadata.tables.keys())}")

if __name__ == "__main__":
    init_db()
