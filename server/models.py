from sqlalchemy import Boolean, Column, String, DateTime, Table, MetaData
from datetime import datetime, timedelta

try:
    # Try absolute imports first (when running as a module)
    from server.database import UsersBase, LanguagesBase, users_metadata, languages_metadata
except ImportError:
    # Fall back to relative imports (when running directly)
    from database import UsersBase, LanguagesBase, users_metadata, languages_metadata

# User-related models (stored in users.db)
class DBUser(UsersBase):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

class Token(UsersBase):
    __tablename__ = "tokens"
    __table_args__ = {'extend_existing': True}
    
    token = Column(String, primary_key=True, index=True)
    expires = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    username = Column(String, index=True)  # Add username to track token ownership

# Language-related models (stored in languages.db)
class Language(LanguagesBase):
    __tablename__ = "languages"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, index=True)  # Track who created the language