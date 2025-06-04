import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Define database paths
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
USERS_DB_PATH = os.path.join(DB_DIR, 'users.db')
LANGUAGES_DB_PATH = os.path.join(DB_DIR, 'languages.db')

def delete_database_files():
    """Delete existing database files if they exist"""
    for db_path in [USERS_DB_PATH, LANGUAGES_DB_PATH]:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Deleted: {db_path}")
            except Exception as e:
                print(f"Error deleting {db_path}: {e}")
        else:
            print(f"Database file does not exist: {db_path}")

def initialize_databases():
    """Initialize the databases with correct schemas"""
    try:
        from init_db import init_db
        init_db()
        print("\nDatabases initialized successfully!")
    except Exception as e:
        print(f"Error initializing databases: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Resetting databases...")
    print("-" * 50)
    
    # Delete existing database files
    print("Deleting existing database files...")
    delete_database_files()
    
    # Create the db directory if it doesn't exist
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Initialize new databases
    print("\nInitializing new databases...")
    initialize_databases()
    
    print("\nDatabase reset complete!")
