import traceback
import shutil
import json
import time
import os
import base64
import pandas as pd
import mysql.connector
import subprocess
import xlsxwriter
from pathlib import Path
from typing import List
from zipfile import ZipFile
from PIL import Image
from datetime import timedelta
from moviepy.editor import VideoFileClip
from datetime import datetime
from io import BytesIO
import routers.lms_service.lms_service_ops as model
from fastapi.responses import JSONResponse,HTMLResponse,FileResponse
from fastapi import APIRouter, Depends,UploadFile, File,Form, Query,HTTPException, Response,Header
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from config.db_config import SessionLocal,n_table_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,fetch_all_inst_learn_data,fetch_users_by_onlyid,delete_user_by_id,change_user_details,add_new,fetch_all_courses_data,fetch_active_courses_data,delete_course_by_id,add_course,add_group,fetch_all_groups_data,fetch_all_groups_data_excel,delete_group_by_id,change_course_details,change_group_details,add_category,fetch_all_categories_data,change_category_details,delete_category_by_id,add_event,fetch_all_events_data,change_event_details,delete_event_by_id,fetch_category_by_onlyid,fetch_course_by_onlyid,fetch_group_by_onlyid,fetch_event_by_onlyid,add_classroom,fetch_all_classroom_data,fetch_classroom_by_onlyid,change_classroom_details,delete_classroom_by_id,add_conference,fetch_all_conference_data,fetch_conference_by_onlyid,change_conference_details,delete_conference_by_id,add_virtualtraining,fetch_all_virtualtraining_data,fetch_virtualtraining_by_onlyid,change_virtualtraining_details,delete_virtualtraining_by_id,add_discussion,fetch_all_discussion_data,fetch_discussion_by_onlyid,change_discussion_details,delete_discussion_by_id,add_calender,fetch_all_calender_data,fetch_calender_by_onlyid,change_calender_details,delete_calender_by_id,add_new_excel,clone_course,enroll_courses_touser,user_exists,fetch_users_data_export,fetch_courses_data_export,fetch_users_course_enrolled,enroll_coursegroup_massaction,fetch_enrolled_unenroll_courses_of_user,unenroll_courses_from_userby_id,enroll_groups_touser,fetch_added_unadded_groups_of_user,remove_group_from_userby_id,enroll_users_tocourse,fetch_enrolled_unenroll_users_of_course,unenrolled_users_from_courseby_id,enroll_groups_tocourse,fetch_enrolled_unenroll_groups_of_course,unenrolled_groups_from_courseby_id,enroll_users_togroup,fetch_added_unadded_users_of_group,remove_user_from_groupby_id,enroll_courses_togroup,fetch_added_unadded_courses_of_group,remove_course_from_groupby_id,remove_course_from_all_groups_by_course_id,fetch_enrolled_unenroll_instructors_of_course,fetch_enrolled_unenroll_learners_of_course,fetch_added_unadded_instructors_of_group,fetch_added_unadded_learners_of_group,remove_file_by_id,fetch_enrolled_courses_of_user,unenroll_courses_from_enrolleduserby_id,fetch_added_groups_of_user,remove_group_from_enrolleduserby_id,update_user,add_course_content, fetch_course_content_by_onlyid, change_course_content_details, delete_course_content_by_id
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,Users, UserDetail,DeleteCourse,DeleteGroup,DeleteCategory,DeleteEvent,DeleteClassroom,DeleteConference,DeleteVirtual,DeleteDiscussion,DeleteCalender,UnenrolledUsers_Course,UnenrolledUsers_Group,UnenrolledCourse_Group,UnenrolledUsers_Group,Remove_file, DeleteCourseContent)
from utils import success_response
from config.logconfig import logger

from ..db_ops import execute_query

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])
user_tab1 = APIRouter(tags=["User Tab1 : Course Page"], dependencies=[Depends(verify_user)])
user_tab2 = APIRouter(tags=["User Tab2 : Group Page"], dependencies=[Depends(verify_user)])

course_tab1 = APIRouter(tags=["COURSE Tab1: User Page"], dependencies=[Depends(verify_user)])
course_tab2 = APIRouter(tags=["COURSE Tab2: Group Page"], dependencies=[Depends(verify_user)])

