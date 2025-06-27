from fastapi import FastAPI, status, Depends, HTTPException, Request, Path, Body, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Annotated, Callable, Awaitable
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
import logging
import uvicorn
import os
import sys
from functools import wraps

# Import from server modules
try:
    # When running from project root via run.py
    from server.database import users_engine, get_users_db, get_languages_db
    from server.models import DBUser, Token, Language, Lection, DBContributor
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from server.auth import create_user, authenticate_user, verify_password, pwd_context, remove_user, authenticate_contributer
    from server.services.user_service import get_user_profile, delete_user
    from server.services.token_service import generate_token, verify_token, remove_expired_tokens
    from server.language_handler.languageregistry import add_language, add_lection, edit_lection, delete_lection, delete_language, get_languages_list as get_languages_list_impl
except ImportError:
    # When running directly from server directory
    from database import users_engine, get_users_db, get_languages_db
    from models import DBUser, Token, Language, Lection, DBContributor
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from auth import create_user, authenticate_user, verify_password, pwd_context, remove_user, authenticate_contributer
    from services.user_service import get_user_profile, delete_user
    from services.token_service import generate_token, verify_token, remove_expired_tokens
    from language_handler.languageregistry import add_language, add_lection, edit_lection, delete_lection, delete_language, get_languages_list as get_languages_list_impl

def get_contributor_by_username(db: Session, username: str):
    """Get a contributor by username."""
    return db.query(DBContributor).filter(DBContributor.username == username).first()

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
    },
    {
        "name": "contributer",
        "description": "Contributer management operations",
    }
]

app = FastAPI(openapi_tags=tags_metadata)

