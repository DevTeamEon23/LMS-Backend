import os
import secrets
import shutil
import random
import base64
import json
from enum import Enum
from typing import List
import traceback
from fastapi import HTTPException
from fastapi.responses import FileResponse
from routers.db_ops import execute_query
from passlib.context import CryptContext
from config.db_config import n_table_user,Base,table_course,table_lmsgroup,table_category,table_lmsevent,table_classroom,table_conference,table_virtualtraining,table_discussion,table_calender
from config.logconfig import logger
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import AddUser
from starlette.responses import JSONResponse
from starlette import status
from sqlalchemy.schema import Column
from sqlalchemy import String, Integer, Text, Enum, Boolean
from sqlalchemy_utils import EmailType, URLType
from ..authenticators import get_user_by_token
from utils import md5, random_string, validate_email,validate_emails

# This is used for the password hashing and validation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

save_file_path = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/{user.file}"

imgpath = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/"

course_file_path = "C:/Users/Admin/Desktop/TEST_projects/All_FastAPI_Projects/fastapi/course/${item.file}"

coursevideo_file_path = "C:/Users/Admin/Desktop/TEST_projects/All_FastAPI_Projects/fastapi/coursevideo/${item.file}"

def sample_data(payload):
    logger.info(payload)
    return {
        "A":random.randint(100,1500),
    }

def get_password_hash(password):
    return pwd_context.hash(password)

def create_token(email):
    base = random_string(8) + email + random_string(8)
    token = md5(base)
    return token

def create_course_token(coursename):
    base = random_string(8) + coursename + random_string(8)
    token = md5(base)
    return token

def create_group_token(groupname):
    base = random_string(8) + groupname + random_string(8)
    token = md5(base)
    return token

def create_category_token(name):
    base = random_string(8) + name + random_string(8)
    token = md5(base)
    return token

def create_event_token(ename):
    base = random_string(8) + ename + random_string(8)
    token = md5(base)
    return token

def create_classroom_token(classname):
    base = random_string(8) + classname + random_string(8)
    token = md5(base)
    return token

def create_conference_token(confname):
    base = random_string(8) + confname + random_string(8)
    token = md5(base)
    return token

def create_virtualtraining_token(virtualname):
    base = random_string(8) + virtualname + random_string(8)
    token = md5(base)
    return token

def create_discussion_token(topic):
    base = random_string(8) + topic + random_string(8)
    token = md5(base)
    return token

def create_calender_token(cal_eventname):
    base = random_string(8) + cal_eventname + random_string(8)
    token = md5(base)
    return token

def random_password(password_length=12):
    return secrets.token_urlsafe(password_length)

def fetch_all_users_data():
    try:
        # Query all users from the database
        users = LmsHandler.get_all_users()

        # Transform the user objects into a list of dictionaries
        users_data = []
        for user in users:

            user_data = {
                "id": user.id,
                "eid": user.eid,
                "sid": user.sid,
                "full_name": user.full_name,
                "email": user.email,
                "dept": user.dept,
                "adhr": user.adhr,
                "username": user.username,
                "bio": user.bio,
                "file": user.file,
                "role": user.role,
                "timezone": user.timezone,
                "langtype": user.langtype,
                "active": True if user.active == 1 else False,
                "deactive": True if user.deactive == 1 else False,
                "exclude_from_email": True if user.exclude_from_email == 1 else False,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                # Include other user attributes as needed
            }

            users_data.append(user_data)

        return users_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch users data"
        })

def get_image(file: str):
    imgpath = "C:/Users/Admin/Desktop/LIVE/LMS-Backend/media/"
    image_path = os.path.join(imgpath, file)
    if os.path.isfile(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    else:
        return {"error": "Image not found"}
    
#Get User data by id for update fields Mapping
def fetch_users_by_onlyid(id):

    try:
        # Query user from the database for the specified id
        user = LmsHandler.get_user_by_id(id)

        if not user:
            # Handle the case when no user is found for the specified id
            return None

        # Transform the user object into a dictionary
        user_data = {
            "id": user.id,
            "eid": user.eid,
            "sid": user.sid,
            "full_name": user.full_name,
            "email": user.email,
            "dept": user.dept,
            "adhr": user.adhr,
            "username": user.username,
            "bio": user.bio,
            "file": user.file,
            "role": user.role,
            "timezone": user.timezone,
            "langtype": user.langtype,
            "active": True if user.active == 1 else False,
            "deactive": True if user.deactive == 1 else False,
            "exclude_from_email": True if user.exclude_from_email == 1 else False,
            # Include other user attributes as needed
        }

        return user_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch user data"
        })

def delete_user_by_id(id):
    try:
        # Delete the user by ID
        users = LmsHandler.delete_users(id)
        return users
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete user data"
        })

# ************************************************   USERS   ***************************************************************

def check_email(email):
    is_valid = validate_email(email)
    if is_valid:
        return str(email).lower()
    else:
        raise ValueError('Invalid email value')

