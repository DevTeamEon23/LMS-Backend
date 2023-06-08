from fastapi import Header
from starlette.exceptions import HTTPException

from config.db_config import n_table_user
from db_ops import execute_query


def get_user_by_token(token):
    query = f"""SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"""
    resp = execute_query(query=query, params={'token': token, 'active': True})
    data = resp.fetchone()
    if data is None:
        raise HTTPException(
            status_code=401, detail="Token Expired or Invalid Token")
    else:
        return data

def verify_admin_token(Auth_Token: str = Header()):
    user = get_user_by_token(Auth_Token)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Authorization Token is invalid")
    elif user['role'] != 'admin':
        raise HTTPException(status_code=401, detail="Access Denied")


def verify_app_user(Auth_Token: str = Header()):
    user = get_user_by_token(Auth_Token)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Authorization Token is invalid")
    elif user['role'] != "app":
        raise HTTPException(status_code=401, detail="Access Denied")


def verify_user(Auth_Token: str = Header()):
    user = get_user_by_token(Auth_Token)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Authorization Token is invalid")