import asyncio
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.append(str(Path(__file__).parent))

from database import get_users_db
from models import DBUser
from services.token_service import generate_token

async def test_token_generation():
    print("Testing token generation...")
    
    # Get a database session
    db = next(get_users_db())
    
    try:
        # Get a test user (assuming there's at least one user in the database)
        user = db.query(DBUser).first()
        if not user:
            print("No users found in the database. Please create a user first.")
            return
            
        print(f"Testing with user: {user.username}")
        
        # Test token generation
        token = await generate_token(user)
        print(f"Token generated successfully: {token}")
        
    except Exception as e:
        print(f"Error during token generation test: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_token_generation())
