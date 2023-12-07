import traceback
import shutil
import json
import time
import os
from typing import Optional
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
import pytz
from io import BytesIO
import routers.lms_service.lms_service_ops as model
from fastapi.responses import JSONResponse,HTMLResponse,FileResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from fastapi import APIRouter, Depends,UploadFile, File,Form, Query,HTTPException, Response,Header
from starlette import status
from sqlalchemy.orm import Session
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from config.db_config import SessionLocal,n_table_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,fetch_last_eid_data,fetch_last_id_data,fetch_all_dept_data,fetch_all_inst_learn_data,fetch_users_by_onlyid,delete_user_by_id,change_user_details,add_new,fetch_all_courses_data,fetch_active_courses_data,delete_course_by_id,add_course,add_group,fetch_all_groups_data,fetch_all_groups_data_excel,delete_group_by_id,change_course_details,change_group_details,add_category,fetch_all_categories_data,change_category_details,delete_category_by_id,add_event,fetch_all_events_data,change_event_details,delete_event_by_id,fetch_category_by_onlyid,fetch_course_by_onlyid,fetch_group_by_onlyid,fetch_event_by_onlyid,add_classroom,fetch_all_classroom_data,fetch_classroom_by_onlyid,change_classroom_details,delete_classroom_by_id,add_conference,fetch_all_conference_data,fetch_conference_by_onlyid,change_conference_details,delete_conference_by_id,add_virtualtraining,fetch_all_virtualtraining_data,fetch_virtualtraining_by_onlyid,change_virtualtraining_details,delete_virtualtraining_by_id,add_discussion,fetch_all_discussion_data,fetch_discussion_by_onlyid,change_discussion_details,delete_discussion_by_id,add_calender,fetch_all_calender_data,fetch_calender_by_onlyid,change_calender_details,delete_calender_by_id,add_new_excel,clone_course,enroll_courses_touser,user_exists,fetch_users_data_export,fetch_courses_data_export,fetch_users_course_enrolled,enroll_coursegroup_massaction,fetch_enrolled_unenroll_courses_of_user,unenroll_courses_from_userby_id,enroll_groups_touser,fetch_added_unadded_groups_of_user,remove_group_from_userby_id,enroll_users_tocourse,fetch_enrolled_unenroll_users_of_course,unenrolled_users_from_courseby_id,enroll_groups_tocourse,fetch_enrolled_unenroll_groups_of_course,unenrolled_groups_from_courseby_id,enroll_users_togroup,fetch_added_unadded_users_of_group,remove_user_from_groupby_id,enroll_courses_togroup,fetch_added_unadded_courses_of_group,remove_course_from_groupby_id,remove_course_from_all_groups_by_course_id,fetch_enrolled_unenroll_instructors_of_course,fetch_enrolled_unenroll_learners_of_course,fetch_added_unadded_instructors_of_group,fetch_added_unadded_learners_of_group,remove_file_by_id,fetch_enrolled_and_admin_inst_created_course_details_to_admin,fetch_enrolled_courses_of_user,unenroll_courses_from_enrolleduserby_id,fetch_enrolled_courses_of_learner,fetch_added_groups_of_admin,fetch_added_groups_of_learner,fetch_added_groups_of_user,remove_group_from_enrolleduserby_id,update_user,update_course, add_course_content, fetch_course_content_by_onlyid,change_course_content_video, change_course_content_details,change_course_content_scorm,update_course_content, delete_course_content_by_id,fetch_infographics_of_user,fetch_course_to_enroll_to_admin_inst,fetch_course_to_enroll_to_inst_learner,fetch_group_to_enroll_to_admin,fetch_group_to_enroll_to_inst_learner,fetch_users_enroll_to_admin,fetch_users_enroll_to_inst_learner,fetch_group_enroll_to_course_of_inst_learner,fetch_enrollusers_of_group_to_admin,fetch_enrollusers_of_group_to_inst_learner,fetch_course_enroll_to_group_of_inst_learner,change_course_details_new,fetch_overview_of_learner,add_ratings_feedback,fetch_all_data_counts_data,get_user_points_by_superadmin,fetch_all_deptwise_users_counts,fetch_all_admin_data_counts_data,fetch_all_deptwise_users_counts_for_admin,get_user_points_by_user_for_admin,get_user_enrolledcourses_info,get_user_enrolledcourses_info_for_admin,fetch_all_instructor_data_counts_data,get_user_points_by_user_for_instructor,fetch_all_deptwise_users_counts_for_instructor,get_user_enrolledcourses_info_for_instructor,fetch_created_courses_of_user,fetch_all_training_data,fetch_ratings_of_learners,get_user_enrolledcourses_info_by_id,add_test_question,get_tests_by_course_id,get_question_by_test_names,get_correct_answer, add_assignment_data,change_assignment_details,fetch_all_assignment_data,check_assignment,fetch_assignment_for_learner,fetch_assignments_done_from_learner,change_submission_details,add_inst_led_training,change_instructor_led_details,fetch_inst_led_by_session_name,delete_instructor_led_by_id
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,User, UserDetail,DeleteCourse,DeleteGroup,DeleteCategory,DeleteEvent,DeleteClassroom,DeleteConference,DeleteVirtual,DeleteDiscussion,DeleteCalender,UnenrolledUsers_Course,UnenrolledUsers_Group,UnenrolledCourse_Group,UnenrolledUsers_Group,Remove_file, DeleteCourseContent)
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

conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT")),
    MAIL_SERVER=os.environ.get("MAIL_SERVER"),
    MAIL_STARTTLS=False,  # Disable STARTTLS
    MAIL_SSL_TLS=True,    # Enable SSL/TLS
    USE_CREDENTIALS=bool(os.environ.get("USE_CREDENTIALS")),
    VALIDATE_CERTS=bool(os.environ.get("VALIDATE_CERTS"))
)

