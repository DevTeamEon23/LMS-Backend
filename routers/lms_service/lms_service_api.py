import traceback
import shutil
import json
import time
import os
import base64
from zipfile import ZipFile
from PIL import Image
from io import BytesIO
import routers.lms_service.lms_service_ops as model
from fastapi.responses import JSONResponse,HTMLResponse,FileResponse
from fastapi import APIRouter, Depends,UploadFile, File,Form, Query
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from config.db_config import SessionLocal,n_table_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,fetch_users_by_onlyid,delete_user_by_id,change_user_details,add_new,fetch_all_courses_data,delete_course_by_id,add_course,add_group,fetch_all_groups_data,delete_group_by_id,change_course_details,change_group_details,add_category,fetch_all_categories_data,change_category_details,delete_category_by_id,add_event,fetch_all_events_data,change_event_details,delete_event_by_id,fetch_category_by_onlyid,fetch_course_by_onlyid,fetch_group_by_onlyid,fetch_event_by_onlyid
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,Users, UserDetail,DeleteCourse,DeleteGroup,DeleteCategory,DeleteEvent)
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
                'ename': ename, 'eventtype': eventtype, 'recipienttype': recipienttype, "descp": descp, 'group_allowed': '[]','picture': ""})
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
    

# To Upload Zip File of SCORM 

@service.post("/upload/")
async def upload_scorm_course_zipfile(file: UploadFile = File(...), uname: str = Form(...)):

    #Create unique folder for uploading Scorm zip
    mode = 0o666
    parent_dir = "C:/Users/Aniruddha/Desktop/LIVE/LMS-Backend"
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

# @service.get("/images", response_class=HTMLResponse)
# def images():
#     imgpath = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/"
#     image_tags = []
#     for filename in os.listdir(imgpath):
#         image_path = os.path.join(imgpath, filename)
#         with open(image_path, 'rb') as f:
#             base64data = base64.b64encode(f.read()).decode('utf-8')
#         image_tags.append(f'<img src="data:image/jpeg;base64,{base64data}" alt="{filename}">')

#     return "\n".join(image_tags)

@service.get("/images")
def list_images():
    imgpath = "C:/Users/Aniruddha/Desktop/LIVE/LMS-Backend/media/"
    image_tags = []
    for filename in os.listdir(imgpath):
        image_tags.append(f'<img src="/images/{filename}" alt="{filename}">')

    return "\n".join(image_tags)

@service.get("/images/{filename}")
def get_image(filename: str):
    imgpath = "C:/Users/Aniruddha/Desktop/LIVE/LMS-Backend/media/"
    image_path = os.path.join(imgpath, filename)
    if os.path.isfile(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}