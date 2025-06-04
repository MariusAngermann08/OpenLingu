from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Import from server modules
try:
    from server.database import get_users_db
    from server.models import DBUser, Token
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from server.services.token_service import generate_token, verify_token
except ImportError:
    # Fall back to direct imports when running directly
    from database import get_users_db
    from models import DBUser, Token
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from services.token_service import generate_token, verify_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_user(username: str, email: str, password: str, db: Session = None):
    close_db = False
    try:
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
            close_db = True
        
        # Check if user already exists by username or email
        existing_user = db.query(DBUser).filter(
            (DBUser.username == username) | (DBUser.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=400, detail="Username already registered")
            else:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = DBUser(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        
        # Add and commit the user
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Successfully created user: {username} with email: {email}")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Rollback in case of error
        if db:
            db.rollback()
        print(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )
        
    finally:
        # Ensure database connection is closed
        if db and close_db:
            db.close()

async def remove_user(username: str, token: str, db: Session = None):
    close_db = False
    try:
        # Get database session
        if db is None:
            db = next(get_users_db())
            close_db = True
        
        #Find user by username
        user = db.query(DBUser).filter(DBUser.username == username).first()

        if not user:
            print(f"User {username} not found")
            raise HTTPException(status_code=404, detail="User not found")

        #Delete user
        db.delete(user)
        db.commit()

        print(f"Successfully deleted user: {username}")
        return {"msg": "User deleted successfully"}

    except HTTPException as e:
        #Re-raise HTTP exceptions
        raise e
    
    except Exception as e:
        #Rollback in case of error
        if db:
            db.rollback()
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code = 500,
            detail = f"Error deleting user: {str(e)}"
        )
    
    finally:
        #Ensure database connection is closed
        if db and close_db:
            db.close()

async def authenticate_user(username: str, password: str, db: Session = None):
    close_db = False
    try:
        # Get database session
        if db is None:
            db = next(get_users_db())
            close_db = True
        
        # Find user by username (case-sensitive)
        user = db.query(DBUser).filter(DBUser.username == username).first()
        
        if not user:
            print(f"Login failed: User '{username}' not found")
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            print(f"Login failed: Incorrect password for user '{username}'")
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Generate token
        token = await generate_token(user)
        
        # Store the token in the database
        token_entry = Token(
            token=token,
            expires=datetime.utcnow() + timedelta(days=1)
        )
        
        db.add(token_entry)
        db.commit()
        
        print(f"User '{username}' successfully authenticated")
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Rollback in case of error
        if db:
            db.rollback()
        print(f"Error during authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )
        
    finally:
        # Ensure database connection is closed
        if db:
            db.close()