def check_emails(email):
    is_valid = validate_emails(email)
    if is_valid:
        return str(email).lower()
    else:
        raise ValueError('Invalid email value')
    
def check_password(email, password):
    query = f"""
    select * from {n_table_user} where email=%(email)s;
    """
    response = execute_query(query, params={'email': email})
    data = response.fetchone()
    if data is None:
        return False
    else:
        hashed_password = data['password']
        if not pwd_context.verify(password, hashed_password):
            raise ValueError('Invalid Password value')
        return True
    
def check_existing_user(email):
    """
    Only safe to use after the email has been validated
    :param email: email of the user
    :return: bool, bool is_existing, is_authorized
    """
    query = f"""
    select * from {n_table_user} where email=%(email)s;
    """
    response = execute_query(query, params={'email': email})
    data = response.fetchone()

    if data is None:
        return False, False
    else:
        active = data['active']
        return True, active

    
def get_user_details(email):
    """
    Only safe to use after the email has been validated
    :param email: email of the user
    :return: bool, bool
            is_existing, is_authorized
    """
    query = f"""
    select * from {n_table_user} where email=%(email)s;
    """
    response = execute_query(query, params={'email': email})
    data = response.fetchone()
    if data is None:
        return None
    else:
        return data
    
def check_verify_existing_user(email):
    try:
        v_email = check_email(email)
        is_existing, is_active = check_existing_user(v_email)
        response = is_existing
        message = 'User exists' if is_existing else 'User not found or Email Address is invalid'
    except ValueError as exc:
        response = False
        message = exc.args[0]
    return response, message

def generate_email_token_2fact(email, request_token="", skip_check=False):
    if skip_check:
        # Called Internally and cautiously
        exists = True
        msg = 'User exists'
    else:
        exists, msg = check_verify_existing_user(email)

    token = None
    if not exists:
        message = msg
    else:
        token = create_token(email)
        query = f"UPDATE {n_table_user} SET request_token=%(request_token)s, token=%(token)s, updated_at=now() WHERE " \
                f"email=%(email)s ; "
        response = execute_query(
            query, params={'email': email, 'token': token, 'request_token': request_token})
        message = 'token generated'
    return token, message

def exists_users(email, auth_token):
    message, active, token, is_mfa_enabled, request_token, details = None, True, None, False, None, {}
    message = 'User already exists'

    # Create New TokenData
    generate_email_token_2fact(email, skip_check=True)

    # User details
    user = get_user_details(email)
    token = user['token']

    # User account details
    details['displayName'] = user['full_name']
    details['email'] = email
    details['photoURL'] = "assets/images/avatars/brian-hughes.jpg"
    details['role'] = user['role']

    return message, active, token, request_token, details

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

def add_new(email: str,file: bytes,generate_tokens: bool = False, auth_token="", inputs={},password=None, skip_new_user=False):
    try:
        # Check Email Address
        v_email = check_email(email)

        # Check user existence and status
        is_existing, is_active = check_existing_user(v_email)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "User Already Exists"
            })

        elif not is_existing and not is_active and skip_new_user == False:

            eid = inputs.get('eid')
            sid = md5(v_email)
            full_name = inputs.get('full_name', None)
            full_name = v_email.split('@')[0] if full_name is None or full_name == '' else full_name
            email = inputs.get('username')
            dept = inputs.get('email')
            adhr = inputs.get('dept')
            file = inputs.get('file')
            username = inputs.get('adhr')
            bio = inputs.get('bio')
            role = inputs.get('role')
            timezone = inputs.get('timezone')
            langtype = inputs.get('langtype')
            active = inputs.get('active')
            deactive = inputs.get('deactive')
            exclude_from_email = inputs.get('exclude_from_email')

            # Password for manual signing
            if password is None:
                password = random_password()
            if password is None:
                hash_password = ""
            else:
                hash_password = get_password_hash(password)

            # Token Generation
            token = create_token(v_email)

            request_token = ''
            
            # Add New User to the list of users
            data = {'eid': eid, 'sid': sid, 'full_name': full_name, 'email': v_email, 'dept': dept, 'adhr': adhr,'username': username, 'password': hash_password, 'bio': bio,'file': file,
                    'role': role, 'timezone': timezone, 'langtype': langtype, "active": active, "deactive": deactive, "exclude_from_email": exclude_from_email,
                    'users_allowed': inputs.get('users_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_users(data)
            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='User added successfully'))

