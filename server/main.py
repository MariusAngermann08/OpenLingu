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
    from server.database import users_engine, get_users_db, get_languages_db
    from server.models import DBUser, Token, Language
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from server.auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from server.services.user_service import get_user_profile, delete_user
    from server.services.token_service import generate_token, verify_token, remove_expired_tokens
    from server.language_handler.languageregistry import add_language, delete_language, get_languages_list as get_languages_list_impl
except ImportError:
    # When running directly from server directory
    from database import users_engine, get_users_db, get_languages_db
    from models import DBUser, Token, Language
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from services.user_service import get_user_profile, delete_user
    from services.token_service import generate_token, verify_token, remove_expired_tokens
    from language_handler.languageregistry import add_language, delete_language, get_languages_list as get_languages_list_impl

# Used for password hashing
from passlib.context import CryptContext

# Define tags for API documentation
tags_metadata = [
    {
        "name": "authentication",
        "description": "User authentication and authorization endpoints",
    },
    {
        "name": "users",
        "description": "User management operations",
    },
    {
        "name": "languages",
        "description": "Language management operations",
    },
    {
        "name": "system",
        "description": "System information and status",
    }
]

app = FastAPI(openapi_tags=tags_metadata)

# Database dependencies
users_db_dependency = Annotated[Session, Depends(get_users_db)]
languages_db_dependency = Annotated[Session, Depends(get_languages_db)]


@app.get("/", tags=["system"])
async def get():
    return {"msg": "OpenLingu"}

from fastapi import Form

@app.post("/login", tags=["authentication"])
async def login(
    username: str,
    password: str
):
    """
    Authenticate a user and return an access token
    
    Args:
        username: The username of the user (from form data)
        password: The user's password (from form data)
        
    Returns:
        dict: Access token and token type
    """
    db = None
    try:
        print(f"[LOGIN] Attempting login for user: {username}")
        
        # Get a new database session
        db = next(get_users_db())
        
        # Authenticate user and generate token
        result = await authenticate_user(
            username=username,
            password=password,
            db=db,
            generate_token=True
        )
        
        # Explicitly commit any pending transactions
        db.commit()
        print(f"[LOGIN] Login successful for user: {username}")
        return result
        
    except HTTPException as e:
        print(f"[LOGIN] Login failed for user {username}: {str(e)}")
        if db:
            db.rollback()
        raise e
        
    except Exception as e:
        # Log the error and return a 500 error
        error_msg = f"Internal server error during login: {str(e)}"
        print(f"[LOGIN] {error_msg}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )
        
    finally:
        # Always close the database session
        if db:
            db.close()

@app.post("/register", tags=["authentication"])
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

@app.post("/logout", tags=["authentication"])
async def logout(token: str, db: users_db_dependency):
    """
    Log out a user by removing their token
    
    Args:
        token: The authentication token to invalidate
        db: Database session dependency
        
    Returns:
        dict: Success message and status
        
    Raises:
        HTTPException: If there's an error during logout
    """
    if not token or not isinstance(token, str) or len(token) < 10:  # Basic validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing authentication token"
        )
    
    print(f"[LOGOUT] Starting logout for token: {token[:10]}...")
    
    try:
        # Verify the token first to ensure it's valid
        try:
            username = await verify_token(token, db)
            print(f"[LOGOUT] Verified token for user: {username}")
        except HTTPException as e:
            if e.status_code == 401:
                print("[LOGOUT] Token is invalid or expired, but will attempt to remove it")
            else:
                raise
        
        # Import token service functions
        from server.services.token_service import remove_token as remove_token_func, remove_expired_tokens as remove_expired_tokens_func
        
        # Remove the specific token
        token_removed = await remove_token_func(token, db)
        
        # Also clean up any expired tokens
        expired_count = await remove_expired_tokens_func(db)
        
        if not token_removed:
            print(f"[WARNING] Token not found during logout - it may have already been removed or expired")
            
        return {
            "status": "success",
            "message": "Successfully logged out",
            "token_removed": token_removed,
            "expired_tokens_removed": expired_count
        }
        
    except HTTPException as he:
        print(f"[LOGOUT] HTTP Error during logout: {str(he)}")
        raise
    except Exception as e:
        db.rollback()
        error_msg = f"Unexpected error during logout: {str(e)}"
        print(f"[LOGOUT] {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@app.get("/user/{username}", tags=["users"])
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

@app.delete("/user/{username}", tags=["users"])
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

@app.post("/languages", tags=["languages"])
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

@app.delete("/languages/{language_name}", tags=["languages"])
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

@app.get("/languages", tags=["languages"])
async def get_languages_list(db: languages_db_dependency):
    """
    Get a list of all languages in the database
    
    Args:
        db: Database session dependency
        
    Returns:
        list: List of language names
    """
    return await get_languages_list_impl(db)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    import logging
    from fastapi import HTTPException
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Ensure this logger shows INFO and above
    logger.info("Starting server initialization...")
    
    # Initialize the database
    try:
        logger.info("Initializing database...")
        try:
            from server.init_db import init_db
        except ImportError:
            from init_db import init_db
            
        init_db()
        logger.info("Database initialization complete")
        
    except Exception as e:
        error_msg = f"Failed to initialize database: {str(e)}"
        logger.error("Failed to initialize database", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize database. See server logs for details."
        )
    
    # Clean up any expired tokens
    db = None
    try:
        logger.debug("Cleaning up expired tokens...")
        # Get a database session
        db = next(get_users_db())
        try:
            await remove_expired_tokens(db)
            logger.debug("Successfully cleaned up expired tokens on startup")
        except Exception as e:
            logger.warning("Error cleaning up expired tokens", exc_info=True)
            # Continue even if token cleanup fails
    except Exception as e:
        logger.warning("Error during token cleanup", exc_info=True)
        # Continue even if we can't clean up tokens
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.warning("Error closing database connection", exc_info=True)
    
    logger.info("Server initialization complete")

# Remove expired tokens on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down server...")
    # Clean up any remaining expired tokens
    db = None
    try:
        print("Cleaning up expired tokens before shutdown...")
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
