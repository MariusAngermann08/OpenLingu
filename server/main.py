from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated

# Import modules
try:
    # When running from project root via run.py
    from server.database import users_engine, get_users_db, get_language_db
    from server.models import DBUser, Token, Language
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from server.auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from server.services.user_service import get_user_profile, delete_user
    from server.services.token_service import generate_token, verify_token, remove_expired_tokens
    from server.language_handler.languageregistry import add_language, delete_language
except ImportError:
    # When running directly from server directory
    from database import users_engine, get_users_db, get_language_db
    from models import DBUser, Token, Language
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from services.user_service import get_user_profile, delete_user
    from services.token_service import generate_token, verify_token, remove_expired_tokens
    from language_handler.languageregistry import add_language, delete_language

# Used for password hashing
from passlib.context import CryptContext

app = FastAPI()

# Database dependencies
users_db_dependency = Annotated[Session, Depends(get_users_db)]
languages_db_dependency = Annotated[Session, Depends(get_language_db)]


@app.get("/")
async def get():
    return {"msg": "OpenLingu"}

from fastapi import Form

@app.post("/login")
async def login(
    username: str,
    password: str,
    db: Session = Depends(get_users_db)
):
    """
    Authenticate a user and return an access token
    
    Args:
        username: The username of the user (from form data)
        password: The user's password (from form data)
        db: Database session dependency
        
    Returns:
        dict: Access token and token type
    """
    try:
        print(f"[LOGIN] Attempting login for user: {username}")
        # Authenticate user and generate token
        result = await authenticate_user(
            username=username,
            password=password,
            db=db,
            generate_token=True
        )
        print(f"[LOGIN] Login successful for user: {username}")
        return result
        
    except HTTPException as e:
        print(f"[LOGIN] Login failed for user {username}: {str(e)}")
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log the error and return a 500 error
        error_msg = f"Internal server error during login: {str(e)}"
        print(f"[LOGIN] {error_msg}")
        if 'db' in locals():
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@app.post("/register")
async def register(username: str, email: str, password: str, db: users_db_dependency):
    """
    Register a new user
    
    Args:
        username: The username for the new user
        password: The password for the new user
        email: The email for the new user
        db: Database session dependency
        
    Returns:
        dict: Success message
    """
    # Check if user already exists
    existing_user = db.query(DBUser).filter(DBUser.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Create new user
    try:
        user = await create_user(username, email, password, db)
        return {"message": "User created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )
    
    return {"message": "User created successfully"}

@app.post("/logout")
async def logout(token: str, db: users_db_dependency):
    """
    Log out a user by removing their token
    
    Args:
        token: The authentication token to invalidate
        db: Database session dependency
        
    Returns:
        dict: Success message
    """
    # Remove the token from the database
    try:
        await remove_expired_tokens(db)
        return {"message": "Logged out successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging out: {str(e)}"
        )

@app.get("/user/{username}")
async def get_user(username: str, token: str, db: users_db_dependency):
    """
    Get a user's profile information
    
    Args:
        username: The username of the user to retrieve
        token: Authentication token
        db: Database session dependency
        
    Returns:
        dict: User profile information
    """
    return await get_user_profile(username, token, db)

@app.delete("/user/{username}")
async def delete_db_user(username: str, token: str, db: users_db_dependency):
    """
    Delete a user account
    
    Args:
        username: The username of the user to delete
        token: Authentication token
        db: Database session dependency
        
    Returns:
        dict: Success message
    """
    return await delete_user(username, token, db)

@app.post("/language/{language_name}")
async def add_language_to_db(language_name: str, username: str, token: str, db: languages_db_dependency):
    """
    Add a new language
    
    Args:
        language_name: The name of the language to add
        username: The username of the user making the request
        token: Authentication token
        db: Database session dependency
        
    Returns:
        dict: Success message and language details
    """
    return await add_language(language_name, username, token, db)

@app.delete("/language/{language_name}")
async def delete_language_from_db(language_name: str, username: str, token: str, db: languages_db_dependency):
    """
    Delete a language
    
    Args:
        language_name: The name of the language to delete
        username: The username of the user making the request
        token: Authentication token
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If there's an error deleting the language
    """
    try:
        result = await delete_language(language_name, username, token, db)
        return result
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status codes
        raise e
    except Exception as e:
        # Log the full error for debugging
        print(f"Error deleting language: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the language: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    # Initialize the database
    try:
        from server.init_db import init_db
    except ImportError:
        from init_db import init_db
    init_db()
    
    # Clean up any expired tokens
    try:
        # Get a database session
        db = next(get_users_db())
        try:
            await remove_expired_tokens(db)
            print("Successfully cleaned up expired tokens on startup")
        except Exception as e:
            print(f"Error cleaning up expired tokens on startup: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        print(f"Failed to get database session for token cleanup on startup: {str(e)}")

# Remove expired tokens on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Clean up any remaining expired tokens
    try:
        # Get a database session
        db = next(get_users_db())
        try:
            await remove_expired_tokens(db)
            print("Successfully cleaned up expired tokens on shutdown")
        except Exception as e:
            print(f"Error cleaning up expired tokens on shutdown: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        print(f"Failed to get database session for token cleanup on shutdown: {str(e)}")