# for excel import 
def add_new_excel(email: str,generate_tokens: bool = False, auth_token="", inputs={},password=None, skip_new_user=False):
    try:
        # Check Email Address
        v_email = check_email(email)

        # Check user existence and status
        is_existing, is_active = check_existing_user(v_email)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "User Already Exists"
            })

        elif not is_existing and not is_active and skip_new_user == False:

            eid = inputs.get('eid')
            sid = md5(v_email)
            full_name = inputs.get('full_name', None)
            full_name = v_email.split('@')[0] if full_name is None or full_name == '' else full_name
            email = inputs.get('username')
            dept = inputs.get('email')
            adhr = inputs.get('dept')
            username = inputs.get('adhr')
            bio = inputs.get('bio')
            role = inputs.get('role')
            timezone = inputs.get('timezone')
            langtype = inputs.get('langtype')
            active = inputs.get('active')
            deactive = inputs.get('deactive')
            exclude_from_email = inputs.get('exclude_from_email')

            # Password for manual signing
            if password is None:
                password = random_password()
            if password is None:
                hash_password = ""
            else:
                hash_password = get_password_hash(password)

            # Token Generation
            token = create_token(v_email)

            request_token = ''
            
            # Add New User to the list of users
            data = {'eid': eid, 'sid': sid, 'full_name': full_name, 'email': v_email, 'dept': dept, 'adhr': adhr,'username': username, 'password': hash_password, 'bio': bio,
                    'role': role, 'timezone': timezone, 'langtype': langtype, "active": active, "deactive": deactive, "exclude_from_email": exclude_from_email,
                    'users_allowed': inputs.get('users_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_users_excel(data)
            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='User added successfully'))

def change_user_details(id, eid, sid, full_name, dept, adhr, username, email, password, bio, file, role, timezone, langtype, active, deactive, exclude_from_email):
    is_existing, _ = check_existing_user(email)
    if is_existing:
        # Update user password
        if password is None:
            password = random_password()
        password_hash = get_password_hash(password)

        sid = md5(email)
         
        LmsHandler.update_user_to_db(id, eid, sid, full_name, dept, adhr, username,email, password_hash, bio, file, role, timezone, langtype, active, deactive, exclude_from_email)
        #     AWSClient.send_signup(email, password, subject='Password Change')
        return True
    else:
        raise ValueError("User does not exists")


##################################################   COURSES  ###########################################################################

#Function for Add Course to stop the Course name unique voilation
def check_existing_course(coursename):

    query = f"""
    select * from {table_course} where coursename=%(coursename)s;
    """
    response = execute_query(query, params={'coursename': coursename})
    data = response.fetchone()

    if data is None:
        return False, False
    else:
        isActive = data['isActive']
        return True, isActive

#Function for Update Course to check the availabilty for Successfull updation
def check_existing_course_by_id(id):

    query = f"""
    select * from {table_course} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False, False
    else:
        isActive = data['isActive']
        return True, isActive
        
def add_course(coursename: str,file: bytes,coursevideo: bytes,generate_tokens: bool = False, auth_token="", inputs={},skip_new_course=False):
    try:

        # Check user existence and status
        is_existing, is_active = check_existing_course(coursename)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Course Already Exists"
            })

        elif not is_existing and not is_active and skip_new_course == False:

            coursename = inputs.get('coursename', None)
            coursename = coursename.split('@')[0] if coursename is None or coursename == '' else coursename
            file = inputs.get('file')
            description = inputs.get('description')
            coursecode = md5(coursename)
            price = inputs.get('price')
            courselink = inputs.get('courselink')
            coursevideo = inputs.get('coursevideo')
            capacity = inputs.get('capacity')
            startdate = inputs.get('startdate')
            enddate = inputs.get('enddate')
            timelimit = inputs.get('timelimit')
            certificate = inputs.get('certificate')
            level = inputs.get('level')
            category = inputs.get('category')
            isActive = inputs.get('isActive')
            isHide = inputs.get('isHide')

            # Token Generation
            token = create_course_token(coursename)

            request_token = ''
            
            # Add New User to the list of users
            data = {'coursename': coursename,'file': file, 'description': description, 'coursecode': coursecode, 'price':price, 'courselink': courselink, 'coursevideo': coursevideo, 'capacity': capacity, 'startdate': startdate, 'enddate': enddate, 'timelimit': timelimit,
                    'certificate': certificate, 'level': level, 'category': category, 'isActive': isActive, 'isHide': isHide,
                    'course_allowed': inputs.get('course_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_courses(data)
            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Course added successfully'))


def change_course_details(id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
    is_existing, _ = check_existing_course_by_id(id)
    if is_existing:
        # Update courses
         
        LmsHandler.update_course_to_db(id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide)
        #     AWSClient.send_signup(email, password, subject='Password Change')
        return True
    else:
        raise ValueError("Course does not exists")
    
def fetch_all_courses_data():
    try:
        # Query all users from the database
        courses = LmsHandler.get_all_courses()

        # Transform the user objects into a list of dictionaries
        courses_data = []
        for course in courses:

            course_data = {
                "id": course.id,
                "coursename": course.coursename,
                "file": course.file,
                "description": course.description,
                "coursecode": course.coursecode,
                "price": course.price ,
                "courselink": course.courselink,
                "coursevideo": course.coursevideo,
                "capacity": course.capacity,
                "startdate": course.startdate,
                "enddate": course.enddate,
                "timelimit": course.timelimit,
                "certificate": course.certificate,
                "level": course.level,
                "category": course.category,
                "isActive": course.isActive,
                "isHide": course.isHide,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
                # Include other course attributes as needed
            }
            courses_data.append(course_data)

        return courses_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch courses data"
        })
    
#Get Course data by id for update fields Mapping
def fetch_course_by_onlyid(id):

    try:
        # Query category from the database for the specified id
        course = LmsHandler.get_course_by_id(id)

        if not course:
            # Handle the case when no category is found for the specified id
            return None

        # Transform the category object into a dictionary
        course_data = {
                "id": course.id,
                "coursename": course.coursename,
                "file": course.file,
                "description": course.description,
                "coursecode": course.coursecode,
                "price": course.price ,
                "courselink": course.courselink,
                "coursevideo": course.coursevideo,
                "capacity": course.capacity,
                "startdate": course.startdate,
                "enddate": course.enddate,
                "timelimit": course.timelimit,
                "certificate": course.certificate,
                "level": course.level,
                "category": course.category,
                "isActive": course.isActive,
                "isHide": course.isHide,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
            # Include other course attributes as needed
        }

        return course_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch course data"
        })
    
def delete_course_by_id(id):
    try:
        # Delete the course by ID
        courses = LmsHandler.delete_courses(id)
        return courses
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete course data"
        })
    

###################################################   GROUPS   #######################################################################

def check_existing_group(groupname):

    query = f"""
    select * from {table_lmsgroup} where groupname=%(groupname)s;
    """
    response = execute_query(query, params={'groupname': groupname})
    data = response.fetchone()

    if data is None:
        return False, False
    else:
        isActive = data['isActive']
        return True, isActive
        
def check_existing_group_by_id(id):

    query = f"""
    select * from {table_lmsgroup} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False, False
    else:
        isActive = data['isActive']
        return True, isActive
    