async def send_welcome_email(user: User):
    # Customize your welcome email template here
    try:
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Welcome to EonLearning App</title>
        </head>
        <body>
            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 1000px; overflow: auto; line-height: 2">
                <div style="margin: 50px auto; width: 70%; padding: 20px 0">
                    <div style="border-bottom: 1px solid #eee">
                        <a href="" style="font-size: 1.4em; color: #00466a; text-decoration: none; font-weight: 600">Welcome to EonLearning App</a>
                    </div>
                    <p style="font-size: 1.1em">Hi {fullname},</p>
                    <p>Your account has been successfully created.</p>
                    <p>Here are your login details:</p>
                    <p>Username: {email}</p>
                    <p>Password: {password}</p>
                    <p>Enjoy using our app!</p>
                </div>
            </div>
        </body>
        </html>
        """
        template = template.replace("{fullname}", user.fullname)
        template = template.replace("{email}", user.email)
        template = template.replace("{password}", user.password)

        message = MessageSchema(
            subject="Welcome to EonLearning App",
            recipients=[user.email],
            body=template,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)

        # Log success
        logger.info(f"Welcome email sent to {user.email}")

    except Exception as e:
        # Log any exceptions
        logger.error(f"Error sending welcome email: {str(e)}")

# Create User
# @service.post('/addusers')
# async def create_user(eid: str = Form(...),sid: str = Form(...), full_name: str = Form(...), email: str = Form(...),dept: str = Form(...), adhr: str = Form(...), username: str = Form(...), password: str = Form(...),bio: str = Form(...), role: str = Form(...), timezone: str = Form(...), langtype: str = Form(...), active: bool = Form(...), deactive: bool = Form(...), exclude_from_email: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...)):
#     with open("media/"+file.filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     url = str("media/"+file.filename)
#     try:
#         result = add_new(email,generate_token,password=password, auth_token="", inputs={
#                 'eid': eid,'sid': sid,'full_name': full_name,'email': email, 'dept': dept, 'adhr': adhr,'username': username,'bio': bio,'file': url,'role': role, 'timezone': timezone, 'langtype': langtype,'users_allowed': '[]', 'active': active, 'deactive': deactive, 'exclude_from_email': exclude_from_email, 'picture': "", "password": None})
        
#         if result.status_code == status.HTTP_200_OK:
#             # If the user was added successfully, send the welcome email
#             await send_welcome_email(user= User)
#             return JSONResponse(status_code=status.HTTP_200_OK, content={
#                 "status": "success",
#                 "message": "User registered successfully"
#             })

#         return {
#             "status": "success",
#             "data": result
#         }

#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "User is not registered"})

@service.post('/addusers')
async def create_user(
    eid: str = Form(...),
    sid: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    dept: str = Form(...),
    adhr: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    bio: str = Form(...),
    role: str = Form(...),
    timezone: str = Form(...),
    langtype: str = Form(...),
    active: bool = Form(...),
    deactive: bool = Form(...),
    exclude_from_email: bool = Form(...),
    generate_token: bool = Form(...),
    file: UploadFile = File(...)
):
    with open("media/" + file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = str("media/" + file.filename)

    try:
        result = add_new(
            email,
            generate_token,
            password=password,
            auth_token="",
            inputs={
                'eid': eid,
                'sid': sid,
                'full_name': full_name,
                'email': email,
                'dept': dept,
                'adhr': adhr,
                'username': username,
                'bio': bio,
                'file': url,
                'role': role,
                'timezone': timezone,
                'langtype': langtype,
                'active': active,
                'deactive': deactive,
                'exclude_from_email': exclude_from_email,
                'picture': "",
            }
        )

        if result.status_code == status.HTTP_200_OK:
            # Create a User object with the necessary information
            user = User(email=email, fullname=full_name, password=password)
            
            # If the user was added successfully, send the welcome email
            await send_welcome_email(user)  # Pass the user object
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "User registered successfully"
            })

        # return {
        #     "status": "success",
        #     "data": result
        # }


    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "User is not registered"})
    

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

CDN_DOMAIN = "https://beta.eonlearning.tech"


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

    
# def export_to_excel_with_multiple_sheets():
#     try:
#         table_data = {
#             "users": fetch_users_data(),
#             "course": fetch_courses_data(),
#             "lmsgroup": fetch_groups_data()
#         }

#         # Specify the pre-defined file name
#         file_name = "exported_data.xlsx"

#         # Create the file path
#         file_path = os.path.join(EXPORT_FOLDER, file_name)

#         # Create an XlsxWriter workbook and add sheets
#         workbook = xlsxwriter.Workbook(file_path, {'nan_inf_to_errors': True})  # Add nan_inf_to_errors option

#         for table, data in table_data.items():
#             worksheet = workbook.add_worksheet(table)

#             # Write the data to the sheet
#             for row_num, row_data in enumerate(data.values):
#                 for col_num, cell_value in enumerate(row_data):
#                     worksheet.write(row_num, col_num, cell_value)

#         # Close the workbook
#         workbook.close()

#         return file_name

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to export data: {e}")


@service.get("/export_to_excel")
async def export_data_to_excel_and_download():
    try:
        users_data = fetch_users_data_export()
        courses_data = fetch_courses_data_export()
        groups_data = fetch_all_groups_data_excel()

        # Specify the pre-defined file name
        file_name = "exported_data.xlsx"

        # Create the file path
        file_path = os.path.join(EXPORT_FOLDER, file_name)

        table_data = {
            "users": users_data,
            "courses": courses_data,
            "lmsgroup": groups_data
        }

        # Create an XlsxWriter workbook
        workbook = xlsxwriter.Workbook(file_path, {'nan_inf_to_errors': True, 'file_options': {'default_extension': 'xlsx'}})

        for table, data in table_data.items():
            worksheet = workbook.add_worksheet(table)

            # Create headers based on the keys in the first row
            headers = list(data[0].keys())
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)

            # Write the data to the sheet
            for row_num, row_data in enumerate(data):
                for col_num, cell_value in enumerate(row_data.values()):
                    worksheet.write(row_num + 1, col_num, cell_value)

        # Close the workbook to save it
        workbook.close()

        # Create the full download link with the CDN domain
        full_download_link = f"{CDN_DOMAIN}/{EXPORT_FOLDER}/{file_name}"

        return JSONResponse(status_code=200, content={"message": "Data exported successfully.", "download_link": full_download_link})

    except HTTPException as e:
        return e
    

@service.get("/export_to_csv")
async def export_data_to_csv():
    try:
        # Fetch data for users, courses, and lmsgroup
        users_data = fetch_users_data()
        courses_data = fetch_courses_data()
        groups_data = fetch_groups_data()

        # Define the file name
        file_name = "exported_data.csv"

        # Create the full file path
        file_path = os.path.join(EXPORT_FOLDER, file_name)

        # Create a dictionary with dataframes
        table_data = {
            "users": users_data,
            "courses": courses_data,
            "lmsgroup": groups_data
        }

        # Export data to CSV
        for table, data in table_data.items():
            data.to_csv(file_path, mode="a", header=True, index=False, sep=',', encoding="utf-8")

        return JSONResponse(status_code=200, content={"message": "Data exported successfully.", "download_link": f"{CDN_DOMAIN}/{EXPORT_FOLDER}/{file_name}"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {e}")


@service.get("/download/{file_name}")
async def download_file(file_name: str):
    # Ensure the requested file exists in the export folder
    file_path = os.path.join(EXPORT_FOLDER, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name, headers={"Content-Disposition": f'attachment; filename={file_name}'})
    else:
        return {"error": "File not found"}

# Read Users list
@service.get("/users")
def fetch_all_users():
    try:
        # Fetch all users' data here
        eid = fetch_all_users_data()

        return {
            "status": "success",
            "data": eid
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch eids' data"
        })

@service.get("/eids")
def fetch_last_eid():
    try:
        # Fetch all eids data here
        eids = fetch_last_eid_data()

        return {
            "status": "success",
            "data": eids
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch eids' data"
        })
    
@service.get("/dept")
def fetch_all_dept():
    try:
        # Fetch all users' data here
        dept = fetch_all_dept_data()

        return {
            "status": "success",
            "data": dept
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch depts' data"
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

@service.get("/course_ids")
def fetch_last_course_id():
    try:
        # Fetch all eids data here
        ids = fetch_last_id_data()

        return {
            "status": "success",
            "data": ids
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch ids' data"
        })
    
# Create Course
@service.post('/addcourses')
async def create_course(id: int = Form(...), user_id: int = Form(...), coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(None), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(None)):
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
                'id': id, 'user_id': user_id, 'coursename': coursename, 'description': description,'coursecode': coursecode,'price': price, 'courselink': courselink, 'capacity': capacity,'startdate': startdate,'enddate': enddate,'timelimit': timelimit,'file': url,'certificate': certificate, 'level': level, 'category': category, 'coursevideo': urls,'course_allowed': '[]', 'isActive': isActive, 'isHide': isHide, 'picture': ""})
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
def update_courses(id: int = Form(...),user_id: int = Form(...),coursename: str = Form(...),description: str = Form(...), coursecode: str = Form(...), price: str = Form(...),courselink: str = Form(...), capacity: str = Form(...), startdate: str = Form(...), enddate: str = Form(...),timelimit: str = Form(...), certificate: str = Form(...), level: str = Form(...), category: str = Form(...), isActive: bool = Form(...), isHide: bool = Form(...),file: UploadFile = File(...),coursevideo: UploadFile = File(...)):
    with open("course/"+file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file = str("course/"+file.filename)
    with open("coursevideo/"+coursevideo.filename, "wb") as buffer:
        shutil.copyfileobj(coursevideo.file, buffer)
    coursevideo = str("coursevideo/"+coursevideo.filename)

    try:
        if change_course_details(id, user_id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
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
    
@service.post("/update_courses_new")
async def update_courses(
    id: int = Form(...),
    user_id: int = Form(...),
    coursename: str = Form(...),
    description: str = Form(...),
    coursecode: str = Form(...),
    price: str = Form(...),
    courselink: str = Form(...),
    capacity: str = Form(...),
    startdate: str = Form(...),
    enddate: str = Form(...),
    timelimit: str = Form(...),
    certificate: str = Form(...),
    level: str = Form(...),
    category: str = Form(...),
    isActive: bool = Form(...),
    isHide: bool = Form(...),
    file: Optional[UploadFile] = File(default=None),
    coursevideo: Optional[UploadFile] = File(default=None),
):
    # Retrieve the existing course file and course video paths from the database
    existing_course = LmsHandler.get_course_by_id(id)  # Replace with your function to retrieve course details

    # Set the file_path and coursevideo_path to existing paths initially
    file_path = existing_course.get("file")
    coursevideo_path = existing_course.get("coursevideo")

    if file:
        # If a new file is provided, update the file_path
        with open("course/" + file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = "course/" + file.filename

    if coursevideo:
        # If a new coursevideo is provided, update the coursevideo_path
        with open("coursevideo/" + coursevideo.filename, "wb") as buffer:
            shutil.copyfileobj(coursevideo.file, buffer)
        coursevideo_path = "coursevideo/" + coursevideo.filename

    if coursevideo_path is None:
        coursevideo_path = 'null'
        
    try:
        if change_course_details_new(id, user_id, coursename, file_path, description, coursecode, price, courselink, coursevideo_path, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
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


@service.put("/update_course/{id}")
async def update_course_fields_endpoint(id: int, update_data: dict):
    try:
        result = update_course(id, update_data)
        return {"status": "success", "message": result}
    except ValueError as exc:
        return {"status": "failure", "message": str(exc)}
    
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
def check_existing_course_content_by_course_id(course_id):

    query = f"""
    select * from course_content where course_id=%(course_id)s;
    """
    response = execute_query(query, params={'course_id': course_id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
# @service.post('/addcourse_content')
# async def create_course_content(course_id: str = Form(...),video_unitname: str = Form(...), video_file: UploadFile = File(...), ppt_unitname: str = Form(...), ppt_file: UploadFile = File(...), scorm_unitname: str = Form(...), scorm_file: UploadFile = File(...),generate_token: bool = Form(...)):
#     with open("coursevideo/"+video_file.filename, "wb") as buffer:
#         shutil.copyfileobj(video_file.file, buffer)
#     url = str("coursevideo/"+video_file.filename)
    
#     with open("courseppt/" + ppt_file.filename, "wb") as buffer:
#         shutil.copyfileobj(ppt_file.file, buffer)
#     ppt_url = str("courseppt/" + ppt_file.filename)

#     with open("coursescorm/" + scorm_file.filename, "wb") as buffer:
#         shutil.copyfileobj(scorm_file.file, buffer)
#     scorm_url = str("coursescorm/" + scorm_file.filename)

#     try:
#         return add_course_content(generate_token, auth_token="", inputs={
#                 'course_id': course_id, 'video_unitname': video_unitname, 'video_file': url, 'ppt_unitname': ppt_unitname, 'ppt_file': ppt_url, 'scorm_unitname': scorm_unitname, 'scorm_file': scorm_url, 'course_content_allowed': '[]','picture': ""})
#     except Exception as exc: 
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "Course Content registration failed Alreadly Exists"
#         })
    
# @service.post('/addcourse_content_video')
# async def create_course_content(course_id: str = Form(...), video_unitname: str = Form(...), video_file: UploadFile = File(...), generate_token: bool = Form(...)):
#     with open("coursevideo/" + video_file.filename, "wb") as buffer:
#         shutil.copyfileobj(video_file.file, buffer)
#     url = str("coursevideo/" + video_file.filename)

#     try:
#         return add_course_content(generate_token, auth_token="", inputs={
#             'course_id': course_id, 'video_unitname': video_unitname, 'video_file': url, 'ppt_unitname': '', 'ppt_file': '', 'scorm_unitname': '', 'scorm_file': '', 'course_content_allowed': '[]','picture': ""})
#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "Course Content registration failed Alreadly Exists"
#         })
    
@service.post('/addcourse_content_video')
async def create_course_content_video(
    course_id: str = Form(...),
    video_unitname: str = Form(...),
    video_file: UploadFile = File(...),
    generate_token: bool = Form(...),
):
    # Handling Video file
    with open("coursevideo/" + video_file.filename, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    url = str("coursevideo/" + video_file.filename)

    try:
        # Check if the course content exists for the given course_id
        is_existing = check_existing_course_content_by_course_id(course_id)

        if is_existing:
            # Update course content if it already exists
            if change_course_content_video(course_id, video_unitname, url):
                return JSONResponse(status_code=status.HTTP_200_OK, content={
                    "status": "success",
                    "message": "Updated Course Content successfully"
                })
        else:
            # Add new course content if it does not exist
            return add_course_content(generate_token, auth_token="", inputs={
                'course_id': course_id,
                'video_unitname': video_unitname,
                'video_file': url,
                'ppt_unitname': '',
                'ppt_file': '',
                'scorm_unitname': '',
                'scorm_file': '',
                'course_content_allowed': '[]',
                'picture': ""
            })
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": f"Course Content registration failed. {exc}"
        })
    
# @service.post('/addcourse_content_ppt')
# async def create_course_content_ppt(course_id: str = Form(...), ppt_unitname: str = Form(...), ppt_file: UploadFile = File(...), generate_token: bool = Form(...)):
#     with open("courseppt/" + ppt_file.filename, "wb") as buffer:
#         shutil.copyfileobj(ppt_file.file, buffer)
#     ppt_file_url = str("courseppt/" + ppt_file.filename)

#     try:
#         return add_course_content(generate_token, auth_token="", inputs={
#             'course_id': course_id, 'video_unitname': '', 'video_file': '', 'ppt_unitname': ppt_unitname, 'ppt_file': ppt_file_url, 'scorm_unitname': '', 'scorm_file': '', 'course_content_allowed': '[]','picture': ""})
#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "Course Content registration failed Alreadly Exists"
#         })

@service.post('/addcourse_content_ppt')
async def create_course_content_ppt(course_id: str = Form(...), ppt_unitname: str = Form(...), ppt_file: UploadFile = File(...), generate_token: bool = Form(...)):
    with open("courseppt/" + ppt_file.filename, "wb") as buffer:
        shutil.copyfileobj(ppt_file.file, buffer)
    ppt_file_url = str("courseppt/" + ppt_file.filename)

    try:
        # Check if the course content exists for the given course_id
        is_existing = check_existing_course_content_by_course_id(course_id)

        if is_existing:
            # Update course content if it already exists
            ppt_file_path = ppt_file_url  # Assuming ppt_file_path is the URL in this case
            if change_course_content_details(course_id, ppt_unitname, ppt_file_path):
                return JSONResponse(status_code=status.HTTP_200_OK, content={
                    "status": "success",
                    "message": "Updated Course Content successfully"
                })
        else:
            # Add new course content if it does not exist
            return add_course_content(generate_token, auth_token="", inputs={
                'course_id': course_id,
                'video_unitname': '',
                'video_file': '',
                'ppt_unitname': ppt_unitname,
                'ppt_file': ppt_file_url,
                'scorm_unitname': '',
                'scorm_file': '',
                'course_content_allowed': '[]',
                'picture': ""
            })
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": f"Course Content registration failed. {exc}"
        })
    
@service.post('/addcourse_content_scorm')
async def create_course_content_scorm(course_id: str = Form(...), scorm_unitname: str = Form(...), scorm_file: UploadFile = File(...), generate_token: bool = Form(...)):
    with open("coursescorm/" + scorm_file.filename, "wb") as buffer:
        shutil.copyfileobj(scorm_file.file, buffer)
    scorm_file_url = str("coursescorm/" + scorm_file.filename)

    try:
        # Check if the course content exists for the given course_id
        is_existing = check_existing_course_content_by_course_id(course_id)

        if is_existing:
            # Update course content if it already exists
            scorm_file_path = scorm_file_url  # Assuming scorm_file_path is the URL in this case
            if change_course_content_scorm(course_id, scorm_unitname, scorm_file_path):
                return JSONResponse(status_code=status.HTTP_200_OK, content={
                    "status": "success",
                    "message": "Updated Course Content successfully"
                })
        else:
            # Add new course content if it does not exist
            return add_course_content(generate_token, auth_token="", inputs={
                'course_id': course_id,
                'video_unitname': '',
                'video_file': '',
                'ppt_unitname': '',
                'ppt_file': '',
                'scorm_unitname': scorm_unitname,
                'scorm_file': scorm_file_url,
                'course_content_allowed': '[]',
                'picture': ""
            })
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": f"Course Content registration failed. {exc}"
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

CDN_BASE_URL = "https://beta.eonlearning.tech/"

def fetch_all_course_content_data():
    try:
        # Query all course_content from the database
        course_contents = LmsHandler.get_all_course_contents()

        # Transform the course_content objects into a list of dictionaries
        course_contents_data = []
        for course_content in course_contents:
            video_path = course_content.video_file  # Assuming video_file is a str
            video_url = "/home/ubuntu/LMS-Backend/" + video_path.decode('utf-8')  # Complete video URL
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
def fetch_course_contents_by_onlyid(course_id):
    try:
        # Fetch all course_content's data here
        course_contents = fetch_course_content_by_onlyid(course_id)

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

# PPT      * * * * * * * * * * * * *
@service.post("/update_course_contents_ppt")
def update_course_content_ppt(course_id: str = Form(...),ppt_unitname: str = Form(...), ppt_file: UploadFile = File(...)):
    # with open("coursevideo/"+video_file.filename, "wb") as buffer:
    #     shutil.copyfileobj(video_file.file, buffer)
    # video_file = str("coursevideo/"+video_file.filename)

    with open("courseppt/" + ppt_file.filename, "wb") as buffer:
        shutil.copyfileobj(ppt_file.file, buffer)
    ppt_file_path = str("courseppt/" + ppt_file.filename)

    # with open("coursescorm/" + scorm_file.filename, "wb") as buffer:
    #     shutil.copyfileobj(scorm_file.file, buffer)
    # scorm_file_path = str("coursescorm/" + scorm_file.filename)
    try:
        if change_course_content_details(course_id, ppt_unitname, ppt_file_path):
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
    
# SCORM       * * * * * * * * * * * *
@service.post("/update_course_contents_scorm")
def update_course_content_scorm(course_id: str = Form(...),scorm_unitname: str = Form(...), scorm_file: UploadFile = File(...)):

    with open("coursescorm/" + scorm_file.filename, "wb") as buffer:
        shutil.copyfileobj(scorm_file.file, buffer)
    scorm_file_path = str("coursescorm/" + scorm_file.filename)

    try:
        if change_course_content_scorm(course_id, scorm_unitname, scorm_file_path):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Added Course Content Scorm successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    

@service.put("/update_course_content/{course_id}")
async def update_course_content_fields_endpoint(course_id: int, update_data: dict):
    try:
        result = update_course_content(course_id, update_data)
        return {"status": "success", "message": result}
    except ValueError as exc:
        return {"status": "failure", "message": str(exc)}
    
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
async def create_group(user_id: int = Form(...), groupname: str = Form(...),groupdesc: str = Form(...), groupkey: str = Form(...),generate_token: bool = Form(...)):
    try:
        return add_group(generate_token, auth_token="", inputs={
                'user_id': user_id, 'groupname': groupname, 'groupdesc': groupdesc, 'groupkey': groupkey, 'group_allowed': '[]','picture': ""})
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
def update_groups(id: int = Form(...),user_id: int = Form(...), groupname: str = Form(...),groupdesc: str = Form(...), groupkey: str = Form(...)):
    try:
        if change_group_details(id, user_id, groupname, groupdesc, groupkey):
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
    
############################################# Training Dashboard Api ######################################

@service.get("/training")
def fetch_all_training():
    try:
        training_data = fetch_all_training_data()
        return training_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "message": "Failed to fetch training data"
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
    # mode = 0o666
    parent_dir = "/home/ubuntu/server/LMS-Backend/"
    file_dir = str(int(time.time()))
    path = os.path.join(parent_dir, file_dir)
    os.mkdir(path)
 
    #MOve uploaded file to created unique folder
    file_path = os.path.join(path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Extract zip file in that unique folder
    with ZipFile(file_path, 'r') as zObject:
        zObject.extractall(
            path=file_dir + "/")

#     # YOu got all relevance data for iframe and database entry
    return {"filename": file.filename, "name": uname, "url": parent_dir+"/"+file_dir+"/story.html"}


@service.post("/scorm_zip_upload/")
async def upload_scorm_course_zipfile(file: UploadFile = File(...), uname: str = Form(...)):

    # uploading Scorm zip
    #mode = 0o666
    parent_dir = "/home/ubuntu/server/LMS-Backend"
    file_dir = str(int(time.time()))
    path = os.path.join(parent_dir, file_dir)
    os.mkdir(path)
 
    #MOve uploaded file to created unique folder
    file_path = os.path.join(path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Extract zip file in that unique folder
    with ZipFile(file_path, 'r') as zObject:
        zObject.extractall(
            path=file_dir + "/")
        
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
            # Construct the full CDN URL for the iframe source
            iframe_url = f"{CDN_BASE_URL.rstrip('/')}/{story_html_path}"
            # For simplicity, create html content
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Course Launcher</title>
                </head>
                <body>
                    <iframe src="{iframe_url}" width="100%" height="750 px"></iframe>
                </body>
                </html>
            """
            return HTMLResponse(content=html_content, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="story.html not found")
    else:
        raise HTTPException(status_code=404, detail="No course available")
    
