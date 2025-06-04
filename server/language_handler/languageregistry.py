from fastapi import HTTPException, status
from sqlalchemy.orm import Session

try:
    # When running from project root via run.py
    from server.models import Language
    from server.services.token_service import verify_token
except ImportError:
    # When running directly from server directory
    from models import Language
    from services.token_service import verify_token

async def add_language(language_name: str, username: str, token: str, db: Session):
    """
    Add a new language to the database
    
    Args:
        language_name: Name of the language to add
        username: Username of the user making the request
        token: Authentication token
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not authorized or language already exists
    """
    # Check if token is valid
    try:
        name = await verify_token(token)
    except HTTPException as e:
        raise e
    
    # Check if token username matches requested username
    if name != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add this Language"
        )
    
    # Check if language already exists
    existing_language = db.query(Language).filter(Language.name == language_name).first()

    if existing_language:
        print(f"Language '{language_name}' already exists")
        raise HTTPException(status_code=400, detail="Language already exists")
    
    # Add language
    new_language = Language(name=language_name)
    db.add(new_language)
    db.commit()
    db.refresh(new_language)

    print(f"Successfully added language: {language_name}")
    return {"msg": "Language added successfully"}

async def delete_language(language_name: str, username: str, token: str, db: Session):
    """
    Delete a language from the database
    
    Args:
        language_name: Name of the language to delete
        username: Username of the user making the request
        token: Authentication token
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not authorized, language not found, or other error occurs
    """
    try:
        # Check if token is valid
        try:
            name = await verify_token(token)
        except HTTPException as e:
            raise e
        
        # Check if token username matches requested username
        if name != username:
            print("Token username does not match requested username")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this Language"
            )
        
        # Check if language exists
        language = db.query(Language).filter(Language.name == language_name).first()

        if not language:
            print(f"Language '{language_name}' not found")
            raise HTTPException(status_code=404, detail="Language not found")
        
        # Delete language
        db.delete(language)
        db.commit()
        
        print(f"Successfully deleted language: {language_name}")
        return {"msg": "Language deleted successfully"}
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"Error deleting language '{language_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the language: {str(e)}"
        )