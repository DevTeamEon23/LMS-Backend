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
    def add_users_to_db(cls, params):
        query = f"""   INSERT into {n_table_user}(full_name, username, email,password, role, users_allowed, auth_token, request_token, token, active) VALUES 
                        (%(full_name)s, %(username)s, %(email)s,%(password)s, %(role)s, %(users_allowed)s,  %(auth_token)s, %(request_token)s, %(token)s, %(active)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
    @classmethod
    def get_all_users(cls):
        query = """ SELECT * FROM users; """
        return execute_query(query).fetchall()