group_tab1 = APIRouter(tags=["GROUP Tab1: User Page"], dependencies=[Depends(verify_user)])
group_tab2 = APIRouter(tags=["GROUP Tab2: Course Page"], dependencies=[Depends(verify_user)])

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
        # Get the original file name provided by the user
        original_filename = file.filename
        
        # Create a temporary file with the original filename to save the uploaded content
        temp_file_path = original_filename
        with open(temp_file_path, "wb") as temp_file:
            while content := await file.read(1024):
                temp_file.write(content)

        # Read the uploaded Excel file using pandas (defaulting to the first sheet)
        df = pd.read_excel(temp_file_path)
        
        total_rows = len(df)
        success_count = 0
        duplicate_count = 0
        
        # Create a set to keep track of seen emails
        seen_emails = set()

        # Process and insert the data from the DataFrame
        for _, row in df.iterrows():
            email = row['email']
            
            # Check if the email is already seen (in the current Excel file)
            if email in seen_emails:
                duplicate_count += 1
                continue  # Skip adding duplicate users

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue  # Skip adding duplicate users
            
            data = {
                'eid': row['eid'],
                'sid': row['sid'],
                'full_name': row['full_name'],
                'email': email,  # Use the email variable from above
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
            add_new_excel(email, password=row['password'], auth_token="", inputs=data)
            success_count += 1

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue

        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
    except Exception as exc:
        logger.error(traceback.format_exc())
        duplicate_count = total_rows - success_count
        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })

@service.post('/addusers_excel_superadmin')
async def create_users_from_excel(file: UploadFile = File(...)):
    try:
        # Get the original file name provided by the user
        original_filename = file.filename
        
        # Create a temporary file with the original filename to save the uploaded content
        temp_file_path = original_filename
        with open(temp_file_path, "wb") as temp_file:
            while content := await file.read(1024):
                temp_file.write(content)

        # Read the uploaded Excel file using pandas (defaulting to the first sheet)
        df = pd.read_excel(temp_file_path)
        
        total_rows = len(df)
        success_count = 0
        duplicate_count = 0
        
        # Create a set to keep track of seen emails
        seen_emails = set()

        # Process and insert the data from the DataFrame
        for _, row in df.iterrows():
            role = row['role']
    
            # Check if the role is not "Admin"
            if role != "Admin":
                continue

            email = row['email']
            
            # Check if the email is already seen (in the current Excel file)
            if email in seen_emails:
                duplicate_count += 1
                continue  # Skip adding duplicate users

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue  # Skip adding duplicate users
            
            data = {
                'eid': row['eid'],
                'sid': row['sid'],
                'full_name': row['full_name'],
                'email': email,  # Use the email variable from above
                'dept': row['dept'],
                'adhr': row['adhr'],
                'username': row['username'],
                'password': row['password'],
                'bio': row['bio'],
                'role': role,
                'timezone': row['timezone'],
                'langtype': row['langtype'],
                'active': row['active'],
                'deactive': row['deactive'],
                'exclude_from_email': row['exclude_from_email'],
                'generate_token': row['generate_token']
            }

            # Call your add_new function with the data
            add_new_excel(email, password=row['password'], auth_token="", inputs=data)
            success_count += 1

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue

        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
    except Exception as exc:
        logger.error(traceback.format_exc())
        duplicate_count = total_rows - success_count
        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
@service.post('/addusers_excel_admin')
async def create_users_from_excel(file: UploadFile = File(...)):
    try:
        # Get the original file name provided by the user
        original_filename = file.filename
        
        # Create a temporary file with the original filename to save the uploaded content
        temp_file_path = original_filename
        with open(temp_file_path, "wb") as temp_file:
            while content := await file.read(1024):
                temp_file.write(content)

        # Read the uploaded Excel file using pandas (defaulting to the first sheet)
        df = pd.read_excel(temp_file_path)
        
        total_rows = len(df)
        success_count = 0
        duplicate_count = 0
        
        # Create a set to keep track of seen emails
        seen_emails = set()

        # Process and insert the data from the DataFrame
        for _, row in df.iterrows():
            role = row['role']
    
            # Check if the role is not "Admin"
            if role != "Instructor":
                continue

            email = row['email']
            
            # Check if the email is already seen (in the current Excel file)
            if email in seen_emails:
                duplicate_count += 1
                continue  # Skip adding duplicate users

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue  # Skip adding duplicate users
            
            data = {
                'eid': row['eid'],
                'sid': row['sid'],
                'full_name': row['full_name'],
                'email': email,  # Use the email variable from above
                'dept': row['dept'],
                'adhr': row['adhr'],
                'username': row['username'],
                'password': row['password'],
                'bio': row['bio'],
                'role': role,
                'timezone': row['timezone'],
                'langtype': row['langtype'],
                'active': row['active'],
                'deactive': row['deactive'],
                'exclude_from_email': row['exclude_from_email'],
                'generate_token': row['generate_token']
            }

            # Call your add_new function with the data
            add_new_excel(email, password=row['password'], auth_token="", inputs=data)
            success_count += 1

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue

        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
    except Exception as exc:
        logger.error(traceback.format_exc())
        duplicate_count = total_rows - success_count
        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
