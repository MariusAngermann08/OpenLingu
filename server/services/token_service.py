from datetime import datetime, timedelta
import uuid
from jose import JWTError, jwt
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session

# Import lib for pwd hashing
from passlib.context import CryptContext

# Import from server modules
try:
    from server.models import Token, DBUser, DBContributor
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fall back to direct imports when running directly
    from models import Token, DBUser, DBContributor
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Import get_users_db only when needed to avoid circular imports
def _get_users_db():
    try:
        from server.database import get_users_db as _get_db
    except ImportError:
        from database import get_users_db as _get_db
    return _get_db()

async def generate_token(user: DBUser, db: Session = None, save_to_db: bool = True):
    """
    Generate a JWT token for the user
    
    Args:
        user: The user to generate token for
        db: Optional database session to check for token collisions
        save_to_db: Whether to save the token to the database
        
    Returns:
        str: The generated JWT token
    """
    close_db = False
    try:
        print(f"[DEBUG] Generating token for user: {user.username}")
        print(f"[DEBUG] SECRET_KEY: {'Set' if SECRET_KEY else 'Not set'}")
        print(f"[DEBUG] ALGORITHM: {ALGORITHM}")
        
        # Get database session if not provided and we need to save to db
        if db is None and save_to_db:
            db = next(_get_users_db())
            close_db = True
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Calculate expiration time
                expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                expire = datetime.utcnow() + expires_delta
                
                # Generate token with current timestamp and expiration
                token_data = {
                    "sub": user.username,
                    "iat": datetime.utcnow(),
                    "nbf": datetime.utcnow(),
                    "exp": expire,  # Set explicit expiration
                    "jti": str(uuid.uuid4()),  # Add a unique ID to the token
                    "is_contributor": hasattr(user, 'is_contributor') and user.is_contributor or False,
                    "is_admin": hasattr(user, 'is_admin') and user.is_admin or False
                }
                print(f"[DEBUG] Token data: {token_data}")
                
                token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
                print(f"[DEBUG] Token generated: {token}")
                
                if save_to_db and db is not None:
                    # Save the token to the database
                    db_token = Token(
                        token=token,
                        expires=expire
                    )
                    db.add(db_token)
                    db.commit()
                    db.refresh(db_token)
                    print(f"[DEBUG] Token saved to database")
                
                return token
                    
            except Exception as e:
                print(f"[ERROR] Failed to generate token: {str(e)}")
                if attempt >= max_attempts - 1:
                    raise
                attempt += 1
                
        raise Exception("Failed to generate unique token after multiple attempts")
        
    except Exception as e:
        print(f"[ERROR] Failed to generate token: {str(e)}")
        raise
    finally:
        if close_db and 'db' in locals():
            db.close()

async def verify_token(token: str, db: Session = None) -> dict:
    """
    Verify the JWT token and return the username if valid.
    
    Args:
        token: The JWT token to verify
        db: Optional database session. If not provided, a new one will be created.
        
    Returns:
        str: The username from the token
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    close_db = False
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No authentication token provided",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get database session if not provided
        if db is None:
            db = next(_get_users_db())
            close_db = True
            
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: No username in token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get database session if not provided
        if db is None:
            db = next(_get_users_db())
            close_db = True
        
        # Check if token exists in database
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: Token not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Check if token is expired
        if db_token.expires < datetime.utcnow():
            # Remove expired token from database
            db.delete(db_token)
            db.commit()
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Check if user exists in either DBUser or DBContributor
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            # Check if user is a contributor
            contributor = db.query(DBContributor).filter(DBContributor.username == username).first()
            if not contributor:
                raise HTTPException(
                    status_code=401,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        # Return the entire payload with user information
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    finally:
        if close_db and 'db' in locals():
            db.close()

async def remove_token(token: str, db: Session) -> bool:
    """
    Remove a specific token from the database with more reliable approach
    
    Args:
        token: The token to remove
        db: Database session
        
    Returns:
        bool: True if token was found and removed, False otherwise
    """
    if not token or not isinstance(token, str):
        print("[ERROR] Invalid token provided for removal")
        return False
        
    try:
        print(f"[DEBUG] Attempting to remove token: {token[:10]}...")
        
        # First try to find the token
        token_entry = db.query(Token).filter(Token.token == token).first()
        
        if token_entry is None:
            print("[DEBUG] Token not found in database")
            return False
            
        print(f"[DEBUG] Found token, deleting...")
        
        # Delete using the instance
        db.delete(token_entry)
        
        # Force flush to ensure the delete is executed
        db.flush()
        
        # Commit the transaction
        db.commit()
        
        # Verify deletion
        token_still_exists = db.query(Token).filter(Token.token == token).first() is not None
        
        if token_still_exists:
            print("[ERROR] Token still exists after deletion attempt!")
            return False
            
        print("[DEBUG] Token successfully removed from database")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error removing token: {str(e)}")
        print(f"[DEBUG] Token value that caused error: {token}")
        return False

async def remove_expired_tokens(db: Session) -> int:
    """
    Remove all expired tokens from the database
    
    Args:
        db: Database session
        
    Returns:
        int: Number of tokens that were removed
    """
    try:
        print("[DEBUG] Removing expired tokens")
        # First find all expired tokens
        expired_tokens = db.query(Token).filter(Token.expires < datetime.utcnow()).all()
        expired_count = len(expired_tokens)
        
        if expired_count > 0:
            print(f"[DEBUG] Found {expired_count} expired tokens to remove")
            # Delete each token individually for better reliability
            for token in expired_tokens:
                db.delete(token)
            
            db.commit()
            print(f"[DEBUG] Successfully removed {expired_count} expired tokens")
        else:
            print("[DEBUG] No expired tokens to remove")
            
        return expired_count
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error removing expired tokens: {str(e)}")
        return 0