def add_group(groupname: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_group=False):
    try:

        # Check user existence and status
        is_existing, is_active = check_existing_group(groupname)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Group Already Exists"
            })

        elif not is_existing and not is_active and skip_new_group == False:

            groupname = inputs.get('groupname', None)
            groupname = groupname.split('@')[0] if groupname is None or groupname == '' else groupname
            groupdesc = inputs.get('groupdesc')
            groupkey = inputs.get('groupkey')

            # Token Generation
            token = create_group_token(groupname)

            request_token = ''
            
            # Add New User to the list of users
            data = {'groupname': groupname, 'groupdesc': groupdesc, 'groupkey': groupkey,
                    'group_allowed': inputs.get('group_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token, 'isActive': True}

            resp = LmsHandler.add_groups(data)
            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Group added successfully'))


def fetch_all_groups_data():
    try:
        # Query all group from the database
        groups = LmsHandler.get_all_groups()

        # Transform the user objects into a list of dictionaries
        groups_data = []
        for group in groups:

            group_data = {
                "id": group.id,
                "groupname": group.groupname,
                "groupdesc": group.groupdesc,
                "groupkey": group.groupkey,
                "created_at": group.created_at,
                "updated_at": group.updated_at,
                # Include other group attributes as needed
            }
            groups_data.append(group_data)

        return groups_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch group data"
        })
    
#Get Group data by id for update fields Mapping
def fetch_group_by_onlyid(id):

    try:
        # Query group from the database for the specified id
        group = LmsHandler.get_group_by_id(id)

        if not group:
            # Handle the case when no group is found for the specified id
            return None

        # Transform the group object into a dictionary
        group_data = {
                "id": group.id,
                "groupname": group.groupname,
                "groupdesc": group.groupdesc,
                "groupkey": group.groupkey,
                "created_at": group.created_at,
                "updated_at": group.updated_at,
            # Include other group attributes as needed
        }

        return group_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch group data"
        })
    
def change_group_details(id, groupname, groupdesc, groupkey):
    is_existing, _ = check_existing_group_by_id(id)
    if is_existing:
        # Update courses
         
        LmsHandler.update_group_to_db(id, groupname, groupdesc, groupkey)
        #     AWSClient.send_signup(email, password, subject='Password Change')
        return True
    else:
        raise ValueError("Group does not exists")
    

def delete_group_by_id(id):
    try:
        # Delete the group by ID
        groups = LmsHandler.delete_groups(id)
        return groups
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete group data"
        })
    
########################################################################################################################