@service.post('/addusers_excel_instructor')
async def create_users_from_excel(file: UploadFile = File(...)):
    try:
        # Get the original file name provided by the user
        original_filename = file.filename
        
        # Create a temporary file with the original filename to save the uploaded content
        temp_file_path = original_filename
        with open(temp_file_path, "wb") as temp_file:
            while content := await file.read(1024):
                temp_file.write(content)

        # Read the uploaded Excel file using pandas (defaulting to the first sheet)
        df = pd.read_excel(temp_file_path)
        
        total_rows = len(df)
        success_count = 0
        duplicate_count = 0
        
        # Create a set to keep track of seen emails
        seen_emails = set()

        # Process and insert the data from the DataFrame
        for _, row in df.iterrows():
            role = row['role']
    
            # Check if the role is not "Admin"
            if role != "Learner":
                continue

            email = row['email']
            
            # Check if the email is already seen (in the current Excel file)
            if email in seen_emails:
                duplicate_count += 1
                continue  # Skip adding duplicate users

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue  # Skip adding duplicate users
            
            data = {
                'eid': row['eid'],
                'sid': row['sid'],
                'full_name': row['full_name'],
                'email': email,  # Use the email variable from above
                'dept': row['dept'],
                'adhr': row['adhr'],
                'username': row['username'],
                'password': row['password'],
                'bio': row['bio'],
                'role': role,
                'timezone': row['timezone'],
                'langtype': row['langtype'],
                'active': row['active'],
                'deactive': row['deactive'],
                'exclude_from_email': row['exclude_from_email'],
                'generate_token': row['generate_token']
            }

            # Call your add_new function with the data
            add_new_excel(email, password=row['password'], auth_token="", inputs=data)
            success_count += 1

            # Call your user_exists function to check for duplicates by email
            if user_exists(email):
                duplicate_count += 1
                continue

        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    
    except Exception as exc:
        logger.error(traceback.format_exc())
        duplicate_count = total_rows - success_count
        message = f"{success_count} users added successfully from the Excel file."
        if duplicate_count > 0:
            message += f" {duplicate_count} users were skipped due to duplicates in the users' table."
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "status": "success",
            "message": message
        })
    

####################################    Export Excel Api     ##################################

CDN_DOMAIN = "https://v1.eonlearning.tech"


def fetch_users_data():
    try:
        # Fetch all users' data using your existing function
        users_data = fetch_users_data_export()

        # Create a DataFrame from the fetched data
        users_df = pd.DataFrame(users_data)

        return users_df

    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch users data"
        })

def fetch_courses_data():
    try:
        # Fetch all users' data using your existing function
        courses_data = fetch_courses_data_export()

        # Create a DataFrame from the fetched data
        courses_df = pd.DataFrame(courses_data)

        return courses_df

    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch courses data"
        })
    
def fetch_groups_data():
    try:
        # Fetch all users' data using your existing function
        users_data = fetch_all_groups_data_excel()

        # Create a DataFrame from the fetched data
        users_df = pd.DataFrame(users_data)

        return users_df

    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch users data"
        })
    
# Define a folder to store exported files
EXPORT_FOLDER = "exported_files"

# Ensure the export folder exists
os.makedirs(EXPORT_FOLDER, exist_ok=True)

    
def export_to_excel_with_multiple_sheets():
    try:
        table_data = {
            "users": fetch_users_data(),
            "course": fetch_courses_data(),
            "lmsgroup": fetch_groups_data()
        }

        # Specify the pre-defined file name
        file_name = "exported_data.xlsx"

        # Create the file path
        file_path = os.path.join(EXPORT_FOLDER, file_name)

        # Create an XlsxWriter workbook and add sheets
        workbook = xlsxwriter.Workbook(file_path, {'nan_inf_to_errors': True})  # Add nan_inf_to_errors option

        for table, data in table_data.items():
            worksheet = workbook.add_worksheet(table)

            # Write the data to the sheet
            for row_num, row_data in enumerate(data.values):
                for col_num, cell_value in enumerate(row_data):
                    worksheet.write(row_num, col_num, cell_value)

        # Close the workbook
        workbook.close()

        return file_name

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {e}")


