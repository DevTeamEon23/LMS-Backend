import traceback
import shutil
import json
import routers.lms_service.lms_service_ops as model
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends,UploadFile, File,Form
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from config.db_config import SessionLocal,n_table_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,delete_user_by_id,change_user_details,add_new,fetch_all_courses_data,delete_course_by_id,add_course,add_group,fetch_all_groups_data,delete_group_by_id,change_course_details
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,Users, UserDetail,DeleteCourse,DeleteGroup)
from utils import success_response
from config.logconfig import logger

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])


@service.post("/list-data")
def get_list_data(payload:CategorySchema):
    return success_response(status_code=status.HTTP_200_OK, data=sample_data(payload))

# Create User
@service.post('/addusers')
async def create_user(eid: str = Form(...),sid: str = Form(...), full_name: str = Form(...), email: str = Form(...),dept: str = Form(...), adhr: str = Form(...), username: str = Form(...), password: str = Form(...),bio: str = Form(...), role: str = Form(...), timezone: str = Form(...), langtype: str = Form(...), active: bool = Form(...), deactive: bool = Form(...), exclude_from_email: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...)):
    with open("media/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = str("media/"+file.filename)
    try:
        return add_new(email,generate_token,password=password, auth_token="", inputs={
                'eid': eid,'sid': sid,'full_name': full_name,'email': email, 'dept': dept, 'adhr': adhr,'username': username,'bio': bio,'file': url,'role': role, 'timezone': timezone, 'langtype': langtype,'users_allowed': '[]', 'active': active, 'deactive': deactive, 'exclude_from_email': exclude_from_email, 'picture': "", "password": None})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User registration failed"
        })

# Read Users list
@service.get("/users")
def fetch_all_users():
    try:
        # Fetch all users' data here
        users = fetch_all_users_data()

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch users' data"
        })
    
# Update users
# @service.post("/update_users")
# def update_users(id: int = Form(...),eid: str = Form(...),sid: str = Form(...), full_name: str = Form(...), email: str = Form(...),dept: str = Form(...), adhr: str = Form(...), username: str = Form(...), password: str = Form(...),bio: str = Form(...), role: str = Form(...), timezone: str = Form(...), langtype: str = Form(...), active: bool = Form(...), deactive: bool = Form(...), exclude_from_email: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...)):
#     with open("media/"+file.filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     url = str("media/"+file.filename)
#     try:
#         return change_user_details(id,email,langtype,generate_token,password, auth_token="", inputs={
#                 'id': id,'eid': eid,'sid': sid,'full_name': full_name,'email': email, 'dept': dept, 'adhr': adhr,'username': username,'bio': bio,'file': url,'role': role, 'timezone': timezone, 'langtype': langtype,'users_allowed': '[]', 'active': active, 'deactive': deactive, 'exclude_from_email': exclude_from_email, 'picture': "", "password": None})
#             # return JSONResponse(status_code=status.HTTP_200_OK, content={
#             #     "status": "success",
#             #     "message": "Updated Course successfully"
#             # })
#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
#             "status": "failure",
#             "message": exc.args[0]
#         })

@service.post("/update_users")
def update_users(id: int = Form(...),eid: str = Form(...),sid: str = Form(...), full_name: str = Form(...), email: str = Form(...),dept: str = Form(...), adhr: str = Form(...), username: str = Form(...), password: str = Form(...),bio: str = Form(...), role: str = Form(...), timezone: str = Form(...), langtype: str = Form(...), active: bool = Form(...), deactive: bool = Form(...), exclude_from_email: bool = Form(...),file: UploadFile = File(...)):
    with open("media/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file = str("media/"+file.filename)
    try:
        if change_user_details(id, eid, sid, full_name, dept, adhr, username, email, password, bio, file, role, timezone, langtype, active, deactive, exclude_from_email):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated User successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
# Delete USER
@service.delete("/delete_user")
def delete_user(payload: DeleteUser):
    try:
        users = delete_user_by_id(payload.id)
        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete user data"
        })
    

##########################################################

# Create Course
@service.post('/addcourses')
async def create_course(coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(...), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(...)):
    with open("course/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = str("course/"+file.filename)
    with open("coursevideo/"+coursevideo.filename, "wb") as buffer:
        shutil.copyfileobj(coursevideo.file, buffer)
    urls = str("coursevideo/"+coursevideo.filename)
    try:
        return add_course(coursename,coursevideo,generate_token, auth_token="", inputs={
                'coursename': coursename, 'description': description,'coursecode': coursecode,'price': price, 'courselink': courselink, 'capacity': capacity,'startdate': startdate,'enddate': enddate,'timelimit': timelimit,'file': url,'certificate': certificate, 'level': level, 'category': category, 'coursevideo': urls,'course_allowed': '[]', 'isActive': isActive, 'isHide': isHide, 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Course registration failed"
        })
    
# Read Users list
@service.get("/courses")
def fetch_all_courses():
    try:
        # Fetch all users' data here
        courses = fetch_all_courses_data()

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch courses' data"
        })

@service.post("/update_courses")
def update_courses(id: int = Form(...),coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(...), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(...)):
    with open("media/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file = str("media/"+file.filename)
    with open("coursevideo/"+coursevideo.filename, "wb") as buffer:
        shutil.copyfileobj(coursevideo.file, buffer)
    coursevideo = str("coursevideo/"+coursevideo.filename)

    try:
        if change_course_details(id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Course successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_course")
def delete_course(payload: DeleteCourse):
    try:
        courses = delete_course_by_id(payload.id)
        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete course data"
        })
    
############################################################

# Create Group
@service.post('/addgroups')
async def create_group(groupname: str = Form(...),groupdesc: str = Form(...), groupkey: str = Form(...), isActive: bool = Form(...),generate_token: bool = Form(...)):
    try:
        return add_group(generate_token, auth_token="", inputs={
                'groupname': groupname, 'groupdesc': groupdesc, 'groupkey': groupkey, 'group_allowed': '[]', 'isActive': isActive ,'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Group registration failed"
        })
    
# Read Group list
@service.get("/groups")
def fetch_all_groups():
    try:
        # Fetch all groups' data here
        groups = fetch_all_groups_data()

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch groups' data"
        })
    
@service.delete("/delete_group")
def delete_group(payload: DeleteGroup):
    try:
        groups = delete_group_by_id(payload.id)
        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete group data"
        })

##########################################################

