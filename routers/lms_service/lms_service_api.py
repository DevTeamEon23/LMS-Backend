import traceback
import shutil
import json
import time
import os
import base64
import pandas as pd
import subprocess
from zipfile import ZipFile
from PIL import Image
from io import BytesIO
import routers.lms_service.lms_service_ops as model
from fastapi.responses import JSONResponse,HTMLResponse,FileResponse
from fastapi import APIRouter, Depends,UploadFile, File,Form, Query,HTTPException
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from config.db_config import SessionLocal,n_table_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,fetch_users_by_onlyid,delete_user_by_id,change_user_details,add_new,fetch_all_courses_data,fetch_active_courses_data,delete_course_by_id,add_course,add_group,fetch_all_groups_data,delete_group_by_id,change_course_details,change_group_details,add_category,fetch_all_categories_data,change_category_details,delete_category_by_id,add_event,fetch_all_events_data,change_event_details,delete_event_by_id,fetch_category_by_onlyid,fetch_course_by_onlyid,fetch_group_by_onlyid,fetch_event_by_onlyid,add_classroom,fetch_all_classroom_data,fetch_classroom_by_onlyid,change_classroom_details,delete_classroom_by_id,add_conference,fetch_all_conference_data,fetch_conference_by_onlyid,change_conference_details,delete_conference_by_id,add_virtualtraining,fetch_all_virtualtraining_data,fetch_virtualtraining_by_onlyid,change_virtualtraining_details,delete_virtualtraining_by_id,add_discussion,fetch_all_discussion_data,fetch_discussion_by_onlyid,change_discussion_details,delete_discussion_by_id,add_calender,fetch_all_calender_data,fetch_calender_by_onlyid,change_calender_details,delete_calender_by_id,add_new_excel,clone_course,enroll_course,enroll_group,check_existing_user,enroll_coursegroup
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,Users, UserDetail,DeleteCourse,DeleteGroup,DeleteCategory,DeleteEvent,DeleteClassroom,DeleteConference,DeleteVirtual,DeleteDiscussion,DeleteCalender)
from utils import success_response
from config.logconfig import logger

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])

# Variable to store the path of the latest extracted folder
latest_extracted_folder = None


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


# Create User via excel
@service.post('/addusers_excel')
async def create_users_from_excel(file: UploadFile = File(...)):
    try:
        # Create a temporary file to save the uploaded content
        temp_file_path = "users.xlsx"
        with open(temp_file_path, "wb") as temp_file:
            while content := await file.read(1024):
                temp_file.write(content)

        # Read the uploaded Excel file using pandas (defaulting to the first sheet)
        df = pd.read_excel(temp_file_path)
        
        # Process and insert the data from the DataFrame
        for _, row in df.iterrows():
            # Assuming your data is in the same order as column names in the DataFrame
            data = {
                'eid': row['eid'],
                'sid': row['sid'],
                'full_name': row['full_name'],
                'email': row['email'],
                'dept': row['dept'],
                'adhr': row['adhr'],
                'username': row['username'],
                'password': row['password'],
                'bio': row['bio'],
                'role': row['role'],
                'timezone': row['timezone'],
                'langtype': row['langtype'],
                'active': row['active'],
                'deactive': row['deactive'],
                'exclude_from_email': row['exclude_from_email'],
                'generate_token': row['generate_token']
            }
            
            # Call your add_new function with the data
            add_new_excel(row['email'], password=row['password'], auth_token="", inputs=data)

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": "Users added successfully from the Excel file."
        })
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to process the Excel file."
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

#Get User data by id for update fields Mapping
@service.get("/users_by_onlyid")
def fetch_user_by_onlyid(id):
    try:
        # Fetch all users' data here
        users = fetch_users_by_onlyid(id)

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

###################################################################################################################

