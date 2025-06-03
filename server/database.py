from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

import os

# Get the absolute path to the database file
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'users.db')

URL_DATABASE = f"sqlite:///{os.path.abspath(DB_PATH)}"

LANGUAGE_DATABASE = f"sqlite:///{os.path.join(DB_DIR, 'languages.db')}"

engine = create_engine(URL_DATABASE)
language_engine = create_engine(LANGUAGE_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
language_session = sessionmaker(autocommit=False, autoflush=False, bind=language_engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_language_db() -> Generator[Session, None, None]:
    language_db = language_session()
    try:
        yield language_db
    finally:
        language_db.close()