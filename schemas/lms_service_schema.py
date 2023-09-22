from enum import Enum

from pydantic import BaseModel,validator
from typing import List,Union, Optional
from utils import validate_email

class query(str, Enum):
    category1 = 'category1'
    category2 = 'category2'
    category3 = 'category3'

class Role(str, Enum):
    Superadmin = 'Superadmin'
    Admin = 'Admin'
    Instructor = 'Instructor'
    Learner = 'Learner'

class Timezone(str, Enum):
    IST = 'IST'
    NST = 'NST'
    AST = 'AST'
    ECT = 'ECT'
    GMT = 'GMT'
    ARABIC = 'ARABIC'

class Langtype(str, Enum):
    English = 'English'
    Hindi = 'Hindi'
    Marathi = 'Marathi'


class CategorySchema(BaseModel):
    email: str
    id: int
    category: query


# class LocalUser(BaseModel):


class AddUser(BaseModel):
    eid: str
    sid: str
    full_name: Union[str, None] = None
    email: str
    dept: str
    adhr: int
    username: str
    password: str
    bio: str
    file: bytes
    role: Role
    timezone: Timezone
    langtype: Langtype
    active: bool = True
    deactive: bool = False
    exclude_from_email: bool = False

class Users(AddUser):
    generate_token: bool


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


class UserDetail(BaseModel):
    id: int
    eid: str
    sid: str
    full_name: Union[str, None] = None
    email: str
    dept: str
    adhr: int
    username: str
    password: str
    bio: str
    file: Optional[bytes] = None
    role: Role
    timezone: Timezone
    langtype: Langtype
    active: bool = True
    deactive: bool = False
    exclude_from_email: bool = False

####################                    Courses                    ##############################

class DeleteCourse(BaseModel):
    id: int

####################                    Groups                     ##############################

class DeleteGroup(BaseModel):
    id: int

####################                    Category                     ##############################

class DeleteCategory(BaseModel):
    id: int

####################                    Event                     ##############################

class DeleteEvent(BaseModel):
    id: int

####################                    Classroom                     ##############################

class DeleteClassroom(BaseModel):
    id: int

####################                    Conference                     ##############################

class DeleteConference(BaseModel):
    id: int

####################                    Virtual Training                     ##############################

class DeleteVirtual(BaseModel):
    id: int

####################                    Discussion                     ##############################

class DeleteDiscussion(BaseModel):
    id: int

####################                    Calender                     ##############################

class DeleteCalender(BaseModel):
    id: int
    
##################################### Unenroll Users from course #############################################

class UnenrolledUsers_Course(BaseModel):
    id: int

##################################### Unenroll Users from group #############################################

class UnenrolledUsers_Group(BaseModel):
    id: int

##################################### Unenroll course from group #############################################

class UnenrolledCourse_Group(BaseModel):
    id: int

##################################### Remove file by id #############################################

class Remove_file(BaseModel):
    id: int

####################                    Course Content                     ##############################

class DeleteCourseContent(BaseModel):
    id: int