def check_existing_category(name):

    query = f"""
    select * from {table_category} where name=%(name)s;
    """
    response = execute_query(query, params={'name': name})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_category_by_id(id):

    query = f"""
    select * from {table_category} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_category(name: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check user existence and status
        is_existing = check_existing_category(name)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Category Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            name = inputs.get('name', None)
            name = name.split('@')[0] if name is None or name == '' else name
            price = inputs.get('price')

            # Token Generation
            token = create_category_token(name)

            request_token = ''
            
            # Add New User to the list of users
            data = {'name': name, 'price': price,
                    'category_allowed': inputs.get('category_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token }

            resp = LmsHandler.add_category(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Category added successfully'))


def fetch_all_categories_data():
    try:
        # Query all group from the database
        categories = LmsHandler.get_all_categories()

        # Transform the category objects into a list of dictionaries
        categories_data = []
        for category in categories:

            category_data = {
                "id": category.id,
                "name": category.name,
                "price": category.price,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                # Include other group attributes as needed
            }
            categories_data.append(category_data)

        return categories_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch category data"
        })
    
#Get Category data by id for update fields Mapping
def fetch_category_by_onlyid(id):

    try:
        # Query category from the database for the specified id
        category = LmsHandler.get_category_by_id(id)

        if not category:
            # Handle the case when no category is found for the specified id
            return None

        # Transform the category object into a dictionary
        category_data = {
            "id": category.id,
            "name": category.name,
            "price": category.price,
            # Include other category attributes as needed
        }

        return category_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch category data"
        })
    

def change_category_details(id, name, price):
    is_existing = check_existing_category_by_id(id)
    if is_existing:
        # Update category
         
        LmsHandler.update_category_to_db(id, name, price)
        #     AWSClient.send_signup(email, password, subject='Password Change')
        return True
    else:
        raise ValueError("Category does not exists")
    

def delete_category_by_id(id):
    try:
        # Delete the category by ID
        categories = LmsHandler.delete_category(id)
        return categories
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete category data"
        })
    

##########################################################################################################################

def check_existing_event(ename):

    query = f"""
    select * from {table_lmsevent} where ename=%(ename)s;
    """
    response = execute_query(query, params={'ename': ename})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_event_by_id(id):

    query = f"""
    select * from {table_lmsevent} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_event(ename: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check user existence and status
        is_existing = check_existing_event(ename)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Events Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            ename = inputs.get('ename', None)
            ename = ename.split('@')[0] if ename is None or ename == '' else ename
            eventtype = inputs.get('eventtype')
            recipienttype = inputs.get('recipienttype')
            descp = inputs.get('descp')

            # Token Generation
            token = create_event_token(ename)

            request_token = ''
            
            # Add New User to the list of users
            data = {'ename': ename, 'eventtype': eventtype, 'recipienttype': recipienttype, 'descp': descp,
                    'event_allowed': inputs.get('event_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token, 'isActive': True }

            resp = LmsHandler.add_event(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Event added successfully'))


def fetch_all_events_data():
    try:
        # Query all group from the database
        events = LmsHandler.get_all_events()

        # Transform the category objects into a list of dictionaries
        events_data = []
        for event in events:

            event_data = {
                "id": event.id,
                "ename": event.ename,
                "eventtype": event.eventtype,
                "recipienttype": event.recipienttype,
                "created_at": event.created_at,
                "updated_at": event.updated_at,
                # Include other event attributes as needed
            }
            events_data.append(event_data)

        return events_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch events data"
        })
    
#Get Event data by id for update fields Mapping
def fetch_event_by_onlyid(id):

    try:
        # Query event from the database for the specified id
        event = LmsHandler.get_event_by_id(id)

        if not event:
            # Handle the case when no event is found for the specified id
            return None

        # Transform the event object into a dictionary
        event_data = {
                "id": event.id,
                "ename": event.ename,
                "eventtype": event.eventtype,
                "recipienttype": event.recipienttype,
                "created_at": event.created_at,
                "updated_at": event.updated_at,
            # Include other event attributes as needed
        }

        return event_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch event data"
        })
    
def change_event_details(id, ename, eventtype,recipienttype,descp):
    is_existing = check_existing_event_by_id(id)
    if is_existing:
        # Update event
         
        LmsHandler.update_event_to_db(id, ename, eventtype,recipienttype,descp)
        return True
    else:
        raise ValueError("Event does not exists")
    

def delete_event_by_id(id):
    try:
        # Delete the event by ID
        events = LmsHandler.delete_event(id)
        return events
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete event data"
        })
        
##########################################################################################################################

