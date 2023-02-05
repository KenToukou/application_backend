import os

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

user = 'user'
password = 'password'
host = 'localhost'
db_name = 'manavis_db'
db_option = "charset=utf8mb4&collation=utf8mb4_general_ci"
db_pool_size = 10
db_max_overflow = 40
db_pool_recycle = 3600
db_pool_pre_ping = True

# DB_URL = f'mysql+mysqlconnector://{user}:{password}@{host}/{db_name}?{db_option}'
DB_URL = os.getenv("DB_URL", f'mysql+mysqlconnector://{user}:{password}@{host}/{db_name}')


# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = sqlalchemy.create_engine(
    f'{DB_URL}?{db_option}',
    
    echo=True,
    pool_size=db_pool_size,
    max_overflow=db_max_overflow,
    pool_recycle=db_pool_recycle,
    pool_pre_ping=db_pool_pre_ping
    
)

Base = sqlalchemy.ext.declarative.declarative_base()

SessionLocal = sqlalchemy.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
