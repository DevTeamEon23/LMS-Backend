import traceback
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request
from schemas.lms_service_schema import DeleteUser
from routers.authenticators import verify_user
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data,delete_user_by_id,change_user_details,add_new
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import (Email,CategorySchema, AddUser, UserDetail)
from utils import success_response
from config.logconfig import logger


service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])


@service.post("/list-data")
def get_list_data(payload:CategorySchema):
    return success_response(status_code=status.HTTP_200_OK, data=sample_data(payload))

@service.post("/addusers")
def add_users(user: AddUser):
    try:
        return add_new(user.email, generate_tokens=user.generate_token, password=user.password, auth_token="", inputs={
            'eid': user.eid,'sid': user.sid, 'full_name': user.full_name, 'dept': user.dept, 'adhr': user.adhr,'bio': user.bio, 'file': user.file,'role': user.role, 'timezone': user.timezone,'langtype': user.langtype, 'users_allowed': '[]', 'active': user.active, 'deactive': user.deactive, 'exclude_from_email': user.exclude_from_email, 'picture': "", "password": None})
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User is not registered"
        })
    
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
