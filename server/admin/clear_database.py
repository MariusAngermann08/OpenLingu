#!/usr/bin/env python3
"""
Database cleanup script for OpenLingu.

This script clears out the database files directly:
- server/db/users.db
- server/db/languages.db

WARNING: This will permanently delete all data from the databases!
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_cleanup.log')
    ]
)
logger = logging.getLogger(__name__)

def get_db_paths():
    """Get the paths to the database files."""
    # Get the absolute path to the server directory
    server_dir = Path(__file__).parent.parent
    db_dir = server_dir / 'db'
    
    users_db = db_dir / 'users.db'
    languages_db = db_dir / 'languages.db'
    
    return users_db, languages_db

def clear_database(db_path):
    """Clear all data from a SQLite database by recreating it with empty tables."""
    try:
        if not db_path.exists():
            logger.warning(f"Database file {db_path} does not exist. Skipping...")
            return False
            
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            logger.info(f"No tables found in {db_path}")
            return True
            
        # Disable foreign keys
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Drop all tables
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Don't drop the sequence table
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                logger.info(f"Dropped table: {table_name}")
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully cleared database: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error clearing database {db_path}: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def confirm_action() -> bool:
    """Ask for confirmation before proceeding with destructive actions."""
    print("\nWARNING: This will permanently delete all data from the databases!")
    response = input("Are you sure you want to continue? (yes/NO): ").strip().lower()
    return response in ('yes', 'y')

def main():
    """Main function to clear all database files."""
    try:
        print("=== OpenLingu Database Cleanup Tool ===")
        print("This will clear all data from the following database files:")
        
        users_db, languages_db = get_db_paths()
        
        print(f"\n1. {users_db}")
        print(f"2. {languages_db}")
        
        if not confirm_action():
            print("\nOperation cancelled.")
            return
            
        success = True
        
        # Clear users database
        print(f"\nClearing {users_db}...")
        if not clear_database(users_db):
            success = False
            
        # Clear languages database
        print(f"\nClearing {languages_db}...")
        if not clear_database(languages_db):
            success = False
            
        if success:
            print("\n✅ Database cleanup completed successfully!")
        else:
            print("\n⚠️  Database cleanup completed with some errors. Check the log file for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
