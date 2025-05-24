from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str  # Store hashed password instead of plain text

#Create the users database
sqlite_file_name = "users.db"
#Put into database folder
sqlite_url = f"sqlite:///database/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