# @service.get("/launch_course")
# async def launch_course():
#     global latest_extracted_folder

#     if latest_extracted_folder:
#         story_html_path = os.path.join(latest_extracted_folder, "story.html")
#         if os.path.exists(story_html_path):
#             # Construct the full CDN URL for the iframe source
#             iframe_url = f"{CDN_BASE_URL.rstrip('/')}/{story_html_path}"

#             html_content = f"""
#                 <!DOCTYPE html>
#                 <html>
#                 <head>
#                     <title>Course Launcher</title>
#                 </head>
#                 <body>
#                     <iframe src="{iframe_url}" width="100%" height="750 px"></iframe>
#                 </body>
#                 </html>
#             """
#             return HTMLResponse(content=html_content, status_code=200)
#         else:
#             raise HTTPException(status_code=404, detail="story.html not found")
#     else:
#         raise HTTPException(status_code=404, detail="No course available")
    

@service.get("/images")
def list_images():
    imgpath = "/home/ubuntu/server/LMS-Backend/media/"
    image_tags = []
    for filename in os.listdir(imgpath):
        image_tags.append(f'<img src="/images/{filename}" alt="{filename}">')

    return "\n".join(image_tags)

@service.get("/images/{filename}")
def get_image(filename: str):
    imgpath = "/home/ubuntu/server/LMS-Backend/media/"
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
    'mp3': 100,
    'webm': 100,
    "zip": 50,
    "mkv": 100,
    # Add more file types as needed
}
# Maximum allowed file size in bytes (10 MB)
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024