@service.get("/export_to_excel")
async def export_data_to_excel_and_download():
    try:
        table_data = {
            "users": fetch_users_data(),
            "course": fetch_courses_data(),
            "lmsgroup": fetch_groups_data()
        }

        # Specify the pre-defined file name
        file_name = "exported_data.xlsx"

        # Create the file path
        file_path = os.path.join(EXPORT_FOLDER, file_name)

        # Create an XlsxWriter workbook and add sheets
        workbook = xlsxwriter.Workbook(file_path, {'nan_inf_to_errors': True})  

        for table, data in table_data.items():
            worksheet = workbook.add_worksheet(table)

            # Write the data to the sheet
            for row_num, row_data in enumerate(data.values):
                for col_num, cell_value in enumerate(row_data):
                    worksheet.write(row_num, col_num, cell_value)

        # Close the workbook
        workbook.close()

        # Create the full download link with the CDN domain
        full_download_link = f"{CDN_DOMAIN}/{EXPORT_FOLDER}/{file_name}"

        return JSONResponse(status_code=200, content={"message": "Data exported successfully.", "download_link": full_download_link})

    except HTTPException as e:
        return e
    

@service.get("/download/{file_name}")
async def download_file(file_name: str):
    # Ensure the requested file exists in the export folder
    file_path = os.path.join(EXPORT_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name)
    else:
        return {"error": "File not found"}
    

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

# Read Users list
@service.get("/instructor_learner_data")
def fetch_all_instructor_learner_data():
    try:
        # Fetch all users' data here
        users = fetch_all_inst_learn_data()

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch instructors & learners' data"
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
    
@service.put("/update_user/{id}")
async def update_user_fields_endpoint(id: int, update_data: dict):
    try:
        result = update_user(id, update_data)
        return {"status": "success", "message": result}
    except ValueError as exc:
        return {"status": "failure", "message": str(exc)}
    
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
async def create_course(coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(None), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(None)):
    with open("course/" + file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = str("course/" + file.filename)

    if coursevideo is not None:
        with open("coursevideo/" + coursevideo.filename, "wb") as buffer:
            shutil.copyfileobj(coursevideo.file, buffer)
        urls = str("coursevideo/" + coursevideo.filename)
    else:
        urls = ""  # Initialize as an empty string if coursevideo is not provided

    # Check if either courselink or coursevideo is provided
    if not (courselink or coursevideo):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Either courselink or coursevideo must be provided"
        })

    # Initialize courselink as an empty string if not provided
    if not courselink:
        courselink = ""

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

@service.post('/addcourse_content')
async def create_course_content(course_id: str = Form(...),video_unitname: str = Form(...), video_file: UploadFile = File(...), active: bool = Form(...), deactive: bool = Form(...),generate_token: bool = Form(...)):
    with open("course/"+video_file.filename, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    url = str("course/"+video_file.filename)
    try:
        return add_course_content(generate_token, auth_token="", inputs={
                'course_id': course_id, 'video_unitname': video_unitname, 'video_file': url, 'active': active, 'deactive': deactive, 'course_content_allowed': '[]','picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Course Content registration failed Alreadly Exists"
        })
    
# Read Course Content list
@service.get("/course_contents")
def fetch_all_course_content():
    try:
        # Fetch all course_content's data here
        course_contents = fetch_all_course_content_data()

        return {
            "status": "success",
            "data": course_contents
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch course_content's data"
        })

CDN_BASE_URL = "https://v1.eonlearning.tech/"

def fetch_all_course_content_data():
    try:
        # Query all course_content from the database
        course_contents = LmsHandler.get_all_course_contents()

        # Transform the course_content objects into a list of dictionaries
        course_contents_data = []
        for course_content in course_contents:
            video_path = course_content.video_file  # Assuming video_file is a str
            video_url = "C:/Users/Admin/Desktop/NEW_LIVE/LMS-Backend/" + video_path.decode('utf-8')  # Complete video URL
            print("video_url:", video_url)
            
            # Calculate video duration based on the CDN URL
            video_duration = get_video_duration(video_url)
            
            # Format video_duration as hours, minutes, seconds, and milliseconds
            duration_formatted = str(timedelta(seconds=video_duration))
            
            course_content_data = {
                "id": course_content.id,
                "course_id": course_content.course_id,
                "video_unitname": course_content.video_unitname,
                "video_file": video_url,  # Use the CDN URL
                "video_duration": duration_formatted,  # Format duration
                "active": course_content.active,
                "deactive": course_content.deactive,
                "created_at": course_content.created_at,
                "updated_at": course_content.updated_at,
                # Include other course_content attributes as needed
            }
            course_contents_data.append(course_content_data)

        return course_contents_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch course_contents data"
        })
    
