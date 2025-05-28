from fastapi import HTTPException
from sqlalchemy.orm import Session

# Import from server modules
try:
    from server.database import get_db
    from server.models import DBUser
    from server.services.token_service import verify_token
except ImportError:
    # Fall back to direct imports when running directly
    from database import get_db
    from models import DBUser
    from services.token_service import verify_token


async def get_user_profile(username: str, token: str):
    #Check if token is valid and matches the username
    try:
        token_username = await verify_token(token)
    except HTTPException as e:
        raise e
    
    #Check if given username matches token username
    if token_username != username:
        print("Token username does not match requested username")
        raise HTTPException(
            status_code = 403,
            detail = "Not authorized to access this User"
        )
    
    #Get user from database
    try:
        db = next(get_db())
        user =  db.query(DBUser).filter(DBUser.username == username).first()

        if not user:
            print(f"User '{username}' not found in database")
            raise HTTPException(status_code=404, detail="User not found")

        print(f"Successfully retrieved user: {username}")
        return {
            "username": user.username, 
            "email": user.email
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving user data"
        )
    finally:
        if db:
            db.close()

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