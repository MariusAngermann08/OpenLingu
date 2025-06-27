#!/usr/bin/env python3
"""
OpenLingu Admin Tools

This module provides command-line tools for server administrators to manage contributor accounts.
These tools require direct server access to run.
"""

import sys
import getpass
from typing import Optional
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import our modules
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from server.database import users_engine
from server.models import DBContributor
from passlib.context import CryptContext

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_session() -> Session:
    """Create a new database session"""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=users_engine)
    return Session()

def create_contributor():
    """Create a new contributor account"""
    print("\n=== Create New Contributor ===")
    username = input("Username: ").strip()
    
    # Get password securely
    while True:
        password = getpass.getpass("Password: ").strip()
        if not password:
            print("Password cannot be empty. Please try again.")
            continue
            
        confirm = getpass.getpass("Confirm password: ").strip()
        if password == confirm:
            break
        print("Passwords do not match. Please try again.")
    
    db = get_session()
    try:
        # Check if contributor exists
        if db.query(DBContributor).filter(DBContributor.username == username).first():
            print(f"Error: Contributor '{username}' already exists")
            return False
        
        # Create new contributor
        hashed_password = pwd_context.hash(password)
        contributor = DBContributor(username=username, hashed_password=hashed_password)
        db.add(contributor)
        db.commit()
        print(f"\n✅ Successfully created contributor: {username}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating contributor: {str(e)}")
        return False
    finally:
        db.close()

def list_contributors() -> bool:
    """List all contributors"""
    print("\n=== List of Contributors ===")
    db = get_session()
    try:
        contributors = db.query(DBContributor).order_by(DBContributor.username).all()
        if not contributors:
            print("No contributors found")
            return True
            
        print(f"\n{'ID':<5} {'Username':<20}")
        print("-" * 30)
        for i, contributor in enumerate(contributors, 1):
            print(f"{i:<5} {contributor.username:<20}")
        return True
    except Exception as e:
        print(f"Error listing contributors: {str(e)}")
        return False
    finally:
        db.close()

def delete_contributor() -> bool:
    """Delete a contributor"""
    print("\n=== Delete Contributor ===")
    username = input("Enter username to delete: ").strip()
    
    if not username:
        print("Username cannot be empty")
        return False
    
    if input(f"\n⚠️  WARNING: Are you sure you want to delete contributor '{username}'? (y/N): ").lower() != 'y':
        print("Operation cancelled")
        return False
    
    db = get_session()
    try:
        contributor = db.query(DBContributor).filter(DBContributor.username == username).first()
        if not contributor:
            print(f"Error: Contributor '{username}' not found")
            return False
            
        db.delete(contributor)
        db.commit()
        print(f"\n✅ Successfully deleted contributor: {username}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error deleting contributor: {str(e)}")
        return False
    finally:
        db.close()

def show_menu():
    """Display the admin menu"""
    menu_options = {
        '1': ('Create new contributor', create_contributor),
        '2': ('List all contributors', list_contributors),
        '3': ('Delete contributor', delete_contributor),
        '4': ('Exit', None)
    }
    
    while True:
        print("\n" + "="*50)
        print("OpenLingu Admin Tools".center(50))
        print("="*50)
        
        for key, (description, _) in menu_options.items():
            print(f"{key}. {description}")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '4':
            print("\nExiting...")
            break
            
        if choice in menu_options:
            _, func = menu_options[choice]
            if func:
                func()
                input("\nPress Enter to continue...")
        else:
            print("\n❌ Invalid choice. Please try again.")

def main():
    """Main entry point for the admin tools"""
    print("="*50)
    print("OpenLingu Admin Tools".center(50))
    print("="*50)
    print("\nThis tool allows management of contributor accounts.")
    print("WARNING: This tool should only be used by server administrators.\n")
    
    if input("Are you sure you want to continue? (y/N): ").lower() != 'y':
        print("\nOperation cancelled")
        return
    
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        if input("\nShow detailed error? (y/N): ").lower() == 'y':
            import traceback
            traceback.print_exc()
    finally:
        print("\nThank you for using OpenLingu Admin Tools.")

if __name__ == "__main__":
    main()