# List of allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx' }

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

        ist = pytz.timezone('Asia/Kolkata')
        utc_now = datetime.utcnow()
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)
                                                              
        # Save file information to the database using execute_query
        query = """
            INSERT INTO documents
            (user_id, files, files_allowed, auth_token, request_token, token, active, created_at, updated_at, filename)
            VALUES
            (%(user_id)s, %(files)s, '', '', '', '', %(active)s, %(created_at)s, %(updated_at)s, %(filename)s)
        """
        params = {
            "user_id": user_id,
            "files": file_path,
            "active": active,
            "created_at": ist_now,
            "updated_at": ist_now,
            "filename": file.filename,
        }

        execute_query(query, params=params)

        return JSONResponse(status_code=200, content={"message": "File uploaded successfully"})
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to upload file, Please check the same filename alreadly exists or not and try again")


@service.put("/update_file/{file_id}/")
async def update_file_api(file_id: int, user_id: int, file: UploadFile, active: bool):
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

        # Save the updated file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ist = pytz.timezone('Asia/Kolkata')
        utc_now = datetime.utcnow()
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)

        # Update file information in the database using execute_query
        query = """
            UPDATE documents
            SET files = %(files)s,
                active = %(active)s,
                updated_at = %(updated_at)s,
                filename = %(filename)s
            WHERE id = %(file_id)s AND user_id = %(user_id)s
        """
        params = {
            "file_id": file_id,
            "user_id": user_id,
            "files": file_path,
            "active": active,
            "updated_at": ist_now,
            "filename": file.filename,
        }

        execute_query(query, params=params)

        return JSONResponse(status_code=200, content={"message": "File updated successfully"})
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to update file")
    
