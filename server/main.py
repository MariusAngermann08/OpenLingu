from fastapi import FastAPI, status, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

#Import Models
from models import *

#Import Parameters
from parameters import *

#Import authentication functions
from auth import *

#Import database
from database import db

#Used for password hashing
from passlib.context import CryptContext

app = FastAPI()


@app.get("/")
async def get():
    return {"msg": "OpenLingu"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return {"item_id": 1, "owner": current_user}
