from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
import sys
from pathlib import Path

try:
    # Try absolute imports first (when running as a module)
    from server.models import *
    from server.parameters import *
    from server.auth import *
    from server.database import *
except ImportError:
    # Fall back to relative imports (when running directly)
    from models import *
    from parameters import *
    from auth import *
    from database import *

#Used for password hashing
from passlib.context import CryptContext

app = FastAPI()

db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def get():
    return {"msg": "OpenLingu"}

@app.post("/login")
async def login(username: str, password: str):
    """
    Authenticate a user with username and password.
    
    Args:
        username: The user's username
        password: The user's password
        
    Returns:
        dict: Access token and token type if authentication is successful
    """
    try:
        return await authenticate_user(username, password)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in login endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during login"
        )

@app.post("/register")
async def register(username: str, password: str, email: str):
    try:
        # Create the user
        user = await create_user(username, email, password)
        
        # Optionally, log the user in automatically after registration
        # by uncommenting the following lines:
        # login_response = await authenticate_user(username, password)
        # return login_response
        
        return {
            "msg": "User created successfully",
            "username": user.username,
            "email": user.email
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in register endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )

@app.post("/logout")
async def logout(token: str):
    db = next(get_db())
    db.query(Token).filter(Token.token == token).delete()
    db.commit()
    db.close()
    return {"msg": "Logged out successfully"}

@app.get("/users/{username}")
async def get_user(username: str, token: str):
    db = None
    try:
        # Verify the token and get the username from it
        token_username = await verify_token(token)
        
        # Check if the token username matches the requested username
        if token_username != username:
            print(f"Token username '{token_username}' does not match requested username '{username}'")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this user's data"
            )
            
        # Get the user from the database
        db = next(get_db())
        user = db.query(DBUser).filter(DBUser.username == username).first()
        
        if not user:
            print(f"User '{username}' not found in database")
            raise HTTPException(status_code=404, detail="User not found")
            
        print(f"Successfully retrieved user: {username}")
        return {
            "username": user.username, 
            "email": user.email
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
        
    except Exception as e:
        # Log the error and return a 500 response
        print(f"Error in get_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving user data"
        )
        
    finally:
        # Ensure database connection is closed
        if db:
            db.close()

@app.delete("/users/{username}/delete")
async def delete_user(username: str, token:str):
    #Check if token is valid
    try:
        token_username = await verify_token(token)
    except HTTPException as e:
        raise e
    
    #Check if token username matches requested username
    if token_username != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code = 403,
            detail = "Not authorized to delete this User"
        )
    
    #Delete user
    try:
        await remove_user(username)
        return {"msg": "User deleted successfully"}
    except HTTPException as e:
        raise e
    
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting user: {str(e)}"
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
    await remove_expired_tokens()

# Remove expired tokens on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    # Clean up any remaining expired tokens
    await remove_expired_tokens()
