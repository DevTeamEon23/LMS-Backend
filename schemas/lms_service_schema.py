from enum import Enum

from pydantic import BaseModel


class query(str, Enum):
    category1 = 'category1'
    category2 = 'category2'
    category3 = 'category3'


class CategorySchema(BaseModel):
    email: str
    id: int
    category: query
