from fastapi import HTTPException, status
from sqlalchemy.orm import Session

try:
    # When running from project root via run.py
    from server.models import Language, Lection
    from server.services.token_service import verify_token
except ImportError:
    # When running directly from server directory
    from models import Language, Lection
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

async def get_languages_list(db: Session):
    """
    Get a list of all languages in the database
    
    Args:
        db: Database session
        
    Returns:
        list: List of language names
    """
    try:
        languages = db.query(Language).all()
        return [language.name for language in languages]
    except Exception as e:
        print(f"Error getting languages list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the languages list: {str(e)}"
        )

async def add_lection(language_name: str, lection_name: str, username: str, token: str, content: dict, db: Session):
    """
    Add a new lection to the database
    
    Args:
        language_name: Name of the language to add the lection to
        lection_name: Name of the lection to add
        username: Username of the user making the request
        token: Authentication token
        content: The JSON content of the lection
        db: Database session
        
    Returns:
        dict: Success message and lection ID
        
    Raises:
        HTTPException: If user is not authorized, lection already exists, or content is invalid JSON
    """
    from datetime import datetime
    # content is now a dict; no need to parse or serialize
    # Check if language exists
    try:
        language = db.query(Language).filter(Language.name == language_name).first()
        if not language:
            print(f"Language '{language_name}' not found")
            raise HTTPException(status_code=404, detail="Language not found")
    except Exception as e:
        print(f"Error getting language '{language_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the language: {str(e)}"
        )
    
    # Verify token
    try:
        name = await verify_token(token)
        if name != username:
            print("Token username does not match requested username")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to add this Lection"
            )
    except HTTPException as e:
        raise e
    
    # Check if lection already exists
    existing_lection = db.query(Lection).filter(Lection.title == lection_name).first()
    if existing_lection:
        print(f"Lection '{lection_name}' already exists")
        raise HTTPException(status_code=400, detail="Lection already exists")

    # Add lection
    try:
        import uuid
        # Generate a unique ID for the lection
        lection_id = str(uuid.uuid4())
        new_lection = Lection(
            id=lection_id,
            title=lection_name, 
            language=language_name, 
            created_by=username, 
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.add(new_lection)
        db.commit()
        db.refresh(new_lection)
        
        print(f"Successfully added lection: {lection_name}")
        return {
            "msg": "Lection added successfully",
            "lection_id": new_lection.id
        }
    except Exception as e:
        db.rollback()
        print(f"Error adding lection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding lection: {str(e)}"
        )

async def edit_lection(language_name: str, lection_name: str, username: str, token: str, content: dict, db: Session):
    """
    Edit a lection in the database
    
    Args:
        language_name: Name of the language to edit the lection in
        lection_name: Name of the lection to edit
        username: Username of the user making the request
        token: Authentication token
        content: The content of the lection
        db: Database session
        
    Returns:
        dict: Success message and lection details
    """

    #Check if language exists
    try:
        language = db.query(Language).filter(Language.name == language_name).first()
    except Exception as e:
        print(f"Error getting language '{language_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the language: {str(e)}"
        )
    
    if not language:
        print(f"Language '{language_name}' not found")
        raise HTTPException(status_code=404, detail="Language not found")

    #Check if lection exists
    try:
        lection = db.query(Lection).filter(Lection.title == lection_name).first()
    except Exception as e:
        print(f"Error getting lection '{lection_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the lection: {str(e)}"
        )
    
    if not lection:
        print(f"Lection '{lection_name}' not found")
        raise HTTPException(status_code=404, detail="Lection not found")

    #Check if token username matches requested username
    try:
        name = await verify_token(token)
    except HTTPException as e:
        raise e
    
    if name != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code=403,
            detail="Not authorized to edit this Lection"
        )

    #Edit lection
    try:
        lection.content = content
        db.commit()
        db.refresh(lection)
        
        print(f"Successfully edited lection: {lection_name}")
        return {
            "msg": "Lection edited successfully",
            "lection_id": lection.id
        }
    except Exception as e:
        db.rollback()
        print(f"Error editing lection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error editing lection: {str(e)}"
        )

async def delete_lection(language_name: str, lection_name: str, username: str, token: str, db: Session):
    """
    Delete a lection from the database
    
    Args:
        language_name: Name of the language to delete the lection from
        lection_name: Name of the lection to delete
        username: Username of the user making the request
        token: Authentication token
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not authorized, lection not found, or other error occurs
    """

    #Check if language exists
    try:
        language = db.query(Language).filter(Language.name == language_name).first()
    except Exception as e:
        print(f"Error getting language '{language_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the language: {str(e)}"
        )
    
    if not language:
        print(f"Language '{language_name}' not found")
        raise HTTPException(status_code=404, detail="Language not found")
    
    #Check if lection exists
    try:
        lection = db.query(Lection).filter(Lection.title == lection_name).first()
    except Exception as e:
        print(f"Error getting lection '{lection_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while getting the lection: {str(e)}"
        )
    
    if not lection:
        print(f"Lection '{lection_name}' not found")
        raise HTTPException(status_code=404, detail="Lection not found")
    
    #Check if token username matches requested username
    try:
        name = await verify_token(token)
    except HTTPException as e:
        raise e
    
    if name != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this Lection"
        )
    
    #Delete lection
    db.delete(lection)
    db.commit()
    
    print(f"Successfully deleted lection: {lection_name}")
    return {"msg": "Lection deleted successfully"}