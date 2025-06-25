import os
import sys
import json
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, String, Text, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

# Import database configuration
try:
    from server.database import LANGUAGES_DATABASE_URL, USERS_DATABASE_URL, create_db_engine
    from server.models import Lection
    from server.init_db import wait_for_db
except ImportError:
    from database import LANGUAGES_DATABASE_URL, USERS_DATABASE_URL, create_db_engine
    from models import Lection
    from init_db import wait_for_db

def update_lections_table():
    """Update the lections table to use JSON type for content field."""
    print("Starting database update...")
    
    # Create engines
    engine = create_db_engine(LANGUAGES_DATABASE_URL)
    
    # Wait for database to be available
    if not wait_for_db(engine):
        print("Error: Could not connect to the database")
        return False
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create a temporary table with the new schema
        metadata = MetaData()
        
        # Reflect the existing table
        metadata.reflect(bind=engine)
        
        # Check if the lections table exists
        if 'lections' not in metadata.tables:
            print("Error: 'lections' table does not exist")
            return False
            
        # Get the existing table
        old_lections = Table('lections', metadata, autoload_with=engine)
        
        # Create a new table with the updated schema
        new_lections = Table(
            'lections_new',
            metadata,
            Column('id', String, primary_key=True, index=True),
            Column('title', String),
            Column('description', String),
            Column('language', String),
            Column('difficulty', String),
            Column('created_at', String),  # Will be converted to DateTime in the model
            Column('created_by', String, index=True),
            Column('content', JSON),  # Changed from String to JSON
            extend_existing=True
        )
        
        # Create the new table
        new_lections.create(engine)
        print("Created new lections table with updated schema")
        
        # Copy data from old table to new table
        print("Migrating data...")
        
        # Get all records from the old table
        result = db.execute(old_lections.select())
        records = result.fetchall()
        
        # Insert records into the new table
        for record in records:
            try:
                # Convert content to JSON if it's a string
                content = record.content
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep it as is
                        pass
                
                # Insert into new table
                insert_stmt = new_lections.insert().values(
                    id=record.id,
                    title=record.title,
                    description=record.description,
                    language=record.language,
                    difficulty=record.difficulty,
                    created_at=record.created_at,
                    created_by=record.created_by,
                    content=content
                )
                db.execute(insert_stmt)
                
            except Exception as e:
                print(f"Error migrating record {record.id}: {str(e)}")
                db.rollback()
                continue
        
        # Commit the transaction
        db.commit()
        
        # In SQLite, we need to use ALTER TABLE to rename
        # First drop the old table
        old_lections.drop(engine)
        
        # Then rename the new table to the original name
        with engine.connect() as conn:
            conn.execute('ALTER TABLE lections_new RENAME TO lections')
        
        print("Database update completed successfully!")
        return True
        
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        db.rollback()
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database migration...")
    if update_lections_table():
        print("Migration completed successfully!")
    else:
        print("Migration failed. Please check the error messages above.")
        sys.exit(1)
