import secrets
from datetime import datetime

import jwt
import traceback

from dateutil.relativedelta import relativedelta
from fastapi import Header, HTTPException
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse

from config.db_config import n_table_user
from config import settings
from config.logconfig import logger
from routers.auth.auth_db_ops import UserDBHandler
from routers.db_ops import execute_query
from utils import md5, random_string, validate_email

# This is used for the password hashing and validation
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_email(email):
    is_valid = validate_email(email)
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


def generate_token(email):
    base = random_string(8) + email + random_string(8)
    token = md5(base)
    return token


def get_password_hash(password):
    return pwd_context.hash(password)


def random_password(password_length=12):
    return secrets.token_urlsafe(password_length)


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


def get_token(email):
    """
    Only safe to use after the email has been validated
    :param email: email of the user
    :return: str
    """
    query = f"""
    select * from {n_table_user} where email=%(email)s;
    """
    response = execute_query(query, params={'email': email})
    data = response.fetchone()
    if data is None:
        return None
    else:
        return data.token


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


def generate_email_token(email, auth_token, skip_check=False):
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
        token = generate_token(email)
        query = f"UPDATE {n_table_user} SET auth_token=%(auth_token)s, token=%(token)s, updated_at=now() WHERE email=%(email)s;"
        response = execute_query(query, params={'email': email, 'token': token, 'auth_token': auth_token})
        message = 'token generated' if response.rowcount >= 1 else 'token not updated'
    return token, message


def get_email_token(email, pwd=None):
    exists, msg = check_verify_existing_user(email)
    token = None
    if not exists:
        message = msg
    else:
        token = get_token(email)
        message = ''
    return token, message


def verify_token(token):
    data = None
    if token is not None:
        # No checks on token might be a vulnerability
        query = f"SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()

    if data is None:
        response = False
        message = 'Not Authenticated'
    else:
        response = True
        message = 'Authenticated'
    return response, message, data


def destroy_token(token):
    if token is not None and token != '':
        query = f"UPDATE {n_table_user} SET token='' where token=%(token)s;"
        resp = execute_query(query=query, params={'token': token})
        data = bool(resp.rowcount)
        return data
    else:
        return True


def exists_user_details(email, auth_token):
    message, active, token, is_mfa_enabled, request_token, details = None, True, None, False, None, {}
    message = 'User already exists'

    # Create New TokenData
    generate_email_token_2fa(email, skip_check=True)

    # User details
    user = get_user_details(email)
    token = user['token']

    # User account details
    details['displayName'] = user['full_name']
    details['email'] = email
    details['photoURL'] = "assets/images/avatars/brian-hughes.jpg"
    details['role'] = user['role']

    return message, active, token, request_token, details


def generate_email_token_2fa(email, request_token="", skip_check=False):
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
        token = generate_token(email)
        query = f"UPDATE {n_table_user} SET request_token=%(request_token)s, token=%(token)s, updated_at=now() WHERE " \
                f"email=%(email)s ; "
        response = execute_query(
            query, params={'email': email, 'token': token, 'request_token': request_token})
        message = 'token generated'
    return token, message

# FETCHING ID for Profile page data fullfillment
def fetch_user_id_from_db(email: str) -> int:
    query = f"SELECT id FROM {n_table_user} WHERE email = %(email)s"
    params = {'email': email}
    result = execute_query(query, params=params)  # Modify this line to match your execute_query function
    
    # Iterate over the MappingResult to extract the user IDs
    user_ids = [row['id'] for row in result]
    
    return user_ids[0] if user_ids else None

