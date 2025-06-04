from datetime import datetime
from jose import JWTError, jwt
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session

# Import lib for pwd hashing
from passlib.context import CryptContext

# Import from server modules
try:
    from server.auth import *
    from server.database import get_users_db
    from server.models import Token, DBUser
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fall back to direct imports when running directly
    from auth import *
    from database import get_users_db
    from models import Token, DBUser
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

async def generate_token(user: DBUser):
    token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def verify_token(token: str, db: Session = None) -> str:
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
            
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: No username in token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
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
            
        # Check if user exists
        user = db.query(DBUser).filter(DBUser.username == username).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return username
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    finally:
        if close_db and 'db' in locals():
            db.close()

async def remove_expired_tokens(db: Session):
    db.query(Token).filter(Token.expires < datetime.utcnow()).delete()
    db.commit()