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
except ImportError:
    # Fall back to direct imports when running directly
    from database import get_users_db
    from models import DBUser, Token
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Lazy import to avoid circular imports
def _get_token_service():
    try:
        from server.services.token_service import generate_token, verify_token
    except ImportError:
        from services.token_service import generate_token, verify_token
    return generate_token, verify_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_user(username: str, email: str, password: str, db: Session = None):
    close_db = False
    try:
        print(f"[DEBUG] create_user called with username={username}, email={email}")
        
        # Get database session if not provided
        if db is None:
            print("[DEBUG] Creating new database session")
            db = next(get_users_db())
            close_db = True
        
        # Check if user already exists by username or email
        print("[DEBUG] Checking for existing user")
        existing_user = db.query(DBUser).filter(
            (DBUser.username == username) | (DBUser.email == email)
        ).first()
        
        if existing_user:
            print(f"[DEBUG] User already exists: {existing_user.username if existing_user.username == username else existing_user.email}")
            if existing_user.username == username:
                raise HTTPException(status_code=400, detail="Username already registered")
            else:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user with explicit column names
        print("[DEBUG] Hashing password")
        hashed_password = get_password_hash(password)
        print(f"[DEBUG] Creating user object with hashed_password: {hashed_password}")
        
        user = DBUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            disabled=False
        )
        
        print(f"[DEBUG] User object created: {user.__dict__}")
        
        # Add and commit the user
        print("[DEBUG] Adding user to session")
        db.add(user)
        print("[DEBUG] Committing transaction")
        db.commit()
        print("[DEBUG] Refreshing user")
        db.refresh(user)
        
        # Verify the user was saved correctly
        print("[DEBUG] Verifying user in database")
        saved_user = db.query(DBUser).filter(DBUser.username == username).first()
        print(f"[DEBUG] User in database: {saved_user.__dict__ if saved_user else 'Not found'}")
        
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

async def authenticate_user(username: str, password: str, db: Session, generate_token: bool = False):
    """
    Authenticate a user and optionally generate an access token
    
    Args:
        username: The username to authenticate
        password: The plain text password
        db: Database session (required)
        generate_token: Whether to generate and return an access token
        
    Returns:
        dict: If generate_token is True, returns dict with access_token and token_type
        DBUser: If generate_token is False, returns the user object
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        if not db:
            raise ValueError("Database session is required")
            
        print(f"[AUTH] Authenticating user: {username}")
        
        # Get user from database
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            print(f"[AUTH] User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Verify password
        if not verify_password(password, user.hashed_password):
            print(f"[AUTH] Invalid password for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        print(f"[AUTH] User '{username}' successfully authenticated")
        
        if not generate_token:
            return user
            
        # Generate token
        print("[AUTH] Generating token...")
        generate_token_func, _ = _get_token_service()
        token = await generate_token_func(user, db=db)
        print(f"[AUTH] Token generated successfully for user: {username}")
        
        # Get the expiration time from the token
        from jose import jwt
        try:
            # Decode the token to get the expiration time
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            expires = datetime.utcfromtimestamp(payload['exp'])
            print(f"[AUTH] Token expires at: {expires}")
            
            # Create and save token entry
            token_entry = Token(
                token=token,
                expires=expires
            )
            
            db.add(token_entry)
            db.commit()
            print("[AUTH] Token saved to database")
            
            return {"access_token": token, "token_type": "bearer"}
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to create token entry: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create authentication token"
            )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
        
    except Exception as e:
        # Log the error and return a 500 error
        error_msg = f"Authentication error: {str(e)}"
        print(f"[AUTH] {error_msg}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again."
        )
