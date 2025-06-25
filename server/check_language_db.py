from sqlalchemy import create_engine, text
import os

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'languages.db')

# Create SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Connect to the database and execute queries
with engine.connect() as connection:
    # List all tables
    print("Tables in the language database:")
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    for row in result:
        print(f"- {row[0]}")
    
    # If languages table exists, show its contents
    print("\nContents of 'languages' table:")
    try:
        result = connection.execute(text("SELECT * FROM languages;"))
        for row in result:
            print(row)
    except Exception as e:
        print(f"Error reading languages table: {e}")

    #If lections table exists, show its contents
    print("\nContents of 'lections' table:")
    try:
        result = connection.execute(text("SELECT * FROM lections;"))
        columns = result.keys()
        for row in result:
            row_dict = dict(zip(columns, row))
            print("- Lection:")
            for key, value in row_dict.items():
                if key == "content":
                    try:
                        # If value is a string, try to parse as JSON
                        if isinstance(value, str):
                            value = json.loads(value)
                        print(f"    {key}:\n" + json.dumps(value, indent=2, ensure_ascii=False))
                    except Exception as e:
                        print(f"    {key}: (Could not parse as JSON) {value}")
                else:
                    print(f"    {key}: {value}")
    except Exception as e:
        print(f"Error reading lections table: {e}")