# def fetch_all_course_content_data():
#     try:
#         # Query all course_content from the database
#         course_contents = LmsHandler.get_all_course_contents()

#         # Transform the course_content objects into a list of dictionaries
#         course_contents_data = []
#         for course_content in course_contents:
#             video_path = course_content.video_file  # Assuming video_file is a str
#             video_url = "C:/Users/Admin/Desktop/NEW_LIVE/LMS-Backend/" + video_path.decode('utf-8')  # Complete video URL
#             print("video_url:", video_url)
#             # Calculate video duration based on the CDN URL
#             video_duration = get_video_duration(video_url)

#             course_content_data = {
#                 "id": course_content.id,
#                 "course_id": course_content.course_id,
#                 "video_unitname": course_content.video_unitname,
#                 "video_file": video_url,  # Use the CDN URL
#                 "video_duration": video_duration,
#                 "active": course_content.active,
#                 "deactive": course_content.deactive,
#                 "created_at": course_content.created_at,
#                 "updated_at": course_content.updated_at,
#                 # Include other course_content attributes as needed
#             }
#             course_contents_data.append(course_content_data)

#         return course_contents_data
#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "Failed to fetch course_contents data"
#         })
    
def get_video_duration(video_url):
    try:
        # Calculate the duration of the video using moviepy without saving it locally
        clip = VideoFileClip(video_url)
        video_duration = clip.duration

        return video_duration
    except Exception as exc:
        logger.error(traceback.format_exc())
        return None
    
#Get Course Content data by id for update fields Mapping
@service.get("/course_contents_by_onlyid")
def fetch_course_contents_by_onlyid(id):
    try:
        # Fetch all course_content's data here
        course_contents = fetch_course_content_by_onlyid(id)

        return {
            "status": "success",
            "data": course_contents
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch course_content's data"
        }) 

