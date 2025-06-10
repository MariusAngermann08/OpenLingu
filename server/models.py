from sqlalchemy import Boolean, Column, String, DateTime, Table, MetaData
from datetime import datetime, timedelta

try:
    # Try absolute imports first (when running as a module)
    from .database import UsersBase, LanguagesBase
except ImportError:
    # Fall back to relative imports (when running directly)
    from database import UsersBase, LanguagesBase

# Suppress SAWarning for declarative base
import warnings
from sqlalchemy import exc as sa_exc
warnings.filterwarnings('ignore', category=sa_exc.SAWarning, module='sqlalchemy')

# User-related models (stored in users.db)
class DBUser(UsersBase):
    __tablename__ = "users"
    
    # This prevents the SAWarning about duplicate class names
    if not hasattr(UsersBase, '_decl_class_registry'):
        _decl_class_registry = {}
        
    __abstract__ = False  # Make sure it's not treated as abstract
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
    expires = Column(DateTime)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires:
            self.expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# Language-related models (stored in languages.db)
class Language(LanguagesBase):
    __tablename__ = "languages"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, index=True)  # Track who created the language