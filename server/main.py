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
    from server.database import engine, get_db
    from server.models import Base, DBUser, Token
    from server.parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from server.auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from server.services.user_service import get_user_profile
    from server.services.token_service import generate_token, verify_token, remove_expired_tokens
    from server.language_handler.languageregistry import add_language
except ImportError:
    # When running directly from server directory
    from database import engine, get_db
    from models import Base, DBUser, Token
    from parameters import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    from auth import create_user, authenticate_user, verify_password, pwd_context, remove_user
    from services.user_service import get_user_profile
    from services.token_service import generate_token, verify_token, remove_expired_tokens
    from language_handler.languageregistry import add_language

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
    return await get_user_profile(username, token)

@app.delete("/users/{username}/delete")

@app.post("/languages/add")
async def add_language_to_db(language_name: str, username: str, token: str):
    return await add_language(language_name, username, token)

@app.delete("/languages/delete")
async def delete_language_from_db(language_name: str, username: str, token: str):
    return await delete_language(language_name, username, token)


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
