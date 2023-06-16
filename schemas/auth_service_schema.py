from typing import Union

from fastapi import Header, HTTPException

from pydantic import BaseModel, validator

from utils import validate_email
from typing import Union


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    email: str
    fullname: Union[str, None] = None
    password: str
    role: str


class NewUser(User):
    generate_token: bool


class Mfa(BaseModel):
    request_token: str
    pin_mfa: Union[str, None] = None


class GoogleCredential(BaseModel):
    credential: str
    clientId: str
    select_by: str


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
