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
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,delete_user_by_id,change_user_details,add_new
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser,Users, UserDetail)
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
            "message": "User is not registered"
        })

# @service.post("/addusers")
# def add_users(eid: str = Form(...),sid: str = Form(...), full_name: str = Form(...), email: str = Form(...),dept: str = Form(...), adhr: str = Form(...), username: str = Form(...), password: str = Form(...),bio: str = Form(...), role: str = Form(...), timezone: str = Form(...), langtype: str = Form(...), active: bool = Form(...), deactive: bool = Form(...), exclude_from_email: bool = Form(...), generate_token: bool = Form(...),file: UploadFile = File(...), db: Session = Depends(get_database_session)):
#     with open("media/"+file.filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     url = str("media/"+file.filename)
#     try:
#         return add_new(email, generate_token,password=password, auth_token="", inputs={
#             'eid': eid,'sid': sid,'full_name': full_name,'email': email,'dept': dept,'adhr': adhr,'username': username,'bio': bio,'file': url,'role': role, 'timezone': timezone, 'langtype': langtype,'users_allowed': '[]', 'active': active, 'deactive': deactive, 'exclude_from_email': exclude_from_email, 'picture': "", "password": None})
#     except Exception as exc: 
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "User is not registered"
#         })
# @service.post("/addusers")
# def add_users(user: Users = Form(...), file: UploadFile = File(...)):
#     user_dict = json.loads(user)
#     with open("media/" + file.filename, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     url = str("media/" + file.filename)
#     try:
#         return add_new(user_dict['email'], generate_tokens=user_dict['generate_token'], password=user_dict['password'], auth_token="", inputs={
#             'eid': user_dict['eid'], 'sid': user_dict['sid'], 'full_name': user_dict['fullname'], 'dept': user_dict['dept'],
#             'adhr': user_dict['adhr'], 'username': user_dict['username'], 'bio': user_dict['bio'], 'file': url,
#             'role': user_dict['role'], 'timezone': user_dict['timezone'], 'langtype': user_dict['langtype'],
#             'users_allowed': '[]', 'active': user_dict['active'], 'deactive': user_dict['deactive'],
#             'exclude_from_email': user_dict['exclude_from_email'], 'picture': "", "password": None})
#     except Exception as exc:
#         logger.error(traceback.format_exc())
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
#             "status": "failure",
#             "message": "User is not registered"
#         })
    
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
    
# Update the user Password
@service.post("/change-password-setting", dependencies=[Depends(verify_user)])
def update_users(request: Request, payload: UserDetail):
    user = get_user_by_token(request.headers['auth-token'])
    try:
        if change_user_details(payload.email, payload.password,payload.eid, payload.sid, user):
            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "status": "success",
                "message": "Updated password successfully"
            })
    except ValueError as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "status": "failure",
            "message": exc.args[0]
        })