# Create enroll_course
@service.post('/enroll_course')
async def enroll_course_user(user_id: int = Form(...),course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_course(user_id,generate_token, auth_token="", inputs={
                'user_id': user_id,'course_id': course_id,'enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User enrolled to course failed"
        })

###################################################################################################################

# Create enroll_group
@service.post('/enroll_group')
async def enroll_group_user(user_id: int = Form(...),group_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_group(user_id,generate_token, auth_token="", inputs={
                'user_id': user_id,'group_id': group_id,'enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User enrolled to group failed"
        })
    
###################################################################################################################

# Create enroll_course_group
@service.post('/enroll_course_group')
async def enroll_course_group(course_id: int = Form(...),group_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_coursegroup(course_id,generate_token, auth_token="", inputs={
                'course_id': course_id,'group_id': group_id,'cr_grp_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "course enrolled to group failed"
        })
    
############################################################################################################################

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


@service.post('/clonecourse/{id}')
async def clone_course_endpoint(id: int):
    try:
        return clone_course(id)
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Course Cloning failed"
        })

# Read All Courses list
@service.get("/courses")
def fetch_all_courses():
    try:
        # Fetch all courses data here
        courses = fetch_all_courses_data()

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all courses' data"
        })

# Read Active Courses list
@service.get("/active_courses")
def fetch_active_courses():
    try:
        # Fetch all active courses data here
        courses = fetch_active_courses_data()

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch active courses' data"
        })
    
#Get Courses data by id for update fields Mapping
@service.get("/courses_by_onlyid")
def fetch_courses_by_onlyid(id):
    try:
        # Fetch all course's data here
        courses = fetch_course_by_onlyid(id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch course's data"
        }) 
    
@service.post("/update_courses")
def update_courses(id: int = Form(...),coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(...), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(...)):
    with open("course/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file = str("course/"+file.filename)
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
    
############################################################################################################################

# Create Group
@service.post('/addgroups')
async def create_group(groupname: str = Form(...),groupdesc: str = Form(...), groupkey: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_group(generate_token, auth_token="", inputs={
                'groupname': groupname, 'groupdesc': groupdesc, 'groupkey': groupkey, 'group_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Group registration failed Alreadly Exists"
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

#Get Group data by id for update fields Mapping
@service.get("/groups_by_onlyid")
def fetch_groups_by_onlyid(id):
    try:
        # Fetch all group's data here
        groups = fetch_group_by_onlyid(id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch group's data"
        }) 
    
@service.post("/update_groups")
def update_groups(id: int = Form(...),groupname: str = Form(...),groupdesc: str = Form(...), groupkey: str = Form(...)):
    try:
        if change_group_details(id, groupname, groupdesc, groupkey):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Group successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
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

######################################################################################################################

# Create Group
@service.post('/addcategories')
async def create_category(name: str = Form(...),price: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_category(name,generate_token, auth_token="",inputs={
                'name': name, 'price': price,'category_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Category registration failed Category Alreadly Exists"
        })
    
# Read Group list
@service.get("/categories")
def fetch_all_categories():
    try:
        # Fetch all categories' data here
        categories = fetch_all_categories_data()

        return {
            "status": "success",
            "data": categories
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch categories' data"
        })

#Get User data by id for update fields Mapping
@service.get("/categories_by_onlyid")
def fetch_categories_by_onlyid(id):
    try:
        # Fetch all users' data here
        categories = fetch_category_by_onlyid(id)

        return {
            "status": "success",
            "data": categories
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch category's data"
        }) 
    
@service.post("/update_categories")
def update_categories(id: int = Form(...),name: str = Form(...), price: str = Form(...)):
    try:
        if change_category_details(id, name, price):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Category successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_category")
def delete_category(payload: DeleteCategory):
    try:
        categories = delete_category_by_id(payload.id)
        return {
            "status": "success",
            "data": categories
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete category data"
        })

#####################################################################################################################


# Create Event
@service.post('/addevents')
async def create_event(ename: str = Form(...),eventtype: str = Form(...), recipienttype: str = Form(...), descp: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_event(generate_token, auth_token="", inputs={
                'ename': ename, 'eventtype': eventtype, 'recipienttype': recipienttype, "descp": descp, 'event_allowed ': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Event registration failed Alreadly Exists"
        })
    
# Read Group list
@service.get("/events")
def fetch_all_events():
    try:
        # Fetch all groups' data here
        events = fetch_all_events_data()

        return {
            "status": "success",
            "data": events
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch events data"
        })

#Get Group data by id for update fields Mapping
@service.get("/events_by_onlyid")
def fetch_events_by_onlyid(id):
    try:
        # Fetch all event's data here
        events = fetch_event_by_onlyid(id)

        return {
            "status": "success",
            "data": events
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch event's data"
        }) 
    
