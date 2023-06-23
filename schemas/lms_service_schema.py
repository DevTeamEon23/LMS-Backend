from enum import Enum

from pydantic import BaseModel
from typing import Union

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
