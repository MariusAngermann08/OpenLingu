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


async def get_user_profile(username: str, requesting_username: str, db: Session = None):
    """
    Get user profile information
    
    Args:
        username: The username of the user to retrieve
        requesting_username: The username of the user making the request
        db: Optional database session. If not provided, a new one will be created.
        
    Returns:
        dict: User profile information including roles
        
    Raises:
        HTTPException: If user is not found or other error occurs
    """
    close_db = False
    try:
        # Get database session if not provided
        if db is None:
            db = next(get_users_db())
            close_db = True
            
        # Get user from database
        user = db.query(DBUser).filter(DBUser.username == username).first()

        if not user:
            print(f"User '{username}' not found in database")
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )

        print(f"Successfully retrieved user: {username}")
        
        # Determine if the requesting user is an admin
        requesting_user = db.query(DBUser).filter(DBUser.username == requesting_username).first()
        is_admin = requesting_user and getattr(requesting_user, "is_admin", False)
        
        # Prepare user data
        user_data = {
            "username": user.username, 
            "email": user.email,
            "is_contributor": getattr(user, "is_contributor", False),
            "is_admin": getattr(user, "is_admin", False),
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        # Add additional admin-only fields if the requesting user is an admin
        if is_admin:
            user_data.update({
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": getattr(user, "is_active", True)
            })
            
        return user_data
            
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

async def delete_user(username: str, requesting_username: str, db: Session = None):
    """
    Delete a user (admin only)
    
    Args:
        username: The username of the user to delete
        requesting_username: The username of the admin making the request
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
            
        # Verify the requesting user is an admin
        admin_user = db.query(DBUser).filter(DBUser.username == requesting_username).first()
        if not admin_user or not getattr(admin_user, "is_admin", False):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to delete users"
            )
            
        # Prevent admins from deleting themselves
        if username == requesting_username:
            raise HTTPException(
                status_code=400,
                detail="Admins cannot delete their own accounts"
            )
        
        # Get user from database
        user = db.query(DBUser).filter(DBUser.username == username).first()

        if not user:
            print(f"User '{username}' not found in database")
            raise HTTPException(
                status_code=404, 
                detail="User not found"
            )

        try:
            # Delete the user
            db.delete(user)
            db.commit()
            print(f"Successfully deleted user: {username}")
            return {
                "status": "success",
                "message": f"User '{username}' deleted successfully"
            }
        except Exception as e:
            db.rollback()
            print(f"Error deleting user from database: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting user from database: {str(e)}"
            )
            
    except HTTPException as e:
        if 'db' in locals() and db.is_active:
            db.rollback()
        raise e
    except Exception as e:
        if 'db' in locals() and db.is_active:
            db.rollback()
        print(f"Error in delete_user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the user: {str(e)}"
        )
    finally:
        if close_db and 'db' in locals() and db.is_active:
            db.close()