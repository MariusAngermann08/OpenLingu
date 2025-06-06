from sqlalchemy import create_engine, inspect
import os

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'users.db')

def check_db_schema():
    # Create SQLAlchemy engine
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    # Create an inspector
    inspector = inspect(engine)
    
    # Get list of tables
    print("\n=== Database Schema ===")
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    # Check each table's columns
    for table_name in tables:
        print(f"\nTable: {table_name}")
        print("Columns:")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']}: {column['type']}", 
                  f"(Primary Key: {column.get('primary_key', False)}, "
                  f"Nullable: {column.get('nullable', True)})")

if __name__ == "__main__":
    check_db_schema()
