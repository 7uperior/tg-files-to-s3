"""This module is concerned with creating models used for both table creation and data validation.

The classes with `table=True` are used to define tables that will be created in the database.

The rest of the classes are used for schema validation: They are used to control what data the api
endpoints can receive and return. If the data doesn't match the schema at either end of the api journey
then an error will occur.

**Note** : Plain SQLModels effectively act as Pydantic Models
"""

from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)


class User(UserBase, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=False)


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    created_at: datetime


class UserLogin(UserCreate):
    pass


class Token(SQLModel):
    access_token: str
    token_type: str
