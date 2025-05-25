from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# Import lib for pwd hasing
from passlib.context import CryptContext

#Get db
try:
    # Try absolute imports first (when running as a module)
    from server.parameters import *
    from server.database import *
    from server.models import DBUser, Token
except ImportError:
    # Fall back to relative imports (when running directly)
    from parameters import *
    from database import *
    from models import DBUser, Token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_user(username: str, email: str, password: str):
    db = None
    try:
        # Get database session
        db = next(get_db())
        
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
        if db:
            db.close()

async def remove_user(username: str):
    db = None
    try:
        # Get database session
        db = next(get_db())

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
        if db:
            db.close()

async def authenticate_user(username: str, password: str):
    db = None
    try:
        # Get database session
        db = next(get_db())
        
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

async def generate_token(user: DBUser):
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def verify_token(token: str) -> str:
    """
    Verify the JWT token and return the username if valid.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        str: The username from the token
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No authentication token provided",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            print("Token is missing 'sub' claim")
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Check if token is in the database (optional, for token invalidation)
        db = next(get_db())
        try:
            token_exists = db.query(Token).filter(Token.token == token).first()
            if not token_exists:
                print(f"Token not found in database: {token}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        finally:
            db.close()
            
        return username
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTError as e:
        print(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during token verification"
        )



async def remove_expired_tokens():
    db = next(get_db())
    db.query(Token).filter(Token.expires < datetime.utcnow()).delete()
    db.commit()
    db.close()