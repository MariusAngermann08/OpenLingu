from fastapi import HTTPException
from sqlalchemy.orm import Session

# Import from server modules
try:
    from server.database import get_users_db
    from server.models import DBUser
    from server.services.token_service import verify_token
except ImportError:
    # Fall back to direct imports when running directly
    from database import get_users_db
    from models import DBUser
    from services.token_service import verify_token


async def get_user_profile(username: str, token: str, db: Session = None):
    """
    Get user profile information
    
    Args:
        username: The username of the user to retrieve
        token: Authentication token
        db: Optional database session. If not provided, a new one will be created.
        
    Returns:
        dict: User profile information
        
    Raises:
        HTTPException: If user is not authorized, not found, or other error occurs
    """
    close_db = False
    try:
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
            close_db = True
            
        # Check if token is valid and matches the username
        try:
            token_username = await verify_token(token, db)
        except HTTPException as e:
            raise e
        
        # Check if given username matches token username
        if token_username != username:
            print("Token username does not match requested username")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this User"
            )
        
        # Get user from database
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
        raise e
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving user data"
        )
    finally:
        if close_db and 'db' in locals():
            db.close()

async def delete_user(username: str, token: str, db: Session = None):
    """
    Delete a user
    
    Args:
        username: The username of the user to delete
        token: Authentication token
        db: Optional database session. If not provided, a new one will be created.
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not authorized, not found, or other error occurs
    """
    close_db = False
    try:
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
            close_db = True
            
        # Check if token is valid and matches the username
        try:
            token_username = await verify_token(token, db)
        except HTTPException as e:
            raise e
        
        # Check if given username matches token username
        if token_username != username:
            print("Token username does not match requested username")
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this User"
            )
        
        # Get user from database
        user = db.query(DBUser).filter(DBUser.username == username).first()

        if not user:
            print(f"User '{username}' not found in database")
            raise HTTPException(status_code=404, detail="User not found")

        # Delete user
        await remove_user(username, token, db)
        print(f"Successfully deleted user: {username}")
        return {"message": "User deleted successfully"}
            
    except HTTPException as e:
        if 'db' in locals():
            db.rollback()
        raise e
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the user"
        )
    finally:
        if close_db and 'db' in locals():
            db.close()