@service.put("/update_file_new/{file_id}/")
async def update_file_new_api(file_id: int, user_id: int, file: UploadFile = File(None), active: bool = Form(None)):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        utc_now = datetime.utcnow()
        ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist)

        # Initialize an empty dictionary for query parameters
        params = {
            "file_id": file_id,
            "user_id": user_id,
            "updated_at": ist_now,
        }

        # Initialize an empty list to store the query components
        query_components = []

        if file is not None:
            # If a new file is provided, update the 'files' field
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

            # Save the updated file to the upload directory
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Add 'files' field to the query
            query_components.append("files = %(files)s")
            params["files"] = file_path

        if active is not None:
            # If 'active' is provided, update the 'active' field
            # Add 'active' field to the query
            query_components.append("active = %(active)s")
            params["active"] = active

        # Construct the final query by joining query components
        query = f"""
            UPDATE documents
            SET {', '.join(query_components)}
            WHERE id = %(file_id)s AND user_id = %(user_id)s
        """

        execute_query(query, params=params)

        return JSONResponse(status_code=200, content={"message": "File information updated successfully"})
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to update file information")
    
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
    
backendBaseUrl = "https://beta.eonlearning.tech"

@service.get("/fetch_files")
def fetch_files_api():
    try:
        # Modify the query to select filename, file type, active status, format the file size, and include the file data
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

        # Process the result and return it with file data using backendBaseUrl
        result = []
        for row in files_metadata:
            file_data = row["files"]
            # Encode the file data in Base64
            file_path = file_data.decode('utf-8').replace("\\", "/")  # Replace backslashes with forward slashes
            encoded_file_data = backendBaseUrl + '/' + file_path
            result.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "file_size_formatted": row["file_size_formatted"],
                "active": row["active"],
                "created_at": row["created_at"],
                "file_data": encoded_file_data
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

