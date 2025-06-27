#!/usr/bin/env python3
"""
Initialize the first admin user for OpenLingu.

This script should be run once to create the initial admin user.
"""

import sys
import getpass
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from passlib.context import CryptContext

# Import database configuration
try:
    from server.database import users_engine
    from server.models import DBUser
except ImportError:
    from database import users_engine
    from models import DBUser

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create the first admin user"""
    print("\n=== Create First Admin User ===\n")
    
    # Get admin credentials
    username = input("Enter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    
    while True:
        password = getpass.getpass("Enter admin password: ").strip()
        if not password:
            print("Password cannot be empty. Please try again.")
            continue
            
        confirm = getpass.getpass("Confirm admin password: ").strip()
        if password == confirm:
            break
        print("Passwords do not match. Please try again.")
    
    # Create database session
    Session = Session(bind=users_engine)
    db = Session()
    
    try:
        # Check if admin already exists
        existing_user = db.query(DBUser).filter(DBUser.username == username).first()
        if existing_user:
            print(f"\n❌ Error: User '{username}' already exists")
            return False
        
        # Create admin user
        hashed_password = pwd_context.hash(password)
        admin_user = DBUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True,
            disabled=False
        )
        
        db.add(admin_user)
        db.commit()
        print(f"\n✅ Successfully created admin user: {username}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("="*50)
    print("OpenLingu Admin Initialization".center(50))
    print("="*50)
    print("\nThis script will create the first admin user for OpenLingu.\n")
    
    if input("Do you want to continue? (y/N): ").lower() != 'y':
        print("\nOperation cancelled")
        sys.exit(0)
    
    if create_admin_user():
        print("\nAdmin user created successfully!")
        print("You can now use this account to log in to the admin interface.")
    else:
        print("\nFailed to create admin user.")
        sys.exit(1)
