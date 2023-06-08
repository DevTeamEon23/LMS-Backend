import traceback
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from starlette.requests import Request

from .auth_ops import  verify_token, get_user_by_token, admin_add_new_user
from .auth_ops import add_new_user, change_user_password, flush_tokens
from config.logconfig import logger

from schemas.auth_schema import (Email, NewUser, User, UserPassword)
from .authenticators import verify_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication Urls
auth = APIRouter(tags=["Service :  Auth Management"])


# Utility Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def loginResponse(message, active, is_mfa_enabled, request_token, token, details={}):
    if token is None and request_token is None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"status": "failure", 'message': message})
    if is_mfa_enabled:
        return {"status": "success", 'message': message, "is_active": active, "is_mfa_enabled": is_mfa_enabled,
                'request_token': request_token, 'error': None}
    else:
        if details.keys():
            user_detail = {
                "user": {
                    "role": details['role'],
                    "data": {
                        "displayName": details['displayName'],
                        "email": details['email'],
                        "photoURL": ""  # details['photoURL']
                    }},
            }
        else:
            user_detail = {}
        return {"status": "success", 'message': message, "is_active": active, "is_mfa_enabled": is_mfa_enabled, "token": token,
                'data': user_detail, 'error': None}


@auth.post('/login')
def login(user: User):
    message, active, is_mfa_enabled, request_token, token, details = add_new_user(user.email, password=user.password, auth_token="",
                                                                                  inputs={
                                                                                      'full_name': user.fullname, 'role': 'user',
                                                                                      'users_allowed': '[]', 'active': False,
                                                                                      'picture': ""}, skip_new_user=True)
    return loginResponse(message, active, is_mfa_enabled, request_token, token, details)


@auth.get('/verify-token')
def verify_access_token(request: Request):
    try:
        is_valid, msg, data = verify_token(request.headers['auth-token'])
        if is_valid:
            user = {}
            details = {}
            details['displayName'] = data['full_name']
            details['email'] = data['email']
            # details['photoURL'] = "assets/images/avatars/brian-hughes.jpg"
            details['photoURL'] = ""
            user['role'] = data['role']

            user['user'] = {}
            user['user']['role'] = data['role']
            user['user']['data'] = details

            return {"status": "success", 'message': "", 'token': request.headers['auth-token'], 'data': user}

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Invalid Token"
        })

    except Exception as exc:
        logger.error(exc.args[0])
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": ""
        })


@auth.post("/logout", status_code=status.HTTP_200_OK)
def logout(request: Request):
    try:
        if flush_tokens(request.headers['auth-token']):
            return {
                "message": "User Logged out successfully"
            }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": ""
        })


# add user
@auth.post("/signup")
def signup(user: NewUser):
    try:
        return admin_add_new_user(user.email, generate_tokens=user.generate_token, password=user.password, auth_token="", inputs={
            'full_name': user.fullname, 'role': 'user', 'users_allowed': '[]', 'active': False, 'picture': "", "password": None})
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User is not registered"
        })


# Update the user Password
@auth.post("/change-user-password", dependencies=[Depends(verify_user)])
def change_password(request: Request, payload: UserPassword):
    user = get_user_by_token(request.headers['auth-token'])
    try:
        if change_user_password(payload.email, payload.password, user):
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
