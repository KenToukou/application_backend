from datetime import datetime, timedelta
from typing import Union
# from unicodedata import name

import hashlib
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return bool(plain_password == hashed_password)
    # return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hashed_password


class UserInDB(BaseModel):
    username: str
    hashed_password: str


def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.name == username).first()
    print(user.hashed_password)
    print(user.name)
    if username in user.name:

        return user.name
    else:
        print("Error")

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):

    search_user = db.query(models.User).filter(
        models.User.name == username).first()
    user = get_user(db, username)
    search_password = search_user.hashed_password
    hash_origin = get_password_hash(search_password)
    hash_request = get_password_hash(password)
    if not user:
        return False
    if not verify_password(hash_origin, hash_request):
        return False
    else:
        print("第二関門クリア！！")
    return user


class TokenData(BaseModel):
    username: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # 中身を見たければ、encoded_jwtをpirntして、https://jwt.io/ へアクセスしてトークンを貼り付けると確認できる。
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # 中身を見たければ、encoded_jwtをpirntして、https://jwt.io/ へアクセスしてトークンを貼り付けると確認できる。
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print("Mission start")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("first step")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[
                             ALGORITHM])  # decodeは値が等しいかどうかを参照して判断している。
        print(payload)
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        print("second step")
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    print(user, "問題なし")
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.UserSelect = Depends(get_current_user)
):
    print("Third step")
    print(current_user)
    if current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
