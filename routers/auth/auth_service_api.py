import traceback
import json
import random
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from passlib.context import CryptContext
from starlette.requests import Request
from routers.auth.auth_db_ops import UserDBHandler
from ..authenticators import get_user_by_token,verify_email,get_user_by_email
from .auth_service_ops import verify_token, admin_add_new_user,add_new_user, change_user_password, flush_tokens
from config.logconfig import logger
from dotenv import load_dotenv
from schemas.auth_service_schema import (Email, NewUser, User,EmailSchema, UserPassword)
from routers.authenticators import verify_user
import os
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication Urls
auth = APIRouter(tags=["Service :  Auth Management"])

load_dotenv()

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

# Login API
@auth.post('/login')
def login(user: User):
    message, active, is_mfa_enabled, request_token, token, details = add_new_user(user.email, password=user.password, auth_token="",
                                                                                  inputs={
                                                                                      'full_name': user.fullname, 'role': 'user',
                                                                                      'users_allowed': '[]', 'active': False,
                                                                                      'picture': ""}, skip_new_user=True)
    return loginResponse(message, active, is_mfa_enabled, request_token, token, details)

# Token Verification for Other apis
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


# Signup 
@auth.post("/signup")
def signup(user: NewUser):
    try:
        return admin_add_new_user(user.email, generate_tokens=user.generate_token, password=user.password, auth_token="", inputs={
            'full_name': user.fullname, 'role': 'Learner', 'users_allowed': '[]', 'active': False, 'picture': "", "password": None})
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "User is not registered"
        })


# Reset Password 
@auth.post("/change-user-password")
def change_password(payload: UserPassword):
    try:
        if change_user_password(payload.email, payload.password):
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

# Logout
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


# Forgot Password Send OTP on Mail-Id
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

@auth.post("/send_mail")
async def send_mail(email: EmailSchema):
    user = get_user_by_email(email.email[0])  # Assuming only one email is provided in the list

    # Check if the user is found (email is registered)
    try:
        user_data = get_user_by_email(email.email[0])
    except Exception as exc:
        return JSONResponse(status_code=401, content={
            "status": "failure",
            "message": "Email is not registered"
        })

    # Generate 4-digit OTP
    otp = str(random.randint(1000, 9999))

    template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>EonLearning LMS</title>
        </head>
        <body>
            <!-- partial:index.partial.html -->
            <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
                <div style="margin:50px auto;width:70%;padding:20px 0">
                    <div style="border-bottom:1px solid #eee">
                        <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Reset your EonLearning LMS password</a>
                    </div>
                    <p style="font-size:1.1em">Hi,</p>
                    <p>Thank you for choosing EonLearning LMS. Use the following OTP to complete your Password Recovery Procedure. OTP is valid for 5 minutes</p>
                    <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{otp}</h2>
                    <p style="font-size:0.9em;">Thanks & Regards,<br />The EonLearning Team</p>
                    <hr style="border:none;border-top:1px solid #eee" />
                    <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                        <p>EonLearning LMS Inc</p>
                        <p>Dalal Street</p>
                        <p>Mumbai-400001</p>
                    </div>
                </div>
            </div>
            <!-- partial -->
        </body>
        </html>
    """
    
    # Replace {otp} with the generated OTP
    template = template.replace("{otp}", otp)

    message = MessageSchema(
        subject="[EonLearning] OTP For Reset Password",
        recipients=email.email,
        body=template,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print(message)

    return JSONResponse(status_code=200, content={"status": "success","message": "Email has been sent","OTP":otp})