def check_existing_classroom(classname):

    query = f"""
    select * from {table_classroom} where classname=%(classname)s;
    """
    response = execute_query(query, params={'classname': classname})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_classroom_by_id(id):

    query = f"""
    select * from {table_classroom} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_classroom(classname: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check user existence and status
        is_existing = check_existing_classroom(classname)

        # If user Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Classroom Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            instname = inputs.get('instname')
            classname = inputs.get('classname')
            date = inputs.get('date')
            starttime = inputs.get('starttime')
            venue = inputs.get('venue')
            messg = inputs.get('messg')
            duration = inputs.get('duration')

            # Token Generation
            token = create_classroom_token(classname)

            request_token = ''
            
            # Add New User to the list of users
            data = {'instname': instname,'classname': classname, 'date': date, 'starttime': starttime, 'venue': venue, 'messg': messg, 'duration': duration,
                    'classroom_allowed': inputs.get('classroom_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_classroom(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Classroom added successfully'))


def fetch_all_classroom_data():
    try:
        # Query all classroom from the database
        classrooms = LmsHandler.get_all_classrooms()

        # Transform the classroom objects into a list of dictionaries
        classrooms_data = []
        for classroom in classrooms:

            classroom_data = {
                "id": classroom.id,
                "instname": classroom.instname,
                "classname": classroom.classname,
                "date": classroom.date,
                "starttime": classroom.starttime,
                "venue": classroom.venue,
                "messg": classroom.messg,
                "duration": classroom.duration,
                "created_at": classroom.created_at,
                "updated_at": classroom.updated_at,
                # Include other classroom attributes as needed
            }
            classrooms_data.append(classroom_data)

        return classrooms_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch classrooms data"
        })
    
#Get Classroom data by id for update fields Mapping
def fetch_classroom_by_onlyid(id):

    try:
        # Query classroom from the database for the specified id
        classroom = LmsHandler.get_classroom_by_id(id)

        if not classroom:
            # Handle the case when no classroom is found for the specified id
            return None

        # Transform the classroom object into a dictionary
        classroom_data = {
                "id": classroom.id,
                "instname": classroom.instname,
                "classname": classroom.classname,
                "date": classroom.date,
                "starttime": classroom.starttime,
                "venue": classroom.venue,
                "messg": classroom.messg,
                "duration": classroom.duration,
                "created_at": classroom.created_at,
                "updated_at": classroom.updated_at,
            # Include other classroom attributes as needed
        }

        return classroom_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch classroom data"
        })
    
def change_classroom_details(id, instname, classname, date, starttime, venue, messg, duration):
    is_existing = check_existing_classroom_by_id(id)
    if is_existing:
        # Update classroom
         
        LmsHandler.update_classroom_to_db(id, instname, classname, date, starttime, venue, messg, duration)
        return True
    else:
        raise ValueError("Classroom does not exists")
    

def delete_classroom_by_id(id):
    try:
        # Delete the classroom by ID
        classrooms = LmsHandler.delete_classroom(id)
        return classrooms
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete classroom data"
        })
    
##########################################################################################################################

def check_existing_conference(confname):

    query = f"""
    select * from {table_conference} where confname=%(confname)s;
    """
    response = execute_query(query, params={'confname': confname})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_conference_by_id(id):

    query = f"""
    select * from {table_conference} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_conference(confname: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check conference existence and status
        is_existing = check_existing_conference(confname)

        # If conference Already Exists
        if is_existing:
            # Check password
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Conference Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            instname = inputs.get('instname')
            confname = inputs.get('confname')
            date = inputs.get('date')
            starttime = inputs.get('starttime')
            meetlink = inputs.get('meetlink')
            messg = inputs.get('messg')
            duration = inputs.get('duration')

            # Token Generation
            token = create_conference_token(confname)

            request_token = ''
            
            # Add New Conference to the list of Conferences
            data = {'instname': instname,'confname': confname, 'date': date, 'starttime': starttime, 'meetlink': meetlink, 'messg': messg, 'duration': duration,
                    'conference_allowed': inputs.get('conference_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_conference(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Conference added successfully'))


def fetch_all_conference_data():
    try:
        # Query all conference from the database
        conferences = LmsHandler.get_all_conferences()

        # Transform the conference objects into a list of dictionaries
        conferences_data = []
        for conference in conferences:

            conference_data = {
                "id": conference.id,
                "instname": conference.instname,
                "confname": conference.confname,
                "date": conference.date,
                "starttime": conference.starttime,
                "meetlink": conference.meetlink,
                "messg": conference.messg,
                "duration": conference.duration,
                "created_at": conference.created_at,
                "updated_at": conference.updated_at,
                # Include other conference attributes as needed
            }
            conferences_data.append(conference_data)

        return conferences_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch conferences data"
        })
    
#Get Conference data by id for update fields Mapping
def fetch_conference_by_onlyid(id):

    try:
        # Query conferences from the database for the specified id
        conference = LmsHandler.get_conference_by_id(id)

        if not conference:
            # Handle the case when no conference is found for the specified id
            return None

        # Transform the conference object into a dictionary
        conference_data = {
                "id": conference.id,
                "instname": conference.instname,
                "confname": conference.confname,
                "date": conference.date,
                "starttime": conference.starttime,
                "meetlink": conference.meetlink,
                "messg": conference.messg,
                "duration": conference.duration,
                "created_at": conference.created_at,
                "updated_at": conference.updated_at,
            # Include other conference attributes as needed
        }

        return conference_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch conference data"
        })
    
def change_conference_details(id, instname, confname, date, starttime, meetlink, messg, duration):
    is_existing = check_existing_conference_by_id(id)
    if is_existing:
        # Update conference
         
        LmsHandler.update_conference_to_db(id, instname, confname, date, starttime, meetlink, messg, duration)
        return True
    else:
        raise ValueError("Conference does not exists")
    

def delete_conference_by_id(id):
    try:
        # Delete the conference by ID
        conferences = LmsHandler.delete_conference(id)
        return conferences
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete conferences data"
        })
        
##########################################################################################################################