@service.get("/fetch_files_byId/{file_id}")
def fetch_files_by_id_api(file_id: int):
    try:
        # Modify the query to select the file by ID
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
            WHERE id = %s;
        """

        # Execute the query and get the result (replace with your actual database query function)
        files_metadata = execute_query(query, (file_id,))

        # Check if a file with the given ID was found
        if not files_metadata:
            return JSONResponse(status_code=404, content={
                "status": "failure",
                "message": "File not found"
            })

        # Process the result and return it with file data using backendBaseUrl
        row = files_metadata.first()  # Use the first() method to access the first result
        file_data = row["files"]
        file_path = file_data.decode('utf-8').replace("\\", "/")  # Replace backslashes with forward slashes
        encoded_file_data = backendBaseUrl + '/' + file_path

        result = {
            "id": row["id"],
            "user_id": row["user_id"],
            "filename": row["filename"],
            "file_type": row["file_type"],
            "file_size_formatted": row["file_size_formatted"],
            "active": row["active"],
            "created_at": row["created_at"],
            "file_data": encoded_file_data
        }

        return {
            "status": "success",
            "data": result
        }
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "message": "Failed to fetch the file"
        })
    
@service.get("/fetch_active_files")
def fetch_active_files_api_for_learner():
    try:
        # Modify the query to select filename, file type, active status, format the file size, and include the file data
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
            WHERE active = 1;
        """

        # Execute the query and get the result (replace with your actual database query function)
        files_metadata = execute_query(query)

        # Process the result and return it with file data using backendBaseUrl
        result = []
        for row in files_metadata:
            file_data = row["files"]
            # Encode the file data in Base64
            file_path = file_data.decode('utf-8').replace("\\", "/")  # Replace backslashes with forward slashes
            encoded_file_data = backendBaseUrl + '/' + file_path
            result.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "filename": row["filename"],
                "file_type": row["file_type"],
                "file_size_formatted": row["file_size_formatted"],
                "active": row["active"],
                "created_at": row["created_at"],
                "file_data": encoded_file_data
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
    
################################## Fecth to enroll courses to Instructor Only####################################################
    
@service.get("/fetch_enrolled_courses_for_admin")
def fetch_enroll_course_for_admin(user_id: int, admin_user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_course_to_enroll_to_admin_inst(user_id, admin_user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data of admin"
        })

################################## Fecth to enroll course to Learner Only####################################################
    
@service.get("/fetch_enrolled_courses_for_inst_learn")
def fetch_enroll_course_for_inst_learner(user_id: int, inst_user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_course_to_enroll_to_inst_learner(user_id, inst_user_id)

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
    
############################################ Courses Lists for for Instructor & Learner ##########################################

@service.get("/fetch_enrolled_and_admin_inst_created_course_data_for_admin")
def fetch_enroll_and_admin_inst_created_course_details_to_admin_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_enrolled_and_admin_inst_created_course_details_to_admin(user_id)

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
    
############################################ Courses Lists for for Instructor & Learner ##########################################

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

@service.get("/fetch_created_courses_of_users")
def fetch_created_course_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_created_courses_of_user(user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch created courses' data"
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

############################################ Courses Lists for Learner ##########################################

@service.get("/fetch_enrolled_courses_of_learners")
def fetch_enrollusers_course_by_only_learners_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = fetch_enrolled_courses_of_learner(user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data of learner"
        }) 
    
################################## Fecth to enroll group to Instructor Only####################################################
    
@service.get("/fetch_enrolled_groups_for_admin")
def fetch_enroll_group_for_admin(user_id: int, admin_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        groups = fetch_group_to_enroll_to_admin(user_id, admin_user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data of admin for instructor"
        })
    
################################## Fecth to enroll group to Learner Only####################################################
    
@service.get("/fetch_enrolled_groups_for_inst_learn")
def fetch_enroll_group_for_inst_learner(user_id: int, inst_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        groups = fetch_group_to_enroll_to_inst_learner(user_id, inst_user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data of instructor for learner"
        })
    
################################################## Groups Lists for Admin ################################################################


@service.get("/fetch_enrolled_and_created_groups_of_admin")
def fetch_enrollusers_and_created_groups_by_onlyuser_id_admin(user_id: int):
    try:
        # Fetch all enrolled users' data of groups here
        groups = fetch_added_groups_of_admin(user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data for Admin"
        })
    
############################################## Groups Lists for Instructor #################################################


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
    
############################################## Groups Lists for Learner #################################################