@service.post("/update_course_contents")
def update_course_contents(id: int = Form(...),course_id: str = Form(...),video_unitname: str = Form(...), video_file: UploadFile = File(...), active: bool = Form(...), deactive: bool = Form(...)):
    with open("course/"+video_file.filename, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    video_file = str("course/"+video_file.filename)
    try:
        if change_course_content_details(id, course_id, video_unitname, video_file, active, deactive):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Course Content successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.delete("/delete_course_content")
def delete_course_contents(payload: DeleteCourseContent):
    try:
        course_contents = delete_course_content_by_id(payload.id)
        return {
            "status": "success",
            "data": course_contents
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Delete course_contents data"
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
    parent_dir = "C:/Users/Admin/Desktop/NEW_LIVE/LMS-Backend"
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
    parent_dir = "C:/Users/Admin/Desktop/NEW_LIVE/LMS-Backend"
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
                    <iframe src="{story_html_path}" width="100%" height="750 px"></iframe>
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
    imgpath = "/home/ubuntu/LMS-Backend/media/"
    image_tags = []
    for filename in os.listdir(imgpath):
        image_tags.append(f'<img src="/images/{filename}" alt="{filename}">')

    return "\n".join(image_tags)

@service.get("/images/{filename}")
def get_image(filename: str):
    imgpath = "/home/ubuntu/LMS-Backend/media/"
    image_path = os.path.join(imgpath, filename)
    if os.path.isfile(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}
    
# Upload files and mark them as active
UPLOAD_DIR = "uploads"

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define the allowed file types and their maximum file sizes
ALLOWED_FILE_TYPES = {
    'ppt': 100,
    'pptx': 100,
    'doc': 100,
    'docx': 100,
    'xls': 100,
    'xlsx': 100,
    'pdf': 100,
    'csv': 100,
    'epub': 100,
    'gz': 100,
    'sql': 100,
    'txt': 2,
    'vtt': 2,
    'srt': 2,
    'gif': 10,
    'jpg': 10,
    'jpeg': 10,
    'png': 10,
    'heic': 10,
    'mp4': 100,
    'webm': 100,
    # Add more file types as needed
}
# Maximum allowed file size in bytes (10 MB)
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024

# List of allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx' }

def upload_file_to_db(user_id, file_data, files_allowed, auth_token, request_token, token, active):
    query = """
        INSERT INTO documents (user_id, files, files_allowed, auth_token, request_token, token, active, created_at, updated_at)
        VALUES (%(user_id)s, %(files)s, %(files_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(created_at)s, %(updated_at)s);
    """
    params = {
        "user_id": user_id,
        "files": file_data,  # Binary file data
        "files_allowed": files_allowed,
        "auth_token": auth_token,
        "request_token": request_token,
        "token": token,
        "active": active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    return execute_query(query, params=params)

@service.post("/upload_file/")
async def upload_file_api(user_id: int, file: UploadFile, active: bool):
    try:
        # Check if the file extension is allowed
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_FILE_TYPES:
            raise HTTPException(status_code=400, detail="File type not allowed")

        # Calculate the file size
        file_size_bytes = len(file.file.read())
        file.file.seek(0)

        # Check if the file size exceeds the allowed limit
        if file_size_bytes > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File size exceeds the allowed limit")

        # Save the file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save file information to the database using execute_query
        query = """
            INSERT INTO documents
            (user_id, files, files_allowed, auth_token, request_token, token, active, created_at, updated_at, filename)
            VALUES
            (%(user_id)s, %(files)s, 'some_value', 'some_value', 'some_value', 'some_value', %(active)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %(filename)s)
        """
        params = {
            "user_id": user_id,
            "files": file_path,
            "active": active,
            "filename": file.filename,
        }

        execute_query(query, params=params)

        return JSONResponse(status_code=200, content={"message": "File uploaded successfully"})
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to upload file")


# Fetch active files
@service.get("/files/")
def fetch_user_enrollcourse_by_onlycourse_id():
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_users_course_enrolled()

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data"
        })
    
@service.get("/fetch_files")
def fetch_files_api():
    try:
        # Modify the query to select filename, file type, active status, and format the file size
        query = """
            SELECT
                id,
                user_id,
                filename,
                SUBSTRING_INDEX(filename, '.', -1) as file_type,
                files,
                CONCAT(
                    CASE
                        WHEN LENGTH(files) >= 1024*1024*1024 THEN ROUND(LENGTH(files) / (1024*1024*1024), 2)
                        WHEN LENGTH(files) >= 1024*1024 THEN ROUND(LENGTH(files) / (1024*1024), 2)
                        WHEN LENGTH(files) >= 1024 THEN ROUND(LENGTH(files) / 1024, 2)
                        ELSE LENGTH(files)
                    END,
                    CASE
                        WHEN LENGTH(files) >= 1024*1024*1024 THEN ' GB'
                        WHEN LENGTH(files) >= 1024*1024 THEN ' MB'
                        WHEN LENGTH(files) >= 1024 THEN ' KB'
                        ELSE 'bytes'
                    END
                ) AS file_size_formatted,
                active,
                created_at
            FROM documents
            WHERE active = 1

            UNION ALL

            SELECT
                id,
                user_id,
                filename,
                SUBSTRING_INDEX(filename, '.', -1) as file_type,
                files,
                CONCAT(
                    CASE
                        WHEN LENGTH(files) >= 1024*1024*1024 THEN ROUND(LENGTH(files) / (1024*1024*1024), 2)
                        WHEN LENGTH(files) >= 1024*1024 THEN ROUND(LENGTH(files) / (1024*1024), 2)
                        WHEN LENGTH(files) >= 1024 THEN ROUND(LENGTH(files) / 1024, 2)
                        ELSE LENGTH(files)
                    END,
                    CASE
                        WHEN LENGTH(files) >= 1024*1024*1024 THEN ' GB'
                        WHEN LENGTH(files) >= 1024*1024 THEN ' MB'
                        WHEN LENGTH(files) >= 1024 THEN ' KB'
                        ELSE 'bytes'
                    END
                ) AS file_size_formatted,
                active,
                created_at
            FROM documents
            WHERE active = 0;
        """

        # Execute the query and get the result (replace with your actual database query function)
        files_metadata = execute_query(query)

        # Process the result and return it
        result = []
        for row in files_metadata:
            result.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "file_size_formatted": row["file_size_formatted"],
                "active": row["active"],
                "created_at": row["created_at"]
            })

        return {
            "status": "success",
            "data": result
        }
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "message": "Failed to fetch files"
        })

@service.delete("/remove_file_byid")
def delete_file(payload: Remove_file):
    try:
        file = remove_file_by_id(payload.id)
        return {
            "status": "success",
            "data": file
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to delete file"
        })
    
###################################### Enroll Courses to USER (USERS -> Course Page) ###########################################

# Create enroll_course
@user_tab1.post('/enroll_courses_to_user',tags=["User Tab1 : Course Page"])
async def enroll_course_to_user(user_id: int = Form(...),course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_courses_touser(user_id,generate_token, auth_token="", inputs={
                'user_id': user_id,'course_id': course_id,'u_c_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Course enrolled to user failed"
        })

@user_tab1.get("/fetch_enroll_courses_of_user",tags=["User Tab1 : Course Page"])
def fetch_course_enrollusers_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_enrolled_unenroll_courses_of_user(user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data"
        }) 
    
