from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import desc

from api import models, schemas,auth


def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == name).first()


def get_hashed_password_by_name(db: Session, hashed_password: str) -> models.User:
    return db.query(models.User).filter(models.User.hashed_password == hashed_password).first()


def get_user_by_id(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(
        models.User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User is not found.")
    return user


def get_article_by_id(db: Session, article_id: int) -> models.Article:
    article = db.query(models.Article).filter(
        models.Article.id == article_id).one_or_none()
    if article is None:
        raise HTTPException(status_code=404, detail="Article is not found.")
    return article


def get_users(db: Session, skip: int = 0, limit: int = 5):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        hashed_password= auth.get_password_hash(user.hashed_password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_articles(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.Article).order_by(desc(models.Article.id)).offset(skip).limit(limit).all()


def create_article(db: Session, article: schemas.ArticleCreate, user_id: int):
    db_article = models.Article(**article.dict(), user_id=user_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def add_confirmed_user(db: Session, article_id: str, user_id: str):
    db_article = get_article_by_id(db=db, article_id=int(article_id))
    new_confirmed_user = get_user_by_id(db=db, user_id=int(user_id))
    db_article.confirmed_users.append(new_confirmed_user)
    print(db_article.confirmed_users)
    db.merge(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(db: Session, article_id: int,
                   article: schemas.ArticleUpdate) -> models.Article:
    db_article = get_article_by_id(db, article_id=article_id)
    update_data = article.dict(exclude_unset=True)
    for key, val in update_data.items():
        setattr(db_article, key, val)
    db.merge(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def add_hashed_password(db: Session, user_id: int,
                        password: schemas.PasswordUpdate) -> models.User:
    db_user = get_user_by_id(db, user_id=user_id)
    update_data = password.dict(exclude_unset=True)
    for key, val in update_data.items():
        setattr(db_user, key, val)
    db.merge(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
