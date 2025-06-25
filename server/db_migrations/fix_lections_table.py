import os
import json
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, JSON, inspect
from sqlalchemy.orm import sessionmaker

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'languages.db')

# Create SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Check if lections_new exists
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'lections_new' in tables:
        print("Found lections_new table")
        
        # Get the current schema of lections_new
        columns = inspector.get_columns('lections_new')
        print("\nCurrent schema of lections_new:")
        for col in columns:
            print(f"- {col['name']}: {col['type']}")
        
        # Check if we need to rename it back to lections
        if 'lections' not in tables:
            print("\nRenaming lections_new to lections...")
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text('ALTER TABLE lections_new RENAME TO lections'))
                conn.commit()
            print("Table renamed successfully!")
        else:
            print("\nBoth lections and lections_new tables exist. Please check the database manually.")
    
    # Verify the final state
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nFinal tables in database:", tables)
    
    if 'lections' in tables:
        print("\nFinal schema of lections table:")
        columns = inspector.get_columns('lections')
        for col in columns:
            print(f"- {col['name']}: {col['type']}")
    
    print("\nDatabase fix completed!")

except Exception as e:
    print(f"Error: {str(e)}")
    db.rollback()
finally:
    db.close()