@service.get("/fetch_enrolled_groups_of_learners")
def fetch_enrollusers_groups_by_onlylearner_id(user_id: int):
    try:
        # Fetch all enrolled users' data of groups here
        groups = fetch_added_groups_of_learner(user_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data of learners"
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
def fetch_added_instructor_tocourse_by_onlyuser_id(course_id: int,user_id: int):
    try:
        # Fetch all enrolled users' data of the specified course
        instructors = fetch_enrolled_unenroll_instructors_of_course(course_id,user_id)

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

################################## Fecth users enroll course to Instructor Only####################################################
    
@service.get("/fetch_users_course_enrolled_for_admin")
def fetch_userenroll_courses_for_admin(course_id: int, admin_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        users = fetch_users_enroll_to_admin(course_id, admin_user_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled users' data of admin"
        })
    
################################## Fecth users enroll course to Learner Only ####################################################
    
@service.get("/fetch_users_course_enrolled_for_inst_learn")
def fetch_userenroll_courses_for_inst_learner(course_id: int, inst_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        users = fetch_users_enroll_to_inst_learner(course_id, inst_user_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled users' data of instructor"
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
    
################################## Fecth users enroll course to Instructor and Learner ####################################################
    
@service.get("/fetch_groups_course_enrolled_for_inst_learn")
def fetch_groupenroll_courses_for_inst_learner(course_id: int):
    try:
        # Fetch all enrolled users' data of group here
        groups = fetch_group_enroll_to_course_of_inst_learner(course_id)

        return {
            "status": "success",
            "data": groups
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled groups' data of course"
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

################################## Fecth enroll users of groups to Instructor ####################################################
    
@service.get("/fetch_users_of_group_enrolled_for_admin")
def fetch_groupenroll_users_for_admin(group_id: int, admin_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        users = fetch_enrollusers_of_group_to_admin(group_id, admin_user_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled admin' data of group to instructor"
        })
    
################################## Fecth enroll users of groups to Learner ####################################################
    
@service.get("/fetch_users_of_group_enrolled_for_inst_learn")
def fetch_groupenroll_users_for_inst_learner(group_id: int, inst_user_id: int):
    try:
        # Fetch all enrolled users' data of group here
        users = fetch_enrollusers_of_group_to_inst_learner(group_id, inst_user_id)

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled instructor' data of group to learner"
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
        return FileResponse(file_path, filename=files_name, headers={"Content-Disposition": f'attachment; filename={files_name}'})
    else:
        return {"error": "File not found"}


################################## Fecth users enroll course to Instructor and Learner ####################################################
    
@service.get("/fetch_courses_group_enrolled_for_inst_learn")
def fetch_courseenroll_groups_for_inst_learner(group_id: int):
    try:
        # Fetch all enrolled users' data of group here
        courses = fetch_course_enroll_to_group_of_inst_learner(group_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' data of group"
        })


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
    
###################################################################################################################

@service.get("/fetch_infographics_of_users")
def fetch_infographics_of_user_by_onlyuser_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        infographics = fetch_infographics_of_user(user_id)

        return {
            "status": "success",
            "data": infographics
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch infographics data of Users"
        }) 
    
@service.get("/learner_overview")
def get_learner_overview(user_id: int):
    try:
        # Fetch all enrolled users' data of the course here
        infographics = fetch_overview_of_learner(user_id)

        return infographics
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch infographics data of Users"
        })

################################################# Rating & Feedback ##########################################################

@service.post("/give_ratings_feedback")
def rating_and_feedback(user_id: int = Form(...), course_id: int = Form(...), rating: int = Form(...), feedback: str = Form(...)):
    try:
        inputs = {
            'user_id': user_id,
            'course_id': course_id,
            'rating': rating,
            'feedback': feedback
        }

        if add_ratings_feedback(user_id, inputs=inputs):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Thanks For Your Feedback"
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
############################################### Superadmin Dashboard ################################################################

@service.get("/data_counts")
def fetch_all_counts_of_data():
    try:
        # Fetch all courses data here
        data_counts = fetch_all_data_counts_data()

        return {
            "status": "success",
            "data": data_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all data_counts' data"
        })
    
@service.get("/fetch_userpoints_superadmin_by_id")
def fetch_userpoints_for_superadmin():
    try:
        # Fetch all point's data of users here
        points = get_user_points_by_superadmin()

        return {
            "status": "success",
            "data": points
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch points data of Superadmin"
        }) 
    
@service.get("/department_counts")
def fetch_all_users_counts_by_dept():
    try:
        # Fetch all courses data here
        dept_counts = fetch_all_deptwise_users_counts()

        return {
            "status": "success",
            "data": dept_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all dept_counts' data"
        })

@service.get("/fetch_user_enrolled_course_data")
def fetch_users_course_info_for_Dashboard():
    try:
        # Fetch all point's data of users here
        data = get_user_enrolledcourses_info()

        return {
            "status": "success",
            "data": data
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch user enrolled course data"
        }) 
############################################### Admin Dashboard ################################################################

@service.get("/data_counts_for_admin")
def fetch_all_counts_of_data_for_admin(user_id):
    try:
        # Fetch all courses data here
        data_counts = fetch_all_admin_data_counts_data(user_id)

        return {
            "status": "success",
            "data": data_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all admin data_counts"
        })
    
@service.get("/fetch_userpoints_by_userid_for_admin")
def fetch_userpoints_for_admin(user_id):
    try:
        # Fetch all point's data of users here
        points = get_user_points_by_user_for_admin(user_id)

        return {
            "status": "success",
            "data": points
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch points data"
        }) 
    
@service.get("/department_counts_for_admin")
def fetch_all_users_counts_by_dept_for_admin():
    try:
        # Fetch all courses data here
        dept_counts = fetch_all_deptwise_users_counts_for_admin()

        return {
            "status": "success",
            "data": dept_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all admin dept_counts"
        })
    
@service.get("/fetch_user_enrolled_course_data_for_admin")
def fetch_users_course_info_for_Admin_Dashboard(user_id):
    try:
        # Fetch all point's data of users here
        data = get_user_enrolledcourses_info_for_admin(user_id)

        return {
            "status": "success",
            "data": data
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch user enrolled course data for admin"
        }) 
    
############################################### Instructor Dashboard ################################################################

@service.get("/data_counts_for_instructor")
def fetch_all_counts_of_data_for_instructor(user_id):
    try:
        # Fetch all courses data here
        data_counts = fetch_all_instructor_data_counts_data(user_id)

        return {
            "status": "success",
            "data": data_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all instructor data_counts"
        })
    
@service.get("/fetch_userpoints_by_userid_for_instructor")
def fetch_userpoints_for_instructor(user_id):
    try:
        # Fetch all point's data of users here
        points = get_user_points_by_user_for_instructor(user_id)

        return {
            "status": "success",
            "data": points
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch points data"
        }) 
    
@service.get("/department_counts_for_instructor")
def fetch_all_users_counts_by_dept_for_instructor():
    try:
        # Fetch all courses data here
        dept_counts = fetch_all_deptwise_users_counts_for_instructor()

        return {
            "status": "success",
            "data": dept_counts
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch all instructor dept_counts"
        })
    
@service.get("/fetch_user_enrolled_course_data_for_instructor")
def fetch_users_course_info_for_Instructor_Dashboard(user_id):
    try:
        # Fetch all point's data of users here
        data = get_user_enrolledcourses_info_for_instructor(user_id)

        return {
            "status": "success",
            "data": data
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch user enrolled course data for instructor"
        }) 

#########################################################################################################

@service.get("/learner_ratings")
def get_learner_ratings(user_id: int):
    try:
        # Fetch all ratings of course given by learners
        ratings = fetch_ratings_of_learners(user_id)

        return ratings
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch ratings data of Users"
        })
    
@service.get("/fetch_enroll_courses_of_user_by_id")
def fetch_course_enroll_tousers_by_using_user_id(user_id: int):
    try:
        # Fetch all enrolled users' data of course here
        courses = get_user_enrolledcourses_info_by_id(user_id)

        return {
            "status": "success",
            "data": courses
        }
    except Exception as exc:    
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch enrolled courses' of learner"
        }) 

############################################## Test Crud api's ##########################################################

