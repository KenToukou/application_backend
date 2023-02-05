from datetime import datetime, timedelta
from typing import Union, List
# from unicodedata import name
from passlib.context import CryptContext
# import hashlib
from pydantic import ValidationError
from sqlalchemy.orm import Session
from api import models, schemas
from api.database import get_db
from fastapi import Depends, HTTPException, status,Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return  pwd_context.verify(plain_password, hashed_password)
    # return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    # hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    #hashed_password
    return pwd_context.hash(password)





def get_user(db: Session, username: str):
    print("Userはどこだ")
    user = db.query(models.User).filter(models.User.name == username).first()
    print("結果：",user.hashed_password)
    print(user.name)
    if username in user.name:

        return user
   

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):

    print("OK???")
    user = get_user(db, username)
    search_password = user.hashed_password
    print("database:",search_password)
    print(password)
    # hash_origin = get_password_hash(search_password)
   
    if not user:
        return False
    if not verify_password(password, search_password):
        return False
    else:
        print("第二関門クリア！！")
    return user

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


async def get_current_user(security_scopes: SecurityScopes,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
       
        payload = jwt.decode(token, SECRET_KEY, algorithms=[
                             ALGORITHM])  # decodeは値が等しいかどうかを参照して判断している。
        print("payload:",payload)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])# 右の[]で型が決まる
        token_data = schemas.TokenData(scopes=token_scopes,username=username)
        
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    print(user, "問題なし")
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes: #security_scopes に保存されているリスト（scopes)の中のscopeと同じscopeがあるかそうか探している。
        if scope not in token_data.scopes: #1個づつ取り出してゆき、その都度、対象のリストの中に値が存在するのかを確認する。
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: schemas.UserSelect = Security(get_current_user, scopes=["common"])
):
    if current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