@service.post("/update_events")
def update_events(id: int = Form(...),ename: str = Form(...),eventtype: str = Form(...), recipienttype: str = Form(...), descp: str = Form(...)):
    try:
        if change_event_details(id, ename, eventtype, recipienttype, descp):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Event successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_event")
def delete_event(payload: DeleteEvent):
    try:
        events = delete_event_by_id(payload.id)
        return {
            "status": "success",
            "data": events
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete event data"
        })
    
############################################################################################################################

# Create Classroom
@service.post('/addclassrooms')
async def create_classroom(instname: str = Form(...),classname: str = Form(...), date: str = Form(...), starttime: str = Form(...), venue: str = Form(...), messg: str = Form(...), duration: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_classroom(generate_token, auth_token="", inputs={
                'instname': instname, 'classname': classname, 'date': date, 'starttime': starttime, 'venue': venue, 'messg': messg, 'duration': duration, 'classroom_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Classroom registration failed Alreadly Exists"
        })
    
# Read Classroom list
@service.get("/classrooms")
def fetch_all_classrooms():
    try:
        # Fetch all classrooms' data here
        classrooms = fetch_all_classroom_data()

        return {
            "status": "success",
            "data": classrooms
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch classroom's data"
        })

#Get Classroom data by id for update fields Mapping
@service.get("/classrooms_by_onlyid")
def fetch_classrooms_by_onlyid(id):
    try:
        # Fetch all classroom's data here
        classrooms = fetch_classroom_by_onlyid(id)

        return {
            "status": "success",
            "data": classrooms
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch classroom's data"
        }) 
    
@service.post("/update_classrooms")
def update_classrooms(id: int = Form(...),instname: str = Form(...),classname: str = Form(...), date: str = Form(...), starttime: str = Form(...), venue: str = Form(...), messg: str = Form(...), duration: str = Form(...)):
    try:
        if change_classroom_details(id, instname, classname, date, starttime, venue, messg, duration):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Classroom successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_classroom")
def delete_classroom(payload: DeleteClassroom):
    try:
        classrooms = delete_classroom_by_id(payload.id)
        return {
            "status": "success",
            "data": classrooms
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete classrooms data"
        })
    
############################################################################################################################

# Create Conference
@service.post('/addconferences')
async def create_conference(instname: str = Form(...),confname: str = Form(...), date: str = Form(...), starttime: str = Form(...), meetlink: str = Form(...), messg: str = Form(...), duration: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_conference(generate_token, auth_token="", inputs={
                'instname': instname, 'confname': confname, 'date': date, 'starttime': starttime, 'meetlink': meetlink, 'messg': messg, 'duration': duration, 'conference_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Conference registration failed Alreadly Exists"
        })
    
# Read Conference list
@service.get("/conferences")
def fetch_all_conferences():
    try:
        # Fetch all conference's data here
        conferences = fetch_all_conference_data()

        return {
            "status": "success",
            "data": conferences
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch conference's data"
        })

#Get Conference data by id for update fields Mapping
@service.get("/conferences_by_onlyid")
def fetch_conferences_by_onlyid(id):
    try:
        # Fetch all conference's data here
        conferences = fetch_conference_by_onlyid(id)

        return {
            "status": "success",
            "data": conferences
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch conference's data"
        }) 
    
@service.post("/update_conferences")
def update_conferences(id: int = Form(...),instname: str = Form(...),confname: str = Form(...), date: str = Form(...), starttime: str = Form(...), meetlink: str = Form(...), messg: str = Form(...), duration: str = Form(...)):
    try:
        if change_conference_details(id, instname, confname, date, starttime, meetlink, messg, duration):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Conference successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_conference")
def delete_conference(payload: DeleteConference):
    try:
        conferences = delete_conference_by_id(payload.id)
        return {
            "status": "success",
            "data": conferences
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete conferences data"
        })
    

############################################################################################################################

