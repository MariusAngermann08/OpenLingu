from sqlalchemy import Boolean, Column, String, DateTime

from datetime import datetime, timedelta

try:
    # Try absolute imports first (when running as a module)
    from server.database import Base
except ImportError:
    # Fall back to relative imports (when running directly)
    from database import Base




# SQLAlchemy models
class DBUser(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, index=True)
    expires = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))

class Language(Base):
    __tablename__ = "languages"
    name = Column(String, primary_key=True, index=True)