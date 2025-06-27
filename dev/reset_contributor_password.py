#!/usr/bin/env python3
"""
Reset a contributor's password in the database.
This script should only be used for development and testing purposes.
"""

import sys
import os
from contextlib import contextmanager

# Add the server directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_users_db, UsersSessionLocal
from server.models import DBContributor
from passlib.context import CryptContext

@contextmanager
def get_db_session():
    """Get a database session with proper cleanup."""
    db = UsersSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        UsersSessionLocal.remove()

def main():
    if len(sys.argv) != 3:
        print("Usage: python reset_contributor_password.py <username> <new_password>")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    # Initialize password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        with get_db_session() as db:
            # Find the contributor
            contributor = db.query(DBContributor).filter(DBContributor.username == username).first()
            if not contributor:
                print(f"Error: Contributor '{username}' not found")
                sys.exit(1)
            
            # Update the password
            hashed_password = pwd_context.hash(new_password)
            print(f"Updating password hash for {username} to: {hashed_password}")
            contributor.hashed_password = hashed_password
            
            # Commit the changes
            db.commit()
            print(f"Successfully updated password for contributor: {username}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
