from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

# Import from server modules
try:
    from server.database import get_users_db
    from server.models import DBUser, Token, DBContributor
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fall back to direct imports when running directly
    from database import get_users_db
    from models import DBUser, Token, DBContributor
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
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"[DEBUG] Password verification result: {result}")
    return result

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
        
        # Generate token and let the generate_token function handle saving to DB
        token = await generate_token_func(user, db=db, save_to_db=True)
        print(f"[AUTH] Token generated and saved successfully for user: {username}")
        
        # Get the expiration time from the token
        from jose import jwt
        try:
            # Decode the token to get the expiration time
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            expires = datetime.utcfromtimestamp(payload['exp'])
            print(f"[AUTH] Token expires at: {expires}")
            
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

async def create_contributer(username: str, password: str, db: Session):
    """
    Create a new contributor
    
    Args:
        username: The username for the new contributor
        password: The password for the new contributor
        db: Database session
        
    Returns:
        dict: Success message
    """

    #Check if contributer already exists
    existing_contributer = db.query(DBContributor).filter(DBContributor.username == username).first()
    if existing_contributer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contributer already registered"
        )
    
    #Create new contributor
    try:
        contributor = DBContributor(username=username, hashed_password=get_password_hash(password))
        db.add(contributor)
        db.commit()
        db.refresh(contributor)
        
        print(f"Successfully created contributor: {username}")
        return {"msg": "Contributor created successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error creating contributor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contributor: {str(e)}"
        )

async def authenticate_contributer(username: str, password: str, db: Session, generate_token: bool = False):
    """
    Authenticate a contributor and optionally generate an access token
    
    Args:
        username: The username to authenticate
        password: The plain text password
        db: Database session
        generate_token: Whether to generate and return an access token
        
    Returns:
        dict: If generate_token is True, returns dict with access_token and token_type
        DBContributor: If generate_token is False, returns the contributor object
        
    Raises:
        HTTPException: If authentication fails
    """
    print(f"[DEBUG] authenticate_contributer called with username: {username}")
    
    # Check if contributor exists
    contributor = db.query(DBContributor).filter(DBContributor.username == username).first()
    print(f"[DEBUG] Found contributor in DB: {contributor is not None}")
    
    if not contributor:
        print(f"[DEBUG] Contributor '{username}' not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print(f"[DEBUG] Contributor found. Username: {contributor.username}, Hashed password: {contributor.hashed_password}")
    
    # Verify password
    print("[DEBUG] Starting password verification")
    if not verify_password(password, contributor.hashed_password):
        print("[DEBUG] Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    print("[DEBUG] Password verification successful")
    
    # Set is_contributor flag before generating token
    setattr(contributor, 'is_contributor', True)
    
    # Generate token
    if generate_token:
        print("[DEBUG] Generating token")
        generate_token_func, _ = _get_token_service()
        token = await generate_token_func(contributor, db=db)
        print("[DEBUG] Token generated successfully")
        return {"access_token": token, "token_type": "bearer"}
    
    print("[DEBUG] Returning contributor object")
    return contributor


async def get_current_user(token: str, db: Session = None) -> Dict[str, Any]:
    """
    Get the current user from the token
    
    Args:
        token: The JWT token
        db: Database session (optional)
        
    Returns:
        dict: User information from the token
        
    Raises:
        HTTPException: If the token is invalid or user not found
    """
    close_db = False
    try:
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
            close_db = True
            
        # Verify token and get payload
        _, verify_token_func = _get_token_service()
        payload = await verify_token(token, db)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get username from token
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get user information from the token
        user_info = {
            "username": username,
            "is_contributor": bool(payload.get("is_contributor", False)),
            "is_admin": bool(payload.get("is_admin", False))
        }
        
        return user_info
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting current user: {str(e)}"
        )
    finally:
        if close_db and 'db' in locals():
            db.close()
