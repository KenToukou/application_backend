from sqlalchemy import (ForeignKey,
                        Column, Integer, String, DateTime)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base, SessionLocal, engine


class UserArticle(Base):
    __tablename__ = "users_articles"

    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'),
                        nullable=False, primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True, unique=True)
    hashed_password = Column(String(512), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    update_at = Column(DateTime, nullable=False,
                       default=datetime.now, onupdate=datetime.now)
    # disabled = False
    articles = relationship(
        "Article", back_populates="user", cascade='all, delete')
    confirmed_articles = relationship(
        'Article',
        secondary=UserArticle.__tablename__,
        back_populates='confirmed_users',
    )


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(128), nullable=False, index=True)
    content = Column(String(4096))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    update_at = Column(DateTime, nullable=False,
                       default=datetime.now, onupdate=datetime.now)
    user = relationship("User", back_populates="articles")
    confirmed_users = relationship(
        'User',
        secondary=UserArticle.__tablename__,
        back_populates='confirmed_articles',
    )


Base.metadata.create_all(engine)  # ここのコードめっちゃ大事!!!!!

###############################################################################
# <テスト>　　　　試しにmysqlにデータを保存してみる
# session = SessionLocal()
# user_1 = User(name="東光健", hashed_password='toko')
# session.add(user_1)
# session.commit()

# <確認しよーぜ>
# session = SessionLocal()
# persons = session.query(User).all()
# for person in persons:
#     print(person.name)
