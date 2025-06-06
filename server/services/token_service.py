from datetime import datetime
from jose import JWTError, jwt
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session

# Import lib for pwd hashing
from passlib.context import CryptContext

# Import from server modules
try:
    from server.models import Token, DBUser
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fall back to direct imports when running directly
    from models import Token, DBUser
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Import get_users_db only when needed to avoid circular imports
def _get_users_db():
    try:
        from server.database import get_users_db as _get_db
    except ImportError:
        from database import get_users_db as _get_db
    return _get_db()

async def generate_token(user: DBUser):
    try:
        print(f"[DEBUG] Generating token for user: {user.username}")
        print(f"[DEBUG] SECRET_KEY: {'Set' if SECRET_KEY else 'Not set'}")
        print(f"[DEBUG] ALGORITHM: {ALGORITHM}")
        
        token_data = {"sub": user.username}
        print(f"[DEBUG] Token data: {token_data}")
        
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        print(f"[DEBUG] Token generated: {token}")
        
        return token
    except Exception as e:
        print(f"[ERROR] Failed to generate token: {str(e)}")
        raise

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