from fastapi import HTTPException

from config.db_config import n_table_user
from ..db_ops import execute_query

class LmsHandler:

    def get_user_by_token(token):
        query = f"""SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

    @classmethod
    def add_user_to_db(cls, params):
        query = f"""   INSERT into {n_table_user}(eid, sid, full_name, dept, adhr, username, email, password, bio, file, role, timezone, langtype, users_allowed, auth_token, request_token, token, active, deactive, exclude_from_email) VALUES 
                        (%(eid)s, %(sid)s, %(full_name)s, %(dept)s, %(adhr)s, %(username)s, %(email)s,%(password)s, %(bio)s, %(file)s, %(role)s, %(timezone)s, %(langtype)s, %(users_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s, %(exclude_from_email)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
    @classmethod
    def change_password(cls, email, password,user):
        query = """ UPDATE users SET password = %(password)s WHERE email=%(email)s and id = %(user_id)s"""
        params = {"password": password, "email": email,"user_id":user['id']}
        return execute_query(query, params=params)
    
    @classmethod
    def get_all_users(cls):
        query = """ SELECT * FROM users; """
        return execute_query(query).fetchall()
    
    @classmethod
    def delete_users(cls, id):
        query = f""" DELETE FROM users WHERE id = '{id}'; """
        return execute_query(query)