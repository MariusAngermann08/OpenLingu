import sqlite3
import os
from pathlib import Path

def update_lections_table():
    # Path to your SQLite database
    db_path = os.path.join('db', 'languages.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    print(f"Updating schema in database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQLite doesn't support direct ALTER COLUMN, so we need to:
        # 1. Rename the old table
        # 2. Create a new table with the correct schema
        # 3. Copy data from old to new
        # 4. Drop the old table
        # 5. Rename new table to original name
        
        print("1. Renaming existing lections table...")
        cursor.execute('ALTER TABLE lections RENAME TO lections_old;')
        
        print("2. Creating new lections table with updated schema...")
        cursor.execute('''
        CREATE TABLE lections (
            id VARCHAR NOT NULL, 
            title VARCHAR, 
            description VARCHAR, 
            language VARCHAR, 
            difficulty VARCHAR, 
            created_at DATETIME, 
            created_by VARCHAR, 
            content TEXT, 
            PRIMARY KEY (id)
        )
        ''')
        
        print("3. Copying data from old table to new table...")
        cursor.execute('''
        INSERT INTO lections (id, title, description, language, difficulty, created_at, created_by, content)
        SELECT id, title, description, language, difficulty, created_at, created_by, content 
        FROM lections_old
        ''')
        
        print("4. Dropping old table...")
        cursor.execute('DROP TABLE lections_old;')
        
        # Commit changes
        conn.commit()
        print("Database schema updated successfully!")
        
    except Exception as e:
        print(f"Error updating database schema: {e}")
        if conn:
            conn.rollback()
            print("Changes have been rolled back due to an error.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_lections_table()
