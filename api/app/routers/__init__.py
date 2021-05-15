from redis import Redis
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, Dict, List
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
import os

redis_pass = os.getenv("REDIS_PASS")
r = Redis(host='redis', port=6379, db=0, password=redis_pass)
mongodb_user = os.getenv("MONGODB_USER")
mongodb_pass = os.getenv("MONGODB_PASS")
mongo = MongoClient(host='mongodb',
                    port=27017,
                    username=mongodb_user,
                    password=mongodb_pass)

db = mongo.secure_code_platform
users = db.users
challenges = db.challenges
categories = db.categories
tags = db.tags

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
roles = ('admin', 'editor', 'user')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str
    expiration_time: datetime


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str]
    full_name: Optional[str]
    sex: Optional[int]
    disabled: Optional[bool]
    user_role: str = 'user'
    avatar_path: str = ''
    created_at: str = ''
    modified_at: str = ''


class UserInDB(User):
    password: str





class Tag(BaseModel):
    tag_name: str
    tag_class: str


class Category(BaseModel):
    category_name: str


def get_user(username: str):
    if username in [user['username'] for user in db.users.find({})]:
        user_dict = users.find_one({'username': username}, {'_id': False})
        return UserInDB(**user_dict)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_if_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_role != 'admin':
        raise HTTPException(status_code=403, detail="Non admin user")
    return current_user


async def get_current_user_if_editor(current_user: User = Depends(get_current_user)):
    if current_user.user_role not in ('editor', 'admin'):
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user
