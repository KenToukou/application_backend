
from datetime import timedelta
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends, FastAPI, HTTPException, status,Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from enum import Enum
from api import crud, schemas, auth
from api.auth import (authenticate_user, create_access_token,
                      create_refresh_token, get_current_user, oauth2_scheme)
from api.database import SessionLocal, engine, get_db

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


class ModelName(str, Enum):
    username = "username"
    password = "password"


origins = [

    "http://localhost:51156",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["POST", "GET", "OPTIONS", "DELETE"],
#     allow_headers={"X-Requested-With", "Origin",
#                    "X-Csrftoken", "Content-Type", "Accept"},

# )


@app.get("/auth/logout")
async def read_master(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.post("/token")
async def login(db: Session = Depends(get_db),
                form_data: OAuth2PasswordRequestForm = Depends()):
    print("Hello login")
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=2)
    print("Hello login02")
    if user.id ==1:
        scope_list:list = ["common","master"]
    else: 
        scope_list:list = ["common"]
    access_token = create_access_token(
        data={"sub": user.name,"scopes":scope_list}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.name,"scopes":scope_list}, expires_delta=refresh_token_expires)
    print("Hello login 03")
    user_info = crud.get_user_by_name(db, form_data.username)
    user_info_id = user_info.id
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user_id": str(user_info_id)}
    # ここでusernameをキーにして、DBのUsersから該当のユーザーを取得し、
    # パスワードが一致しているかチェックする.一致していなかった場合は400 BadRequestを返す

    # 一致していた場合は、アクセストークンを生成して下記のaccess_tokenフィールドでトークンを返す

    # return {"access_token": "", "token_type": "Bearer"}


@app.get("/view_token")
async def read_items_token(token: str = Depends(oauth2_scheme),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])):
    if not current_user:
        return False
    return {"token": token}


@app.get("/current_user", response_model=schemas.UserCreate)
async def read_users_me(current_user=Depends(auth.get_current_active_user)):
    return current_user


# @app.get("/Current_User", response_model=schemas.UserSelect)
# async def read_users_me(current_user: schemas.UserSelect = Depends(get_current_active_user)):
#     print("Missin completed")
#     return current_user


@app.get("/users", response_model=List[schemas.UserSelect])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])):
    if not current_user:
        return False
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users", response_model=schemas.UserSelect)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])):
    if not current_user:
        return False
    
    db_user = crud.get_user_by_name(db, name=user.name,)

    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_user(db=db, user=user)


@app.post("/add_hashed_password", response_model=schemas.UserSelect)
def add_hashed_password(user: schemas.UserCreate, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])):
    if not current_user:
        return False
    db_password = crud.get_hashed_password_by_name(
        db, hashed_password=user.hashed_password)
    if db_password is not None:
        return
    return crud.create_user(db=db, user=user)

# @app.get("/users/{user_id}", response_model=schemas.UserSelect)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


@app.get("/articles", response_model=List[schemas.ArticleSelect])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user)):
    if not current_user:
        return False
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles


@app.patch("/articles/{article_id}", response_model=schemas.ArticleSelect)
def update_article(
    article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])
):
    if not current_user:
        return False
    return crud.update_article(db=db, article_id=article_id, article=article)


@app.patch("/users/{user_id}", response_model=schemas.UserSelect)
def update_password(
    user_id: int, hashed_password: schemas.PasswordUpdate, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user, scopes=["master"])
):
    if not current_user:
        return False
    return crud.add_hashed_password(db=db, user_id=user_id, password=hashed_password)


@app.put("/articles/{article_id}", response_model=schemas.ArticleSelect)
def add_confirmed_user(
    article_id: str, user: schemas.AddConfirmedUser, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user)
):
    if not current_user:
        return False
    return crud.add_confirmed_user(db=db, article_id=article_id, user_id=user.user_id)

# "PUT /articles/37 HTTP/1.1" 200 OK
# "PUT /articles/37 HTTP/1.1" 422 Unprocessable Entity


@app.post("/users/{user_id:int}/articles", response_model=schemas.ArticleSelect)
def add_article(
    user_id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db),current_user: schemas.UserSelect = Security(auth.get_current_active_user)
):
    if not current_user:
        return False
    return crud.create_article(db=db, article=article, user_id=user_id)