def add_new_user(email: str, generate_tokens: bool = False, auth_token="", inputs={}, password=None, skip_new_user=False):
    message, active, is_mfa_enabled, request_token, token, details = None, False, False, None, None, {}
    try:
        # Check Email Address
        v_email = check_email(email)

        # Check user existence and status
        is_existing, is_active = check_existing_user(v_email)

        # If user Already Exists
        if is_existing and is_active:
            # Check password
            if password is not None:
                check_password(email, password)

            message, active, token, request_token, details = exists_user_details(email, auth_token)

        # If user exsist and is not active
        elif is_existing and not is_active:
            # Check password
            if password is not None:
                check_password(email, password)
            message = 'User not activated'
            active = is_active
        elif skip_new_user:
            message = 'User not Found or Email Address is invalid'

        elif not is_existing and not is_active and skip_new_user == False:

            username = md5(v_email)
            full_name = inputs.get('full_name', None)
            full_name = v_email.split('@')[0] if full_name is None or full_name == '' else full_name

            # Password for manual signing
            if password is None:
                password = random_password()
            if password is None:
                hash_password = ""
            else:
                hash_password = get_password_hash(password)

            # Token Generation
            token = generate_token(v_email)

            request_token = ''

            # Add New User to the list of users
            data = {'full_name': full_name, 'username': username, 'email': v_email, 'password': hash_password,
                    'role': inputs.get('role', 'Learner'),
                    'users_allowed': inputs.get('users_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token, 'active': False}

            resp = UserDBHandler.add_user_to_db(data)
            message = 'User added successfully. Not activated.'
            active = False

            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return message, active, is_mfa_enabled, request_token, token, details


def admin_add_new_user(email: str, generate_tokens: bool = False, auth_token="", inputs={}, password=None, skip_new_user=False):
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

            username = md5(v_email)
            full_name = inputs.get('full_name', None)
            full_name = v_email.split('@')[0] if full_name is None or full_name == '' else full_name

            # Password for manual signing
            if password is None:
                password = random_password()
            if password is None:
                hash_password = ""
            else:
                hash_password = get_password_hash(password)

            # Token Generation
            token = generate_token(v_email)

            request_token = ''

            # Add New User to the list of users
            data = {'full_name': full_name, 'username': username, 'email': v_email, 'password': hash_password,
                    'role': inputs.get('role', 'Learner'),
                    'users_allowed': inputs.get('users_allowed', ''), 'auth_token': auth_token,
                    'request_token': request_token, 'token': token, 'active': True, }

            resp = UserDBHandler.add_user_to_db(data)
            # If token not required,
            if not generate_tokens and len(auth_token) == 0:
                token = None

    except ValueError as exc:
        logger.error(traceback.format_exc())
        message = exc.args[0]
        logger.error(message)

    return JSONResponse(status_code=status.HTTP_200_OK, content=dict(status='Success',message='User added successfully'))


def generate_request_token(email):
    """
    The generate_request_token function takes in an email address and returns a JWT token.
    The token is valid for 120 seconds, after which it expires.

    :param email: Identify the user
    :return: A token string

    """
    payload = {'email': email, 'exp': datetime.utcnow() + relativedelta(seconds=120)}
    token = jwt.encode(payload=payload, key=settings.JWT_SECRECT, algorithm='HS256')
    return token


def verify_request_token(request_token):
    valid, email, msg = False, None, None
    if request_token:
        try:
            decoded = jwt.decode(request_token, key=settings.JWT_SECRECT,
                                 algorithms=['HS256'], leeway=10)
            email = decoded['email']
            msg = "Valid Token"
            valid = True
        except (jwt.InvalidSignatureError, jwt.InvalidTokenError):
            msg = 'Invalid Token'
        except jwt.ExpiredSignatureError:
            msg = 'Token Expired'
        except Exception as exc:
            msg = "Couldn't verify token"
            logger.error(
                f'Unknown error while request token verification: {exc}')

    else:
        msg = "Invalid params or empty values provided"
    return valid, email, msg


def change_user_password(email, password):
    is_existing, _ = check_existing_user(email)
    if is_existing:
        # Update user password
        if password is None:
            password = random_password()
        password_hash = get_password_hash(password)
        UserDBHandler.change_password(email, password_hash)
        #     AWSClient.send_signup(email, password, subject='Password Change')
        return True
    else:
        raise ValueError("User does not exists")


def flush_tokens(token):
    return UserDBHandler.flush_tokens(token)
