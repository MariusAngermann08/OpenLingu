from sqlalchemy import create_engine, text
import os

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'users.db')

# Create SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Connect to the database and execute queries
with engine.connect() as connection:
    # List all tables
    print("Tables in the database:")
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    for row in result:
        print(f"- {row[0]}")
    
    # If users table exists, show its contents
    print("\nContents of 'users' table:")
    try:
        result = connection.execute(text("SELECT * FROM users;"))
        for row in result:
            print(row)
    except Exception as e:
        print(f"Error reading users table: {e}")
    
    # Show contents of tokens table if it exists
    print("\nContents of 'tokens' table:")
    try:
        result = connection.execute(text("SELECT * FROM tokens;"))
        for row in result:
            print(row)
    except Exception as e:
        print(f"Error reading tokens table: {e}")
