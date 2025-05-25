from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, String
from server.database import Base

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# SQLAlchemy models
class DBUser(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)