# Create Virtual Training
@service.post('/addvirtualtrainings')
async def create_virtualtraining(instname: str = Form(...),virtualname: str = Form(...), date: str = Form(...), starttime: str = Form(...), meetlink: str = Form(...), messg: str = Form(...), duration: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_virtualtraining(generate_token, auth_token="", inputs={
                'instname': instname, 'virtualname': virtualname, 'date': date, 'starttime': starttime, 'meetlink': meetlink, 'messg': messg, 'duration': duration, 'virtualtraining_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Virtual Training registration failed Alreadly Exists"
        })
    
# Read Virtual Training list
@service.get("/virtualtrainings")
def fetch_all_virtualtraining():
    try:
        # Fetch all virtualtraining's data here
        virtualtrainings = fetch_all_virtualtraining_data()

        return {
            "status": "success",
            "data": virtualtrainings
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch virtualtraining's data"
        })

#Get Virtual Training data by id for update fields Mapping
@service.get("/virtualtrainings_by_onlyid")
def fetch_virtualtrainings_by_onlyid(id):
    try:
        # Fetch all virtualtraining's data here
        virtualtrainings = fetch_virtualtraining_by_onlyid(id)

        return {
            "status": "success",
            "data": virtualtrainings
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch virtualtraining's data"
        }) 
    
@service.post("/update_virtualtrainings")
def update_virtualtrainings(id: int = Form(...),instname: str = Form(...),virtualname: str = Form(...), date: str = Form(...), starttime: str = Form(...), meetlink: str = Form(...), messg: str = Form(...), duration: str = Form(...)):
    try:
        if change_virtualtraining_details(id, instname, virtualname, date, starttime, meetlink, messg, duration):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Virtual Training successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_virtualtraining")
def delete_virtualtrainings(payload: DeleteVirtual):
    try:
        virtualtrainings = delete_virtualtraining_by_id(payload.id)
        return {
            "status": "success",
            "data": virtualtrainings
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete virtualtrainings data"
        })
    
############################################################################################################################

# Create Discussion
@service.post('/add_discussions')
async def create_discussion(topic: str = Form(...),messg: str = Form(...), file : UploadFile = File(...), access: str = Form(...),generate_token: bool = Form(...)):
    with open("files/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = str("files/"+file.filename)
    try:
        return add_discussion(topic,generate_token, auth_token="", inputs={
                'topic': topic,'messg': messg, 'file': url, 'access': access, 'discussion_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Discussion registration failed Alreadly Exists"
        })
    
# Read Discussion list
@service.get("/discussions")
def fetch_all_discussions():
    try:
        # Fetch all discussion's data here
        discussions = fetch_all_discussion_data()

        return {
            "status": "success",
            "data": discussions
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch discussion's data"
        })

#Get Discussion data by id for update fields Mapping
@service.get("/discussions_by_onlyid")
def fetch_discussions_by_onlyid(id):
    try:
        # Fetch all discussion's data here
        discussions = fetch_discussion_by_onlyid(id)

        return {
            "status": "success",
            "data": discussions
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch discussion's data"
        }) 
    
@service.post("/update_discussions")
def update_discussions(id: int = Form(...),topic: str = Form(...),messg: str = Form(...), file : UploadFile = File(...), access: str = Form(...)):
    with open("files/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file = str("files/"+file.filename)
    try:
        if change_discussion_details(id, topic, messg, file, access):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Discussion successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_discussion")
def delete_discussions(payload: DeleteDiscussion):
    try:
        discussions = delete_discussion_by_id(payload.id)
        return {
            "status": "success",
            "data": discussions
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete discussions data"
        })
    
############################################################################################################################

# Create Calender
@service.post('/add_calenders')
async def create_calender(cal_eventname: str = Form(...),date: str = Form(...), starttime : str = Form(...), duration: str = Form(...), audience: str = Form(...), messg: str = Form(...),generate_token: bool = Form(...)):

    try:
        return add_calender(cal_eventname,generate_token, auth_token="", inputs={
                'cal_eventname': cal_eventname,'date': date, 'starttime': starttime, 'duration': duration, 'audience': audience, 'messg': messg, 'calender_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Calender registration failed Alreadly Exists"
        })
    
