import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from server.database import engine, Base
    from server.models import DBUser
    from server.database import language_engine
except ImportError:
    from database import engine, Base
    from models import DBUser
    from database import language_engine

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=language_engine)
    print("Database tables created successfully!")
    print(f"Database location: {os.path.abspath('db/users.db')}")
    print(f"Language Database location: {os.path.abspath('db/languages.db')}")

if __name__ == "__main__":
    init_db()