@service.post("/add_test")
def add_test(test_name: str = Form(None), course_id: int = Form(None), user_id: int = Form(None), question: str = Form(None), option_a: str = Form(None), option_b: str = Form(None), option_c: str = Form(None), option_d: str = Form(None), correct_answer: str = Form(None), marks: int = Form(None), user_selected_answer: str = Form(None), active: bool = Form(None)):
    try:
        inputs = {
            'test_name': test_name,
            'course_id': course_id,
            'question': question,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_answer': correct_answer,
            'marks': marks,
            'user_selected_answer': user_selected_answer,
            'active': active
        }

        if add_test_question(user_id, inputs=inputs):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "The Test Question has been added "
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })

@service.get("/fetch_all_tests_by_course_id")
def fetch_all_tests_by_course(course_id: str):
    try:
        tests = get_tests_by_course_id(course_id)

        return {
            "status": "success",
            "data": tests
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch Tests of learner using course_id"
        })
    
@service.get("/fetch_all_questions_by_test_name")
def fetch_all_questions_by_testname(test_name: str):
    try:
        questions = get_question_by_test_names(test_name)

        return {
            "status": "success",
            "data": questions
        }
    except Exception as exc:    
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch questions of test for learner"
        }) 
    
@service.get("/correct_answer")
def fetch_correct_answer(inst_id: int, ler_id: int):
    try:
        answers = get_correct_answer(inst_id, ler_id)

        return {
            "status": "success",
            "data": answers
        }
    except Exception as exc:    
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch answers' of learner"
        }) 

########################################## Assignment Api's ###########################################

@service.post("/add_assignment")
def add_assignment(assignment_name: str = Form(None), course_id: int = Form(None), user_id: int = Form(None), assignment_topic: str = Form(None), complete_by_instructor: bool = Form(None), complete_on_submission: bool = Form(None), assignment_answer: str = Form(None), file: UploadFile = File(None), active: bool = Form(None)):
    # with open("files/"+file.filename, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    # url = str("files/"+file.filename)
    try:
        url = None  # Initialize url to None

        if file:
            # Process the file only if it is provided
            with open("files/" + file.filename, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            url = str("files/" + file.filename)
        inputs = {
            'assignment_name': assignment_name,
            'course_id': course_id,
            'assignment_topic': assignment_topic,
            'complete_by_instructor': complete_by_instructor,
            'complete_on_submission': complete_on_submission,
            'assignment_answer': assignment_answer,
            'file': url,
            'active': active
        }

        if add_assignment_data(user_id, inputs=inputs):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "The Assignment has been added "
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
# Update assignment
@service.post("/update_assignment")
def update_assignments(
    id: int = Form(...),
    course_id: int = Form(...),
    user_id: int = Form(...),
    assignment_name: str = Form(...),
    assignment_topic: str = Form(...),
    complete_by_instructor: bool = Form(...),
    complete_on_submission: bool = Form(...),
    assignment_answer: str = Form(None),
    active: bool = Form(...),
    file: UploadFile = File(None)  # Make file parameter optional
):
    try:
        # url = None  # Initialize url to None

        if file:
            # Process the file only if it is provided
            with open("files/" + file.filename, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            url = str("files/" + file.filename)

        if change_assignment_details(id, course_id, user_id, assignment_name, assignment_topic, complete_by_instructor, complete_on_submission, assignment_answer, active, url):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Assignment successfully"
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })

@service.get("/assignments")
def fetch_all_assignments():
    try:
        # Fetch all assignments' data here
        assignment = fetch_all_assignment_data()

        return {
            "status": "success",
            "data": assignment
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch assignments' data"
        })

@service.post("/submit_assignment_result")
def add_assignment_result(course_id: int = Form(None), user_id: int = Form(None), submission_status: str = Form(None), grade: int = Form(None), comment: str = Form(None), active: bool = Form(None)):
    try:
        inputs = {
            'course_id': course_id,
            'submission_status': submission_status,
            'grade': grade,
            'comment': comment,
            'active': active
        }

        if check_assignment(user_id, inputs=inputs):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "The Assignment has been Checked and Grade has been Given to Learner "
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.post("/update_submission")
def update_submissions(
    id: int = Form(...),
    course_id: int = Form(...),
    user_id: int = Form(...),
    submission_status: str = Form(...),
    grade: str = Form(...),
    comment: str = Form(...),
    active: bool = Form(...)
):
    try:
        if change_submission_details(id, course_id, user_id, submission_status, grade, comment, active):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Submission Successfully"
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.get("/pre_assignment_for_course_content")
def fetch_assignment_for_learner_in_course_content(course_id):
    try:
        # Fetch all assignments' data here
        assignment = fetch_assignment_for_learner(course_id)

        return {
            "status": "success",
            "data": assignment
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch assignments' data"
        })
    
@service.get("/post_assignments_data_for_checking")
def fetch_assignment_done_by_learner(user_id):
    try:
        # Fetch all assignments' data here
        assignment = fetch_assignments_done_from_learner(user_id)

        return {
            "status": "success",
            "data": assignment
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch assignment's completed by Learner's"
        })
    
############################################# Instructor-Led-Training ###########################################

@service.post("/add_instructor-led_training")
def add_instructor_led_training(session_name: str = Form(None), date: str = Form(None), starttime: str = Form(None), capacity: str = Form(None), instructor: str = Form(None), session_type: str = Form(None), duration: str = Form(None), description: str = File(None)):
    try:
        inputs = {
            'session_name': session_name,
            'date': date,
            'starttime': starttime,
            'capacity': capacity,
            'instructor': instructor,
            'session_type': session_type,
            'duration': duration,
            'description': description
        }

        if add_inst_led_training(instructor, inputs=inputs):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "The Instructor-Led-Training has been added "
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
# Update Instructor-Led-Training
@service.post("/update_inst_led_training")
def update_inst_led_training(
    id: int = Form(...),
    session_name: str = Form(...),
    date: str = Form(...),
    starttime: str = Form(...),
    capacity: str = Form(...),
    instructor: str = Form(...),
    session_type: str = Form(...),
    duration: str = Form(...),
    description: str = Form(...)
):
    try:
        if change_instructor_led_details(id, session_name, date, starttime, capacity, instructor, session_type, duration, description):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated Instructor-Led-Training successfully"
            })

    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
    
@service.get("/fetch_inst_led_training")
def fetch_inst_led_training_by_session_name(session_name):
    try:
        inst_led_training = fetch_inst_led_by_session_name(session_name)

        return {
            "status": "success",
            "data": inst_led_training
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch inst_led_training's"
        })
    
@service.delete('/delete_inst_led_training_byid')
async def Delete_Inst_led_training(id: int = Form(...)):
    try:
        result = delete_instructor_led_by_id(id)
        return {
            "status": "success",
            "message": "Instructor-Led-Training deleted successfully"
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to delete Instructor-Led-Training"
        })