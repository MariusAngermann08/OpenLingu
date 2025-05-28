from datetime import datetime
from jose import JWTError, jwt
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session

# Import lib for pwd hashing
from passlib.context import CryptContext

# Import from server modules
try:
    from server.auth import *
    from server.database import get_db
    from server.models import Token, DBUser
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fall back to direct imports when running directly
    from auth import *
    from database import get_db
    from models import Token, DBUser
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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