# Middleware to clean up expired tokens on every request
@app.middleware("http")
async def cleanup_expired_tokens_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Middleware to clean up expired tokens on every request.
    This ensures that expired tokens are removed from the database even if the server runs for a long time.
    """
    # Get a database session
    db = next(get_users_db())
    try:
        # Clean up expired tokens
        removed_count = await remove_expired_tokens(db)
        if removed_count > 0:
            print(f"[MIDDLEWARE] Removed {removed_count} expired tokens")
    except Exception as e:
        print(f"[MIDDLEWARE] Error cleaning up expired tokens: {str(e)}")
    finally:
        # Always close the database session
        db.close()
    
    # Continue processing the request
    response = await call_next(request)
    return response

# Database dependencies
users_db_dependency = Annotated[Session, Depends(get_users_db)]
languages_db_dependency = Annotated[Session, Depends(get_languages_db)]

# Auth dependencies
async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_users_db)
) -> Dict[str, Any]:
    """
    Dependency to get the current user from the Authorization header
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    try:
        # Import the verify_token function
        from services.token_service import verify_token
        
        # Verify the token and get the payload
        payload = await verify_token(token, db)
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: No username in token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get the user from the database
        user = get_contributor_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return {
            "username": user.username,
            "is_contributor": True,
            "is_admin": getattr(user, "is_admin", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_contributor(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require contributor status
    """
    if not user.get("is_contributor", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contributor privileges required"
        )
    return user

def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require admin status
    """
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user


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

@app.get("/login_contributer", response_model=Dict[str, Any], tags=["authentication"])
async def login_contributer(
    username: str,
    password: str,
    db: Session = Depends(get_users_db)
):
    """
    Authenticate a contributor and return an access token with role information
    
    Args:
        username: The username of the contributor
        password: The contributor's password
        db: Database session dependency
        
    Returns:
        dict: Access token, token type, and user information including roles
        
    Raises:
        HTTPException: If authentication fails
    """
    print(f"[DEBUG] login_contributer called with username: {username}")
    
    try:
        print("[DEBUG] Starting authentication...")
        
        # First, check if the user exists
        user = get_contributor_by_username(db, username)
        if not user:
            print(f"[DEBUG] User {username} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        print(f"[DEBUG] User found: {user.username}")
        
        # Now authenticate with password
        auth_result = await authenticate_contributer(username, password, db, generate_token=True)
        
        # If we get here, authentication was successful
        if not auth_result or "access_token" not in auth_result:
            print("[ERROR] Authentication succeeded but no token was returned")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication succeeded but no token was generated"
            )
            
        print("[DEBUG] Authentication successful, generating response...")
        
        # Get the user object with role information
        user_info = {
            "username": username,
            "is_contributor": True,  # This endpoint is only for contributors
            "is_admin": getattr(user, "is_admin", False)
        }
        
        response = {
            "access_token": auth_result["access_token"],
            "token_type": "bearer",
            "user": user_info
        }
        
        print(f"[DEBUG] Returning successful response for user: {username}")
        return response
        
    except HTTPException as he:
        print(f"[DEBUG] HTTPException in login_contributer: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Exception in login_contributer: {str(e)}")
        print(f"[ERROR] Traceback: {error_details}")
        
        # Return more detailed error in development
        if os.getenv("ENVIRONMENT", "development") == "development":
            detail = f"An error occurred during authentication: {str(e)}\n\n{error_details}"
        else:
            detail = "An error occurred during authentication"
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
    finally:
        # Make sure to close the database session
        if db:
            db.close()

from pydantic import BaseModel

class UserCreate(BaseModel):
    """Model for user registration data"""
    username: str
    email: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "newuser",
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }

@app.post("/register", 
          response_model=Dict[str, Any], 
          status_code=status.HTTP_201_CREATED,
          tags=["authentication"],
          summary="Register a new user account",
          responses={
              201: {"description": "User registered successfully"},
              400: {"description": "Invalid input data"},
              409: {"description": "Username or email already exists"},
              500: {"description": "Internal server error"}
          })
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_users_db)
):
    """
    Register a new user account
    
    This endpoint allows new users to create an account. The username must be unique,
    and the password must be at least 8 characters long.
    
    Args:
        user_data: User registration data including username, email, and password
        db: Database session dependency
        
    Returns:
        dict: Access token, token type, and basic user information
        
    Raises:
        HTTPException: If registration fails due to invalid data or existing user
    """
    try:
        # Validate input
        if len(user_data.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )
            
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
            
        # Check if username or email already exists
        existing_user = db.query(DBUser).filter(
            (DBUser.username == user_data.username) | 
            (DBUser.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
            
        # Create the user
        user = await create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        # Return success response without token
        return {
            "status": "success",
            "message": "User registered successfully. Please sign in.",
            "user": {
                "username": user.username,
                "email": user.email
            }
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "unique constraint" in error_msg:
            if "username" in error_msg:
                detail = "Username already exists"
            elif "email" in error_msg:
                detail = "Email already in use"
            else:
                detail = "User with these details already exists"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail
            )
        print(f"Error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )
    finally:
        if db:
            db.close()

@app.post("/logout", tags=["authentication"])
async def logout(
    authorization: str = Header(..., description="Bearer token"),
    db: Session = Depends(get_users_db)
):
    """
    Log out a user by removing their token
    
    Args:
        authorization: The Authorization header containing the Bearer token
        db: Database session dependency
        
    Returns:
        dict: Success message and status
        
    Raises:
        HTTPException: If there's an error during logout
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing Authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    if not token or len(token) < 10:  # Basic validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing authentication token"
        )
    
    print(f"[LOGOUT] Starting logout for token: {token[:10]}...")
    
    try:
        # Verify the token first to ensure it's valid
        try:
            user = await get_current_user(authorization, db)
            print(f"[LOGOUT] Verified token for user: {user['username']}")
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
        
        # Close the database session
        db.close()
            
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
    finally:
        if db:
            db.close()

@app.get("/me", response_model=Dict[str, Any], tags=["users"])
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """
    Get the current authenticated user's profile
    
    Args:
        current_user: The currently authenticated user
        db: Database session dependency
        
    Returns:
        dict: Current user's profile information
        
    Raises:
        HTTPException: If user is not found
    """
    try:
        return await get_user_profile(current_user["username"], current_user["username"], db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )

@app.get("/user/{username}", tags=["users"])
async def get_user(
    username: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_users_db)
):
    """
    Get a user's profile information (admin only)
    
    Args:
        username: The username of the user to retrieve
        current_user: The currently authenticated user
        db: Database session dependency
        
    Returns:
        dict: User profile information
        
    Raises:
        HTTPException: If user is not found or not authorized
    """
    # Only admins can view other users' profiles
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view other users' profiles"
        )
    
    try:
        return await get_user_profile(username, current_user["username"], db)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profile: {str(e)}"
        )

@app.delete("/user/{username}", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user_endpoint(
    username: str,
    current_user: Dict[str, Any] = Depends(require_admin),  # Only admins can delete users
    db: Session = Depends(get_users_db)
):
    """
    Delete a user account (admin only)
    
    Args:
        username: The username of the user to delete
        current_user: The currently authenticated admin user
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not an admin or deletion fails
    """
    try:
        # Prevent admins from deleting themselves
        if username == current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admins cannot delete their own accounts"
            )
            
        result = await delete_user(username, current_user["username"], db)
        return {
            "status": "success",
            "message": f"User '{username}' deleted successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
    finally:
        if db:
            db.close()

class LanguageCreate(BaseModel):
    username: str

@app.post(
    "/add_language/{language_name}",
    tags=["languages"],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Language added successfully"},
        400: {"description": "Language already exists"},
        401: {"description": "Not authenticated"},
        403: {"description": "Contributor privileges required"},
        500: {"description": "Internal server error"}
    }
)
async def add_language_to_db(
    request: Request,
    language_name: str,
    language_data: LanguageCreate,
    current_user: Dict[str, Any] = Depends(require_contributor),
    db: Session = Depends(get_languages_db)
):
    """
    Add a new language (Contributor only)
    
    This endpoint allows contributors to add a new language to the system.
    The user must be authenticated as a contributor.
    
    Args:
        language_name: The name of the language to add
        current_user: The authenticated contributor's information (from token)
        db: Database session dependency
        
    Returns:
        dict: Success message and language details
        
    Raises:
        HTTPException: If the language already exists or other error occurs
    """
    try:
        # Add the language using the contributor's username and token
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.split(" ")[1]
        
        # Get the username from the request body
        username = language_data.username
        
        result = await add_language(
            language_name=language_name,
            username=username,
            token=token,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Language '{language_name}' added successfully", 
            "data": result
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Language '{language_name}' already exists"
            )
        print(f"Error adding language: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the language"
        )
    finally:
        if db:
            db.close()

@app.delete(
    "/delete_language/{language_name}",
    tags=["languages"],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Language deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Contributor privileges required"},
        404: {"description": "Language not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_language_from_db(
    request: Request,
    language_name: str,
    current_user: Dict[str, Any] = Depends(require_contributor),
    db: Session = Depends(get_languages_db)
):
    """
    Delete a language (Contributor only)
    
    This endpoint allows contributors to delete a language from the system.
    The user must be authenticated as a contributor.
    
    Args:
        language_name: The name of the language to delete
        current_user: The authenticated contributor's information (from token)
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If the language doesn't exist or other error occurs
    """
    try:
        # Get the token from the Authorization header
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.split(" ")[1]
        
        # Delete the language using the contributor's username and token
        await delete_language(
            language_name=language_name,
            username=current_user["username"],
            token=token,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Language '{language_name}' deleted successfully"
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language '{language_name}' not found"
            )
        print(f"Error deleting language: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the language"
        )
    finally:
        if db:
            db.close()

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

class LectionCreate(BaseModel):
    lection_name: str
    content: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "lection_name": "Lektion 1",
                "content": {
                    "id": "spanish_grammar_101", 
                    "title": "Spanish Grammar Basics", 
                    "pages": []
                }
            }
        }


@app.post(
    "/add_lection/{language_name}",
    tags=["lections"],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Lection created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Contributor privileges required"},
        404: {"description": "Language not found"},
        409: {"description": "Lection already exists"},
        500: {"description": "Internal server error"}
    }
)
async def add_lection_to_db(
    request: Request,
    language_name: str,
    lection_data: LectionCreate,
    current_user: Dict[str, Any] = Depends(require_contributor),
    db: Session = Depends(get_languages_db)
):
    """
    Add a new lection (Contributor only)
    
    This endpoint allows contributors to add a new lection to a language.
    The user must be authenticated as a contributor.
    
    Args:
        language_name: The name of the language to add the lection to
        lection_data: Lection data including name and content
        current_user: The authenticated contributor's information (from token)
        db: Database session dependency
        
    Returns:
        dict: Success message and lection details
        
    Raises:
        HTTPException: If the lection already exists, language not found, or other error occurs
    """
    try:
        # Get the token from the Authorization header
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.split(" ")[1]
        
        # Add the lection using the contributor's username and token
        result = await add_lection(
            language_name=language_name,
            lection_name=lection_data.lection_name,
            username=current_user["username"],
            token=token,
            content=lection_data.content,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Lection '{lection_data.lection_name}' added to '{language_name}' successfully",
            "data": result
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lection '{lection_data.lection_name}' already exists in language '{language_name}'"
            )
        elif "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language '{language_name}' not found"
            )
        print(f"Error adding lection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the lection"
        )
    finally:
        if db:
            db.close()

@app.get("/languages/{language_name}/lections", tags=["lections"])
def get_lection_list(language_name: str, db: Session = Depends(get_languages_db)):
    """
    Get a list of all lections for a language
    
    Args:
        language_name: Name of the language to get the lections from
        db: Database session dependency
        
    Returns:
        list: List of lection dictionaries with id and title
        
    Raises:
        HTTPException: If there's an error accessing the database
    """
    try:
        # Query the database for lections matching the language and return just the titles
        lections = db.query(Lection).filter(Lection.language == language_name).all()
        
        # Return a list of lection dictionaries with only id and title
        return [{"id": lection.id, "title": lection.title} for lection in lections]
        
    except Exception as e:
        # Log the error and return a 500 error
        print(f"Error getting lection list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the lection list"
        )

@app.get("/languages/{language_name}/lections/by_title/{title}", tags=["lections"])
async def get_lection_by_title(
    language_name: str = Path(..., description="Name of the language"),
    title: str = Path(..., description="Title of the lection"),
    db: Session = Depends(get_languages_db)
):
    """
    Get the content of a specific lection by its title
    
    Args:
        language_name: Name of the language
        title: Title of the lection to retrieve
        db: Database session dependency
        
    Returns:
        dict: Lection details including content
        
    Raises:
        HTTPException: If the lection is not found or there's an error
    """
    try:
        # Query the database for the specific lection by title
        lection = db.query(Lection).filter(
            Lection.title == title,
            Lection.language == language_name
        ).first()
        
        if not lection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lection with title '{title}' not found in language '{language_name}'"
            )
            
        return {
            "id": lection.id,
            "title": lection.title,
            "description": lection.description,
            "language": lection.language,
            "difficulty": lection.difficulty,
            "created_at": lection.created_at,
            "created_by": lection.created_by,
            "content": lection.content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting lection content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the lection content"
        )

@app.get("/languages/{language_name}/lections/{lection_id}", tags=["lections"])
async def get_lection_by_id(
    language_name: str = Path(..., description="Name of the language"),
    lection_id: str = Path(..., description="ID of the lection"),
    db: Session = Depends(get_languages_db)
):
    """
    Get the content of a specific lection by its ID
    
    Args:
        language_name: Name of the language
        lection_id: ID of the lection to retrieve
        db: Database session dependency
        
    Returns:
        dict: Lection details including content
        
    Raises:
        HTTPException: If the lection is not found or there's an error
    """
    try:
        # Query the database for the specific lection by ID
        lection = db.query(Lection).filter(
            Lection.id == lection_id,
            Lection.language == language_name
        ).first()
        
        if not lection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lection with ID {lection_id} not found in language '{language_name}'"
            )
            
        return {
            "id": lection.id,
            "title": lection.title,
            "description": lection.description,
            "language": lection.language,
            "difficulty": lection.difficulty,
            "created_at": lection.created_at,
            "created_by": lection.created_by,
            "content": lection.content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting lection content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the lection content"
        )

@app.put(
    "/edit_lection/{language_name}",
    tags=["lections"],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lection updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
        403: {"description": "Contributor privileges required"},
        404: {"description": "Lection or language not found"},
        500: {"description": "Internal server error"}
    }
)
async def edit_lection_to_db(
    request: Request,
    language_name: str,
    lection_data: LectionCreate,
    current_user: Dict[str, Any] = Depends(require_contributor),
    db: Session = Depends(get_languages_db)
):
    """
    Edit a lection (Contributor only)
    
    This endpoint allows contributors to edit an existing lection.
    The user must be authenticated as a contributor.
    
    Args:
        language_name: The name of the language the lection belongs to
        lection_data: Updated lection data including name and content
        current_user: The authenticated contributor's information (from token)
        db: Database session dependency
        
    Returns:
        dict: Success message and updated lection details
        
    Raises:
        HTTPException: If the lection doesn't exist, permission denied, or other error occurs
    """
    try:
        # Get the token from the Authorization header
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.split(" ")[1]
        
        # Edit the lection using the contributor's username and token
        result = await edit_lection(
            language_name=language_name,
            lection_name=lection_data.lection_name,
            username=current_user["username"],
            token=token,
            content=lection_data.content,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success",
            "message": f"Lection '{lection_data.lection_name}' updated successfully",
            "data": result
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lection or language not found: {error_msg}"
            )
        elif "permission" in error_msg or "not authorized" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this lection"
            )
        print(f"Error updating lection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the lection"
        )
    finally:
        if db:
            db.close()

@app.delete(
    "/delete_lection/{language_name}/{lection_name}",
    tags=["lections"],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lection deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Contributor privileges or ownership required"},
        404: {"description": "Lection or language not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_lection_from_db(
    request: Request,
    language_name: str,
    lection_name: str,
    current_user: Dict[str, Any] = Depends(require_contributor),
    db: Session = Depends(get_languages_db)
):
    """
    Delete a lection (Contributor only)
    
    This endpoint allows contributors to delete a lection they own.
    The user must be authenticated as a contributor and must be the owner of the lection.
    
    Args:
        language_name: The name of the language the lection belongs to
        lection_name: The name of the lection to delete
        current_user: The authenticated contributor's information (from token)
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If the lection doesn't exist, permission denied, or other error occurs
    """
    try:
        # Get the token from the Authorization header
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = authorization.split(" ")[1]
        
        # Delete the lection using the contributor's username and token
        await delete_lection(
            language_name=language_name,
            lection_name=lection_name,
            username=current_user["username"],
            token=token,
            db=db
        )
        
        # Commit the transaction
        db.commit()
        
        return {
            "status": "success",
            "message": f"Lection '{lection_name}' deleted successfully from '{language_name}'"
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lection '{lection_name}' not found in language '{language_name}'"
            )
        elif "permission" in error_msg or "not authorized" in error_msg or "not the owner" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this lection. Only the owner can delete it."
            )
        print(f"Error deleting lection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the lection"
        )
    finally:
        if db:
            db.close()

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
