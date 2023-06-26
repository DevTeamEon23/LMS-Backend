from enum import Enum

from pydantic import BaseModel,validator
from typing import Union
from utils import validate_email

class query(str, Enum):
    category1 = 'category1'
    category2 = 'category2'
    category3 = 'category3'


class CategorySchema(BaseModel):
    email: str
    id: int
    category: query


class User(BaseModel):
    email: str
    fullname: Union[str, None] = None
    password: str

class DeleteUser(BaseModel):
    id: int

class Email(BaseModel):
    email: str

    @validator("email")
    def validate_email(cls, email):
        if validate_email(email):
            return email
        raise ValueError(f"Invalid field: {email}")


class UserStatus(Email):
    status: Union[str, None] = False


class UserPassword(Email):
    password: str = None