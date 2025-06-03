from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

try:
    # When running from project root via run.py
    from server.database import get_language_db
    from server.models import Language
    from server.services.token_service import verify_token
except ImportError:
    # When running directly from server directory
    from database import get_language_db
    from models import Language
    from services.token_service import verify_token



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def add_language(language_name: str, username: str, token: str):
    #Check if token is valid
    try:
        name = await verify_token(token)
    except HTTPException as e:
        raise e
    
    #Check if token username matches requested username
    if name != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code = 403,
            detail = "Not authorized to add this Language"
        )
    
    #Get language database
    db = next(get_language_db())

    #Check if language already exists
    existing_language = db.query(Language).filter(Language.name == language_name).first()

    if existing_language:
        print(f"Language '{language_name}' already exists")
        raise HTTPException(status_code=400, detail="Language already exists")
    
    #Add language
    new_language = Language(name=language_name)
    db.add(new_language)
    db.commit()
    db.refresh(new_language)

    print(f"Successfully added language: {language_name}")
    return {"msg": "Language added successfully"}

async def delete_language(language_name: str, username: str, token: str):
    #Check if token is valid
    try:
        name = await verify_token(token)
    except HTTPException as e:
        raise e
    
    #Check if token username matches requested username
    if name != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code = 403,
            detail = "Not authorized to delete this Language"
        )
    
    #Get language database
    db = next(get_language_db())

    #Check if language exists
    language = db.query(Language).filter(Language.name == language_name).first()

    if not language:
        print(f"Language '{language_name}' not found")
        raise HTTPException(status_code=404, detail="Language not found")
    
    #Delete language
    db.delete(language)
    db.commit()
    
    print(f"Successfully deleted language: {language_name}")
    return {"msg": "Language deleted successfully"}