def check_existing_virtualtraining(virtualname):

    query = f"""
    select * from {table_virtualtraining} where virtualname=%(virtualname)s;
    """
    response = execute_query(query, params={'virtualname': virtualname})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_virtualtraining_by_id(id):

    query = f"""
    select * from {table_virtualtraining} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_virtualtraining(virtualname: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check virtualtraining existence and status
        is_existing = check_existing_virtualtraining(virtualname)

        # If virtualtraining Already Exists
        if is_existing:
            # Check virtualtraining
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Virtual Training Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            instname = inputs.get('instname')
            virtualname = inputs.get('virtualname')
            date = inputs.get('date')
            starttime = inputs.get('starttime')
            meetlink = inputs.get('meetlink')
            messg = inputs.get('messg')
            duration = inputs.get('duration')

            # Token Generation
            token = create_virtualtraining_token(virtualname)

            request_token = ''
            
            # Add New Conference to the list of Conferences
            data = {'instname': instname,'virtualname': virtualname, 'date': date, 'starttime': starttime, 'meetlink': meetlink, 'messg': messg, 'duration': duration,
                    'virtualtraining_allowed': inputs.get('virtualtraining_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_virtualtraining(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Virtual Training added successfully'))


def fetch_all_virtualtraining_data():
    try:
        # Query all virtualtraining from the database
        virtualtrainings = LmsHandler.get_all_virtualtrainings()

        # Transform the virtualtraining objects into a list of dictionaries
        virtualtrainings_data = []
        for virtualtraining in virtualtrainings:

            virtualtraining_data = {
                "id": virtualtraining.id,
                "instname": virtualtraining.instname,
                "virtualname": virtualtraining.virtualname,
                "date": virtualtraining.date,
                "starttime": virtualtraining.starttime,
                "meetlink": virtualtraining.meetlink,
                "messg": virtualtraining.messg,
                "duration": virtualtraining.duration,
                "created_at": virtualtraining.created_at,
                "updated_at": virtualtraining.updated_at,
                # Include other virtualtraining attributes as needed
            }
            virtualtrainings_data.append(virtualtraining_data)

        return virtualtrainings_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch virtualtrainings data"
        })
    
#Get Virtual Training data by id for update fields Mapping
def fetch_virtualtraining_by_onlyid(id):

    try:
        # Query virtualtraining from the database for the specified id
        virtualtraining = LmsHandler.get_virtualtraining_by_id(id)

        if not virtualtraining:
            # Handle the case when no virtualtraining is found for the specified id
            return None

        # Transform the virtualtraining object into a dictionary
        virtualtraining_data = {
                "id": virtualtraining.id,
                "instname": virtualtraining.instname,
                "virtualname": virtualtraining.virtualname,
                "date": virtualtraining.date,
                "starttime": virtualtraining.starttime,
                "meetlink": virtualtraining.meetlink,
                "messg": virtualtraining.messg,
                "duration": virtualtraining.duration,
                "created_at": virtualtraining.created_at,
                "updated_at": virtualtraining.updated_at,
            # Include other virtualtraining attributes as needed
        }

        return virtualtraining_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch virtualtraining data"
        })
    
def change_virtualtraining_details(id, instname, virtualname, date, starttime, meetlink, messg, duration):
    is_existing = check_existing_virtualtraining_by_id(id)
    if is_existing:
        # Update virtualtrainings
        LmsHandler.update_virtualtraining_to_db(id, instname, virtualname, date, starttime, meetlink, messg, duration)
        return True
    else:
        raise ValueError("Virtual Training does not exists")
    

def delete_virtualtraining_by_id(id):
    try:
        # Delete the virtualtraining by ID
        virtualtrainings = LmsHandler.delete_virtualtraining(id)
        return virtualtrainings
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete virtualtraining data"
        })
    
##########################################################################################################################

def check_existing_discussion(topic):

    query = f"""
    select * from {table_discussion} where topic=%(topic)s;
    """
    response = execute_query(query, params={'topic': topic})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_discussion_by_id(id):

    query = f"""
    select * from {table_discussion} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_discussion(topic: str,file: bytes,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check discussion existence and status
        is_existing = check_existing_discussion(topic)

        # If discussion Already Exists
        if is_existing:
            # Check discussion
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "Discussion Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            topic = inputs.get('topic')
            messg = inputs.get('messg')
            file = inputs.get('file')
            access = inputs.get('access')

            # Token Generation
            token = create_discussion_token(topic)

            request_token = ''
            
            # Add New Discussion to the list of Discussions
            data = {'topic': topic, 'messg': messg, 'file': file, 'access': access,
                    'discussion_allowed': inputs.get('discussion_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_discussion(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Discussion added successfully'))


def fetch_all_discussion_data():
    try:
        # Query all discussion from the database
        discussions = LmsHandler.get_all_discussions()

        # Transform the discussion objects into a list of dictionaries
        discussions_data = []
        for discussion in discussions:

            discussion_data = {
                "id": discussion.id,
                "instname": discussion.topic,
                "virtualname": discussion.messg,
                "date": discussion.file,
                "starttime": discussion.access,
                "created_at": discussion.created_at,
                "updated_at": discussion.updated_at,
                # Include other discussion attributes as needed
            }
            discussions_data.append(discussion_data)

        return discussions_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch discussions data"
        })
    