# Read calender list
@service.get("/calenders")
def fetch_all_calenders():
    try:
        # Fetch all calender's data here
        calenders = fetch_all_calender_data()

        return {
            "status": "success",
            "data": calenders
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch Calender's data"
        })

#Get Calender data by id for update fields Mapping
@service.get("/calenders_by_onlyid")
def fetch_calenders_by_onlyid(id):
    try:
        # Fetch all calender's data here
        calenders = fetch_calender_by_onlyid(id)

        return {
            "status": "success",
            "data": calenders
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch Calender's data"
        }) 
    
@service.post("/update_calenders")
def update_calenders(id: int = Form(...),cal_eventname: str = Form(...),date: str = Form(...), starttime : str = Form(...), duration: str = Form(...), audience: str = Form(...), messg: str = Form(...)):
    try:
        if change_calender_details(id, cal_eventname, date, starttime, duration, audience, messg):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Calender successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_calender")
def delete_calenders(payload: DeleteCalender):
    try:
        calenders = delete_calender_by_id(payload.id)
        return {
            "status": "success",
            "data": calenders
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete Calenders data"
        })
    
##########################################################################################################################

# To Upload Zip File of SCORM 

@service.post("/upload/")
async def upload_scorm_course_zipfile(file: UploadFile = File(...), uname: str = Form(...)):

    #Create unique folder for uploading Scorm zip
    mode = 0o666
    parent_dir = "C:/Users/Admin/Desktop/LIVE/LMS-Backend"
    file_dir = str(int(time.time()))
    path = os.path.join(parent_dir, file_dir)
    os.mkdir(path, mode)

    #MOve uploaded file to created unique folder
    with open(file_dir + "/" + file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Extract zip file in that unique folder
    with ZipFile(file_dir + "/" + file.filename, 'r') as zObject:
        zObject.extractall(
            path=file_dir + "/")

#     # YOu got all relevance data for iframe and database entry
    return {"filename": file.filename, "name": uname, "url": parent_dir+"/"+file_dir+"/story.html"}


@service.post("/scorm_zip_upload/")
async def upload_scorm_course_zipfile(file: UploadFile = File(...), uname: str = Form(...)):

    # Create unique folder for uploading SCORM zip
    mode = 0o666
    parent_dir = "C:/Users/Admin/Desktop/LIVE/LMS-Backend"
    file_dir = str(int(time.time()))
    path = os.path.join(parent_dir, file_dir)
    os.mkdir(path, mode)

    # Move uploaded file to the created unique folder
    with open(os.path.join(path, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract zip file in the unique folder
    with ZipFile(os.path.join(path, file.filename), 'r') as zObject:
        zObject.extractall(path=path)

    # Update the latest extracted folder
    global latest_extracted_folder
    latest_extracted_folder = path

    # Return relevant data for iframe and database entry
    return {"filename": file.filename, "name": uname, "url": parent_dir+"/"+file_dir+"/story.html"}

@service.get("/launch_course")
async def launch_course():
    global latest_extracted_folder

    if latest_extracted_folder:
        story_html_path = os.path.join(latest_extracted_folder, "story.html")
        if os.path.exists(story_html_path):
            # Here, you can generate the HTML page to launch the course automatically
            # You can use frameworks like Flask, Django, or even just pure HTML/JS to do this
            # For simplicity, let's assume you are using a simple HTML page to display the story.html content
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Course Launcher</title>
                </head>
                <body>
                    <iframe src="{story_html_path}" width="100%" height="100%"></iframe>
                </body>
                </html>
            """
            return HTMLResponse(content=html_content, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="story.html not found")
    else:
        raise HTTPException(status_code=404, detail="No course available")
    
@service.get("/images")
def list_images():
    imgpath = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/"
    image_tags = []
    for filename in os.listdir(imgpath):
        image_tags.append(f'<img src="/images/{filename}" alt="{filename}">')

    return "\n".join(image_tags)

@service.get("/images/{filename}")
def get_image(filename: str):
    imgpath = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/"
    image_path = os.path.join(imgpath, filename)
    if os.path.isfile(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}


