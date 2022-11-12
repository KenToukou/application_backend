
from datetime import timedelta
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import crud, schemas
from api.auth import (authenticate_user, create_access_token,
                      get_current_active_user, get_current_user, oauth2_scheme)
from api.database import SessionLocal, engine, get_db

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
@app.get("/auth/logout")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.post("/token")
async def login(db: Session = Depends(get_db),
                form_data: OAuth2PasswordRequestForm = Depends()):
    print("hello !")
    print(form_data.username)
    print(form_data.password)

    user = authenticate_user(db, form_data.username, form_data.password)
    print(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("Congratulation")
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer", "Create": "Now"}
    # ここでusernameをキーにして、DBのUsersから該当のユーザーを取得し、
    # パスワードが一致しているかチェックする.一致していなかった場合は400 BadRequestを返す

    # 一致していた場合は、アクセストークンを生成して下記のaccess_tokenフィールドでトークンを返す

    # return {"access_token": "", "token_type": "Bearer"}


@app.get("/view_token")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/current_user", response_model=schemas.UserCreate)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


# @app.get("/Current_User", response_model=schemas.UserSelect)
# async def read_users_me(current_user: schemas.UserSelect = Depends(get_current_active_user)):
#     print("Missin completed")
#     return current_user


@app.get("/users", response_model=List[schemas.UserSelect])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users", response_model=schemas.UserSelect)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name,)

    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_user(db=db, user=user)


@app.post("/add_hashed_password", response_model=schemas.UserSelect)
def add_hashed_password(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles


@app.patch("/articles/{article_id}", response_model=schemas.ArticleSelect)
def update_article(
    article_id: int, article: schemas.ArticleUpdate, db: Session = Depends(get_db)
):
    return crud.update_article(db=db, article_id=article_id, article=article)


@app.patch("/users/{user_id}", response_model=schemas.UserSelect)
def update_password(
    user_id: int, hashed_password: schemas.PasswordUpdate, db: Session = Depends(get_db)
):
    return crud.add_hashed_password(db=db, user_id=user_id, password=hashed_password)


@app.put("/articles/{article_id}", response_model=schemas.ArticleSelect)
def add_confirmed_user(
    article_id: int, user: schemas.AddConfirmedUser, db: Session = Depends(get_db)
):
    return crud.add_confirmed_user(db=db, article_id=article_id, user_id=user.user_id)


@app.post("/users/{user_id}/articles", response_model=schemas.ArticleSelect)
def add_article(
    user_id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db)
):
    return crud.create_article(db=db, article=article, user_id=user_id)
