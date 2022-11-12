from typing import List, Optional

from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime


class BaseModel(PydanticBaseModel):
    class Config:
        extra = 'forbid'


class Token(BaseModel):
    access_token: str
    token_type: str


class ArticleCreate(BaseModel):
    title: str
    content: Optional[str] = None


class ArticleUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class PasswordUpdate(BaseModel):
    hashed_password: str


class UserCreate(BaseModel):
    name: str
    hashed_password: Optional[str]


class UserSelect(BaseModel):
    id: int
    name: str
    hashed_password: Optional[str]
    created_at: datetime
    update_at: datetime
    # disabled: Union[bool, None]

    class Config:
        orm_mode = True


class UserName(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ArticleSelect(BaseModel):
    id: int
    user_id: int
    title: str
    content: Optional[str]
    created_at: datetime
    update_at: datetime
    user: UserName
    confirmed_users: List[UserName]

    class Config:
        orm_mode = True


class AddConfirmedUser(BaseModel):
    user_id: int