# Unenrolled USER from Course
@user_tab1.delete("/unenroll_courses_from_user",tags=["User Tab1 : Course Page"])
def unenroll_course_user(payload: UnenrolledUsers_Course):
    try:
        users = unenroll_courses_from_userby_id(payload.id)
        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled user data from course"
        })
    
#############################################################################################################################

@service.get("/fetch_enrolled_courses_of_users")
def fetch_enrollusers_course_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_enrolled_courses_of_user(user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data"
        }) 

@service.delete("/unenroll_courses_from_enrolled_user")
def unenroll_course_from_enroll_user(data_user_course_enrollment_id: int):
    try:
        users = unenroll_courses_from_enrolleduserby_id(data_user_course_enrollment_id)
        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled user data from course"
        })
        
@service.get("/fetch_enrolled_groups_of_users")
def fetch_enrollusers_groups_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of groups here
        groups = fetch_added_groups_of_user(user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data"
        })
    
@service.delete("/remove_groups_from_enrolled_user")
def unenroll_group_from_enroll_user(data_user_group_enrollment_id: int):
    try:
        groups = remove_group_from_enrolleduserby_id(data_user_group_enrollment_id)
        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled group data from course"
        })
    
###################################### Enroll Group to USER (USERS -> Group Page) ###########################################

# Create enroll_course
@user_tab2.post('/enroll_groups_to_user',tags=["User Tab2 : Group Page"])
async def enroll_group_to_user(user_id: int = Form(...),group_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_groups_touser(user_id,generate_token, auth_token="", inputs={
                'user_id': user_id,'group_id': group_id,'u_g_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Group enrolled to user failed"
        })

@user_tab2.get("/fetch_groups_of_user",tags=["User Tab2 : Group Page"])
def fetch_added_groups_touser_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        groups = fetch_added_unadded_groups_of_user(user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data"
        }) 
    
# Unenrolled USER from Course
@user_tab2.delete("/remove_groups_from_user",tags=["User Tab2 : Group Page"])
def unenroll_group_user(payload: UnenrolledUsers_Group):
    try:
        groups = remove_group_from_userby_id(payload.id)
        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled group data from course"
        })



###################################### Enroll Users to COURSE (COURSE -> User Page) ###########################################

# Create enroll_course
@course_tab1.post('/enroll_users_to_course',tags=["COURSE Tab1: User Page"])
async def enroll_user_to_course(user_id: int = Form(...),course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_users_tocourse(user_id,generate_token, auth_token="", inputs={
                'user_id': user_id,'course_id': course_id,'u_c_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User enrolled to Course failed"
        })

@course_tab1.get("/fetch_enroll_users_of_course", tags=["COURSE Tab1: User Page"])
def fetch_added_users_tocourse_by_onlyuser_id(course_id: int):
    try:
        # Fetch all enrolled users' data of the specified course
        users = fetch_enrolled_unenroll_users_of_course(course_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled users' data"
        }) 

@course_tab1.get("/fetch_enroll_instructors_of_course", tags=["Admin :-COURSE Tab: User Page"])
def fetch_added_instructor_tocourse_by_onlyuser_id(course_id: int):
    try:
        # Fetch all enrolled users' data of the specified course
        instructors = fetch_enrolled_unenroll_instructors_of_course(course_id)

        return {
            "status": "success",
            "data": instructors
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled Instructor's data"
        }) 
    
@course_tab1.get("/fetch_enroll_learners_of_course", tags=["Instructor:- COURSE Tab: User Page"])
def fetch_added_learners_tocourse_by_onlyuser_id(course_id: int):
    try:
        # Fetch all enrolled users' data of the specified course
        learners = fetch_enrolled_unenroll_learners_of_course(course_id)

        return {
            "status": "success",
            "data": learners
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled learners' data"
        }) 
    

# Unenrolled USER from Course
@course_tab1.delete("/remove_users_from_course",tags=["COURSE Tab1: User Page"])
def unenroll_user_course(payload: UnenrolledUsers_Course):
    try:
        users = unenrolled_users_from_courseby_id(payload.id)
        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled users data from course"
        })

###################################### Enroll Group to COURSE (COURSE -> Group Page) ###########################################

# Create 
@course_tab2.post('/enroll_group_to_course',tags=["COURSE Tab2: Group Page"])
async def enroll_group_to_course(group_id: int = Form(...),course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_groups_tocourse(group_id,generate_token, auth_token="", inputs={
                'group_id': group_id,'course_id': course_id,'c_g_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Group enrolled to Course failed"
        })

@course_tab2.get("/fetch_groups_of_course",tags=["COURSE Tab2: Group Page"])
def fetch_added_groups_tocourse_by_onlygroup_id(course_id: int):
    try:
        # Fetch all enrolled users' data of course here
        groups = fetch_enrolled_unenroll_groups_of_course(course_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data"
        }) 
    
