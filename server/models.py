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
    
    def __setattr__(self, key, value):
        print(f"DBUser.__setattr__: {key} = {value}")
        super().__setattr__(key, value)
    
    def __init__(self, **kwargs):
        print(f"DBUser.__init__ with args: {kwargs}")
        super().__init__(**kwargs)

class Token(UsersBase):
    __tablename__ = "tokens"
    __table_args__ = {'extend_existing': True}
    
    token = Column(String, primary_key=True, index=True)
    expires = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))

# Language-related models (stored in languages.db)
class Language(LanguagesBase):
    __tablename__ = "languages"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, index=True)  # Track who created the language