#Get Discussion data by id for update fields Mapping
def fetch_discussion_by_onlyid(id):

    try:
        # Query discussion from the database for the specified id
        discussion = LmsHandler.get_discussion_by_id(id)

        if not discussion:
            # Handle the case when no discussion is found for the specified id
            return None

        # Transform the discussion object into a dictionary
        discussion_data = {
                "id": discussion.id,
                "instname": discussion.topic,
                "virtualname": discussion.messg,
                "date": discussion.file,
                "starttime": discussion.access,
                "created_at": discussion.created_at,
                "updated_at": discussion.updated_at,
            # Include other discussion attributes as needed
        }

        return discussion_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch discussion data"
        })
    
def change_discussion_details(id, topic, messg, file, access):
    is_existing = check_existing_discussion_by_id(id)
    if is_existing:
        # Update discussions
        LmsHandler.update_discussion_to_db(id, topic, messg, file, access)
        return True
    else:
        raise ValueError("Discussion does not exists")
    

def delete_discussion_by_id(id):
    try:
        # Delete the discussion by ID
        discussions = LmsHandler.delete_discussion(id)
        return discussions
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete discussion data"
        })
    
##########################################################################################################################

def check_existing_calender(cal_eventname):

    query = f"""
    select * from {table_calender} where cal_eventname=%(cal_eventname)s;
    """
    response = execute_query(query, params={'cal_eventname': cal_eventname})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
        
def check_existing_calender_by_id(id):

    query = f"""
    select * from {table_calender} where id=%(id)s;
    """
    response = execute_query(query, params={'id': id})
    data = response.fetchone()

    if data is None:
        return False
    else:
        return True
    
def add_calender(cal_eventname: str,generate_tokens: bool = False, auth_token="", inputs={},skip_new_category=False):
    try:

        # Check calender existence and status
        is_existing = check_existing_calender(cal_eventname)

        # If calender Already Exists
        if is_existing:
            # Check calender
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
                "message": "calender Already Exists"
            })

        elif not is_existing and skip_new_category == False:

            cal_eventname = inputs.get('cal_eventname')
            date = inputs.get('date')
            starttime = inputs.get('starttime')
            duration = inputs.get('duration')
            audience = inputs.get('audience')
            messg = inputs.get('messg')

            # Token Generation
            token = create_calender_token(cal_eventname)

            request_token = ''
            
            # Add New calender to the list of calenders
            data = {'cal_eventname': cal_eventname, 'date': date, 'starttime': starttime, 'duration': duration, 'audience': audience, 'messg': messg,
                    'calender_allowed': inputs.get('calender_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token}

            resp = LmsHandler.add_calender(data)
            # # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='success',message='Calender added successfully'))


def fetch_all_calender_data():
    try:
        # Query all calender from the database
        calenders = LmsHandler.get_all_calenders()

        # Transform the calender objects into a list of dictionaries
        calenders_data = []
        for calender in calenders:

            calender_data = {
                "id": calender.id,
                "cal_eventname": calender.cal_eventname,
                "date": calender.date,
                "starttime": calender.starttime,
                "duration": calender.duration,
                "audience": calender.audience,
                "messg": calender.messg,
                "created_at": calender.created_at,
                "updated_at": calender.updated_at,
                # Include other calender attributes as needed
            }
            calenders_data.append(calender_data)

        return calenders_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch Calenders data"
        })
    
#Get Calender data by id for update fields Mapping
def fetch_calender_by_onlyid(id):

    try:
        # Query Calender from the database for the specified id
        calender = LmsHandler.get_calender_by_id(id)

        if not calender:
            # Handle the case when no Calender is found for the specified id
            return None

        # Transform the Calender object into a dictionary
        calender_data = {
                "id": calender.id,
                "cal_eventname": calender.cal_eventname,
                "date": calender.date,
                "starttime": calender.starttime,
                "duration": calender.duration,
                "audience": calender.audience,
                "messg": calender.messg,
                "created_at": calender.created_at,
                "updated_at": calender.updated_at,
            # Include other Calender attributes as needed
        }

        return calender_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch Calender data"
        })
    
def change_calender_details(id, cal_eventname, date, starttime, duration, audience, messg):
    is_existing = check_existing_calender_by_id(id)
    if is_existing:
        # Update calenders
        LmsHandler.update_calender_to_db(id, cal_eventname, date, starttime, duration, audience, messg)
        return True
    else:
        raise ValueError("Calender does not exists")
    
def delete_calender_by_id(id):
    try:
        # Delete the calender by ID
        calenders = LmsHandler.delete_calender(id)
        return calenders
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to delete Calender data"
        })
    