# Unenrolled USER from Course
@course_tab2.delete("/remove_groups_from_course",tags=["COURSE Tab2: Group Page"])
def unenroll_group_course(payload: UnenrolledCourse_Group):
    try:
        groups = unenrolled_groups_from_courseby_id(payload.id)
        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled groups data from course"
        })
    

###################################### Enroll User to GROUP (GROUP -> User Page) ###########################################

# Create 
@group_tab1.post('/add_users_to_group',tags=["GROUP Tab1: User Page"])
async def enroll_users_to_group(group_id: int = Form(...),user_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_users_togroup(group_id,generate_token, auth_token="", inputs={
                'group_id': group_id,'user_id': user_id,'u_g_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Group enrolled to Course failed"
        })

@group_tab1.get("/fetch_users_of_group",tags=["GROUP Tab1: User Page"])
def fetch_added_users_togroup_by_onlygroup_id(group_id : int):
    try:
        # Fetch all enrolled users' data of course here
        users = fetch_added_unadded_users_of_group(group_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled users' data"
        }) 
    
@group_tab1.get("/fetch_instructors_of_group",tags=["Admin:- GROUP Tab: User Page"])
def fetch_added_instructors_togroup_by_onlygroup_id(group_id : int):
    try:
        # Fetch all enrolled instructors' data of course here
        users = fetch_added_unadded_instructors_of_group(group_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled instructors' data"
        }) 
    
@group_tab1.get("/fetch_learners_of_group",tags=["Instructor:- GROUP Tab: User Page"])
def fetch_added_learners_togroup_by_onlygroup_id(group_id : int):
    try:
        # Fetch all enrolled learners' data of course here
        learners = fetch_added_unadded_learners_of_group(group_id)

        return {
            "status": "success",
            "data": learners
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled learners' data"
        }) 
    

# Unenrolled USER from Course
@group_tab1.delete("/remove_users_from_group",tags=["GROUP Tab1: User Page"])
def unenroll_user_group(payload: UnenrolledUsers_Group):
    try:
        users = remove_user_from_groupby_id(payload.id)
        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled users data from group"
        })


###################################### Enroll Course to GROUP (GROUP -> Course Page) ###########################################

# Create 
@group_tab2.post('/add_courses_to_group',tags=["GROUP Tab2: Course Page"])
async def enroll_course_to_group(group_id: int = Form(...),course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_courses_togroup(group_id,generate_token, auth_token="", inputs={
                'group_id': group_id,'course_id': course_id,'c_g_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Course enrolled to Group failed"
        })

@group_tab2.get("/fetch_courses_of_group",tags=["GROUP Tab2: Course Page"])
def fetch_added_courses_togroup_by_onlygroup_id(group_id : int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_added_unadded_courses_of_group(group_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data"
        }) 
    
# Unenrolled USER from Course
@group_tab2.delete("/remove_courses_from_group",tags=["GROUP Tab2: Course Page"])
def unenroll_course_group(payload: UnenrolledCourse_Group):
    try:
        courses = remove_course_from_groupby_id(payload.id)
        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to Unenrolled courses data from group"
        })

# Define a folder to store exported files
UPLOAD_DIR = "uploads"

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

@service.get("/file_download/{files_name}")
async def download_files(files_name: str):
    # Ensure the requested file exists in the export folder
    file_path = os.path.join(UPLOAD_DIR, files_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=files_name)
    else:
        return {"error": "File not found"}





######################################## Mass Action to all groups ##############################################

@service.post('/mass_enroll_course_group', tags=["Group: Mass Enroll Course to Group"])
async def massaction_groups_enroll(course_id: int = Form(...), generate_token: bool = Form(...)):
    try:
        return enroll_coursegroup_massaction(course_id, generate_token, auth_token="", inputs={
            'course_id': course_id, 'c_g_enrollment_allowed': '[]', 'picture': ""})
    except Exception as exc: 
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "course enrolled to group failed"
        })
    
@service.delete('/mass_unenroll_course_group', tags=["Group: Mass Unenroll Course from Group"])
async def unenroll_course_group(course_id: int = Form(...)):
    try:
        result = remove_course_from_all_groups_by_course_id(course_id)
        return {
            "status": "success",
            "message": "Course unenrolled from all groups successfully"
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to unenroll course from all groups"
        })